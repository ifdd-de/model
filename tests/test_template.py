"""Tests of the template: render the fixtures and check the instances.

Needs `cookiecutter` and the tools of the instance (`just`, LinkML, PyLD, ...:
`pip install cookiecutter -r "{{cookiecutter.ifdd_model_prj_slug}}/requirements.txt"`).
The instance runs its own tests itself (`pytest tests` inside the instance);
these tests cover what only the template knows: the fixtures, the hooks and
counter-checks bound to the example sources.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

TEMPLATE = Path(__file__).resolve().parent.parent
FIXTURES = TEMPLATE / "tests" / "fixtures"
FIXTURE_OF: dict[Path, str] = {}  # rendered instance -> fixture name


def render(fixture: str, out: Path, *extra: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["cookiecutter", "--no-input", "--config-file", str(FIXTURES / f"{fixture}.yaml"),
         "--output-dir", str(out), str(TEMPLATE), *extra],
        check=check, capture_output=True, text=True)


def clean_env() -> dict[str, str]:
    """The environment without IFDD_MODEL_*, so that .env of the instance applies."""
    return {k: v for k, v in os.environ.items() if not k.startswith("IFDD_MODEL_")}


def just(instance: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["just", *args], cwd=instance, env=clean_env(), check=True, capture_output=True, text=True)


@pytest.fixture(scope="session", params=["defaults", "custom"])
def instance(request, tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp(request.param)
    render(request.param, out)
    (path,) = list(out.iterdir())
    FIXTURE_OF[path] = request.param
    return path


@pytest.fixture(scope="session")
def defaults(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("defaults-examples")
    render("defaults", out)
    (path,) = list(out.iterdir())
    FIXTURE_OF[path] = "defaults"
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
    return path


def fixture_value(instance: Path, name: str) -> str:
    context = yaml.safe_load((FIXTURES / f"{FIXTURE_OF[instance]}.yaml").read_text())
    defaults = yaml.safe_load((TEMPLATE / "cookiecutter.json").read_text())
    return (context.get("default_context") or {}).get(name, defaults[name])


def test_no_template_placeholders(instance):
    files = [p for p in instance.rglob("*") if p.is_file() and not {"__pycache__", ".pytest_cache"} & set(p.parts)]
    leftovers = [p for p in files if "cookiecutter." in p.read_text(errors="ignore")]
    assert leftovers == []


def test_env_is_created_from_the_fixture(instance):
    env = instance / ".env"
    assert env.stat().st_mode & 0o777 == 0o600
    text = env.read_text()
    for service in ("schema", "type", "unit"):
        assert f"IFDD_MODEL_{service.upper()}_URL={fixture_value(instance, f'ifdd_{service}_url')}\n" in text


def test_json_follows_the_urls_of_the_fixture(instance, tmp_path):
    just(instance, f"out={tmp_path}", "json")
    for service in ("schema", "type", "unit"):
        url = fixture_value(instance, f"ifdd_{service}_url")
        path = url.split("://", 1)[1].split("/", 1)[1]
        target = tmp_path / service / "json-ld" / path
        assert target.is_dir(), target
        text = "".join(p.read_text() for p in target.rglob("*.jsonld"))
        if service != "schema":
            assert url + "/" in text


@pytest.mark.parametrize("value", [
    "ifdd_type_url=https://type/v1/",
    "ifdd_unit_url=https://unit",
    "ifdd_schema_url=schema/v1",
    "ifdd_type_url=https://type/v1?x=1",
    "ifdd_type_url=https://type/v'1",
    "ifdd_model_prj_slug=with space",
])
def test_hook_rejects_values(tmp_path, value):
    result = render("defaults", tmp_path, value, check=False)
    assert result.returncode != 0
    assert not any(tmp_path.iterdir())


# Counter-checks bound to the example sources: a changed LinkML source must
# lead to a difference in the generated file.
CHANGES = [
    ("type/product.yaml", "      hasPart:\n        slot_uri: product:hasPart\n",
     "      hasPart:\n        slot_uri: product:hasPartX\n", "schema/product.jsonld"),
    ("type/base.yaml", "        multivalued: true\n", "", "schema/base.jsonld"),
    ("type/breaker.grid.example.ifdd.de.yaml", "title_de: Fabriknummer", "title_de: Seriennummer",
     "type/breaker.grid.example.ifdd.de/index.jsonld"),
    ("type/maintenance.ops.example.ifdd.de.yaml", "rank: 120", "rank: 121",
     "type/maintenance.ops.example.ifdd.de/index.jsonld"),
    ("type/climate.ops.example.ifdd.de.yaml", "minimum_value: -50", "minimum_value: -40",
     "type/climate.ops.example.ifdd.de/index.jsonld"),
    ("unit/unit.yaml", "symbol: kV", "symbol: KV", "unit/unit/index.jsonld"),
    ("unit/unit.yaml", "has_quantity_kind: quantitykind:Temperature", "has_quantity_kind: quantitykind:Voltage",
     "unit/quantitykind/index.jsonld"),
]


@pytest.mark.parametrize(("source", "old", "new", "target"), CHANGES)
def test_changed_source_is_detected(defaults, tmp_path, source, old, new, target):
    from ifdd_model.compare import compare, load

    src = tmp_path / "src"
    shutil.copytree(defaults / "src" / "linkml", src)
    path = src / source
    text = path.read_text(encoding="utf-8")
    assert old in text, f"test change does not apply to {source}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    out = tmp_path / "out"
    just(defaults, f"src={src}", f"out={out}", "base")
    assert compare(load(out / "base" / target), load(defaults / "tests" / "reference" / target)) != []


def test_unchanged_examples_match(defaults, tmp_path):
    """Counterpart of the counter-checks: the unchanged examples match."""
    just(defaults, f"out={tmp_path}", "base", "compare")


@pytest.fixture(scope="session")
def example_pages(defaults, tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("pages")
    just(defaults, f"out={out}", "docs-pages")
    return out / "docs"


def test_reference_to_other_namespace_is_a_link(example_pages):
    text = (example_pages / "en" / "type" / "product.md").read_text(encoding="utf-8")
    assert "| `containedIn` | Located in | Location the product is in. | {ref}`ifdd-model-ns-location` |" in text


def test_units_listed_by_name(example_pages):
    text = (example_pages / "de" / "type" / "breaker.grid.example.ifdd.de.md").read_text(encoding="utf-8")
    assert "Einheiten KiloV, V" in text


def test_example_pages_use_the_urls_of_env(example_pages, defaults):
    text = (example_pages / "en" / "type" / "product.md").read_text(encoding="utf-8")
    assert f"`{fixture_value(defaults, 'ifdd_type_url')}/product/`" in text
