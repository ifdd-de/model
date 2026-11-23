"""Build with `just json` and compare with the references in tests/reference.

The references are the expected output with the base URLs. After a wanted
change of a LinkML source, `just json accept` updates them.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from conftest import ROOT, just
from ifdd_model.compare import compare, load
from ifdd_model.relocate import BASE_URLS
from ifdd_model.schema import IfddSchema

REFERENCE = ROOT / "tests" / "reference"
SOURCES = ROOT / "src" / "linkml"


def references() -> list[str]:
    return [str(p.relative_to(REFERENCE)) for p in sorted(REFERENCE.rglob("*.jsonld"))]


def generated(out: Path) -> list[str]:
    base = out / "base"
    return [str(p.relative_to(base)) for p in sorted(base.rglob("*.jsonld"))]


def test_there_are_references():
    assert references(), "tests/reference is empty; run `just json accept` after checking the output"


@pytest.mark.parametrize("rel", references())
def test_reference_is_reproduced(built, rel):
    assert compare(load(built / "base" / rel), load(REFERENCE / rel)) == []


def test_every_output_has_a_reference(built):
    assert generated(built) == references()


@pytest.mark.parametrize("source", sorted(SOURCES.glob("type/*.yaml")), ids=lambda p: p.stem)
def test_context_only_with_a_class(built, source):
    has_class = IfddSchema.load(source).main_class is not None
    assert (built / "base" / "schema" / f"{source.stem}.jsonld").is_file() == has_class
    assert (built / "base" / "type" / source.stem / "index.jsonld").is_file()


def test_raw_linkml_context_is_not_enough(built):
    """Counter-check for ifdd_model.context: without the post-processing the
    output of gen-jsonld-context differs from the reference (@vocab)."""
    raws = sorted((built / "raw").glob("*.jsonld"))
    assert raws
    for raw in raws:
        found = compare(load(raw), load(REFERENCE / "schema" / raw.name))
        assert any(d.startswith("term @vocab: extra") for d in found), raw.name


TARGET_URLS = {
    "IFDD_MODEL_SCHEMA_URL": "https://schema.test.invalid/v7",
    "IFDD_MODEL_TYPE_URL": "https://type.test.invalid/v8",
    "IFDD_MODEL_UNIT_URL": "https://unit.test.invalid/sub/v9",
}


@pytest.fixture(scope="module")
def relocated(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("relocated")
    just(f"out={out}", "json", env=TARGET_URLS)
    return out


def test_relocated_paths_follow_the_urls(relocated):
    assert sorted(p.name for p in (relocated / "schema" / "json-ld").iterdir()) == ["v7"]
    assert sorted(p.name for p in (relocated / "type" / "json-ld").iterdir()) == ["v8"]
    assert (relocated / "unit" / "json-ld" / "sub" / "v9").is_dir()


def test_relocated_files_carry_no_base_url(relocated):
    for service in BASE_URLS:
        for path in (relocated / service).rglob("*.jsonld"):
            text = path.read_text(encoding="utf-8")
            assert not any(base + "/" in text for base in BASE_URLS.values()), path


@pytest.mark.parametrize("rel", references())
def test_relocated_file_means_the_relocated_reference(relocated, rel, tmp_path):
    service, rest = rel.split("/", 1)
    path = {"schema": "v7", "type": "v8", "unit": "sub/v9"}[service]
    # Move the reference with a plain replacement of its own, independent of
    # ifdd_model.relocate.
    text = (REFERENCE / rel).read_text(encoding="utf-8")
    for s, base in {"schema": "https://schema/v1", "type": "https://type/v1", "unit": "https://unit/v1"}.items():
        text = text.replace(base + "/", TARGET_URLS[f"IFDD_MODEL_{s.upper()}_URL"] + "/")
    reference = tmp_path / "reference.jsonld"
    reference.write_text(text, encoding="utf-8")
    generated_file = relocated / service / "json-ld" / path / rest
    assert compare(load(generated_file), load(reference)) == []


@pytest.mark.parametrize("url", ["https://type/v1/", "type/v1", "https://type", "https://type/v1?x=1"])
def test_invalid_url_is_rejected(tmp_path, url):
    result = just(f"out={tmp_path}", "json", env={"IFDD_MODEL_TYPE_URL": url}, check=False)
    assert result.returncode != 0
    assert "IFDD_MODEL" in result.stderr or "type:" in result.stderr


def test_publish_copies_and_never_deletes(tmp_path):
    targets = {s: tmp_path / f"{s}-content" for s in BASE_URLS}
    for path in targets.values():
        path.mkdir()
    keep = targets["type"] / "v1" / "handwritten" / "index.jsonld"
    keep.parent.mkdir(parents=True)
    keep.write_text("{}", encoding="utf-8")
    env = {f"IFDD_MODEL_{s.upper()}_TARGET": str(p) for s, p in targets.items()}
    result = just(f"out={tmp_path / 'out'}", "publish", env=env)
    for rel in references():
        service, rest = rel.split("/", 1)
        assert (targets[service] / "v1" / rest).is_file(), rel
    assert keep.read_text(encoding="utf-8") == "{}"
    assert "./v1/handwritten/index.jsonld" in result.stdout


def test_publish_needs_all_targets(tmp_path):
    (tmp_path / "schema").mkdir()
    result = just(f"out={tmp_path / 'out'}", "publish", env={"IFDD_MODEL_SCHEMA_TARGET": str(tmp_path / "schema")},
                  check=False)
    assert result.returncode != 0
    assert "IFDD_MODEL_TYPE_TARGET is not set" in result.stderr
    assert not any((tmp_path / "schema").iterdir())


def test_build_reads_the_content_directory(tmp_path):
    """IFDD_MODEL_CONTENT_DIR, the directory the web service serves, is also
    the source of the build; empty means src/linkml."""
    content = tmp_path / "content"
    shutil.copytree(SOURCES, content)
    source = content / "type" / "climate.ops.example.ifdd.de.yaml"
    text = source.read_text(encoding="utf-8")
    assert "minimum_value: -50" in text
    source.write_text(text.replace("minimum_value: -50", "minimum_value: -40", 1), encoding="utf-8")
    rel = "type/climate.ops.example.ifdd.de/index.jsonld"
    out = tmp_path / "from-content"
    just(f"out={out}", "base", env={"IFDD_MODEL_CONTENT_DIR": str(content)})
    assert compare(load(out / "base" / rel), load(REFERENCE / rel)) != []
    out = tmp_path / "from-src"
    just(f"out={out}", "base", env={"IFDD_MODEL_CONTENT_DIR": ""})
    assert compare(load(out / "base" / rel), load(REFERENCE / rel)) == []
