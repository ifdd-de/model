"""End-to-end tests: build with `just json` and compare with the references.

The references in tests/reference are copies of the example files of the
templates schema, type and unit (see tests/reference/README.md).
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from ifdd_model.compare import compare, load

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = ROOT / "tests" / "reference"
TYPE_URL, UNIT_URL = "https://type/v1", "https://unit/v1"


def references() -> list[tuple[str, str]]:
    """(service, path below json-ld/) for every reference file."""
    result = []
    for path in sorted(REFERENCE.rglob("*.jsonld")):
        rel = path.relative_to(REFERENCE)
        result.append((rel.parts[0], str(Path(*rel.parts[1:]))))
    return result


def build(src: Path, out: Path) -> None:
    subprocess.run(["just", f"src={src}", f"out={out}", "json"], cwd=ROOT, check=True,
                   capture_output=True, text=True)


def diffs(out: Path, service: str, rel: str) -> list[str]:
    generated = out / service / "json-ld" / rel
    assert generated.is_file(), f"not generated: {generated}"
    return compare(load(generated, TYPE_URL, UNIT_URL), load(REFERENCE / service / rel, TYPE_URL, UNIT_URL))


@pytest.fixture(scope="session")
def built(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("out")
    build(ROOT / "src" / "linkml", out)
    return out


@pytest.mark.parametrize(("service", "rel"), references())
def test_reference_is_reproduced(built, service, rel):
    assert diffs(built, service, rel) == []


def test_nothing_extra_is_generated(built):
    generated = {str(p.relative_to(built)) for p in built.rglob("*.jsonld") if p.parts[len(built.parts)] != "raw"}
    expected = {f"{service}/json-ld/{rel}" for service, rel in references()}
    assert generated == expected


def test_vocabulary_only_namespace_has_no_context(built):
    assert not (built / "schema/json-ld/v1/climate.ops.example.ifdd.de.jsonld").exists()
    assert (built / "type/json-ld/v1/climate.ops.example.ifdd.de/index.jsonld").is_file()


def test_raw_linkml_context_is_not_enough(built):
    """Counter-check for ifdd_model.context: without the post-processing the
    output of gen-jsonld-context differs from the reference (@vocab, class
    terms, @id coercion of embedded values)."""
    raw = load(built / "raw/breaker.grid.example.ifdd.de.jsonld", TYPE_URL, UNIT_URL)
    ref = load(REFERENCE / "schema/v1/breaker.grid.example.ifdd.de.jsonld", TYPE_URL, UNIT_URL)
    found = "\n".join(compare(raw, ref))
    assert "term @vocab: extra" in found
    assert "term Breaker: extra" in found
    assert "term ratedVoltage: generated" in found


CHANGES = [
    ("type/product.yaml", "      hasPart:\n        slot_uri: product:hasPart\n",
     "      hasPart:\n        slot_uri: product:hasPartX\n", "schema/v1/product.jsonld"),
    ("type/base.yaml", "        multivalued: true\n", "", "schema/v1/base.jsonld"),
    ("type/breaker.grid.example.ifdd.de.yaml", "title_de: Fabriknummer", "title_de: Seriennummer",
     "type/v1/breaker.grid.example.ifdd.de/index.jsonld"),
    ("type/maintenance.ops.example.ifdd.de.yaml", "rank: 120", "rank: 121",
     "type/v1/maintenance.ops.example.ifdd.de/index.jsonld"),
    ("type/climate.ops.example.ifdd.de.yaml", "minimum_value: -50", "minimum_value: -40",
     "type/v1/climate.ops.example.ifdd.de/index.jsonld"),
    ("unit/unit.yaml", "symbol: kV", "symbol: KV", "unit/v1/unit/index.jsonld"),
    ("unit/unit.yaml", "has_quantity_kind: quantitykind:Temperature", "has_quantity_kind: quantitykind:Voltage",
     "unit/v1/quantitykind/index.jsonld"),
]


@pytest.mark.parametrize(("source", "old", "new", "target"), CHANGES)
def test_changed_source_is_detected(tmp_path, source, old, new, target):
    """Counter-check for the whole chain: a changed LinkML source must lead to
    a difference in the generated file."""
    src = tmp_path / "src"
    shutil.copytree(ROOT / "src" / "linkml", src)
    path = src / source
    text = path.read_text(encoding="utf-8")
    assert old in text, f"test change does not apply to {source}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    out = tmp_path / "out"
    build(src, out)
    service, rel = target.split("/", 1)
    assert diffs(out, service, rel) != []
