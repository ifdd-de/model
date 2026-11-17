"""Content checks of the generated MyST pages (`just docs-pages`).

tests/check_docs.py checks structure and the Sphinx build. These tests check
that each page shows what its LinkML source says, in the right language.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from ifdd_model.schema import IfddSchema

ROOT = Path(__file__).resolve().parent.parent
SOURCES = sorted((ROOT / "src" / "linkml").glob("*/*.yaml"))
LEAKS = re.compile(r"<built-in|<bound method|\bNone\b|\{\{|\{%|Undefined")


@pytest.fixture(scope="session")
def pages(tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("docs")
    subprocess.run(["just", f"out={out}", "docs-pages"], cwd=ROOT, check=True, capture_output=True, text=True)
    return out / "docs"


def page(pages: Path, lang: str, source: Path) -> str:
    return (pages / lang / source.parent.name / f"{source.stem}.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("source", SOURCES, ids=lambda p: p.stem)
@pytest.mark.parametrize("lang", ["en", "de"])
def test_page_content(pages, lang, source):
    schema = IfddSchema.load(source)
    text = page(pages, lang, source)
    assert not LEAKS.findall(text), LEAKS.findall(text)
    assert text.startswith(f"(ifdd-model-{schema.name.replace('.', '-')})=\n# ")
    title = schema.annotation(schema.view.schema, "title_de") if lang == "de" else schema.view.schema.title
    assert text.splitlines()[1] == f"# {title}"
    assert ("```{uml}" in text) == (schema.main_class is not None)
    if schema.view.all_enums(imports=False):
        for enum in schema.view.all_enums(imports=False).values():
            for key, pv in enum.permissible_values.items():
                label = schema.annotation(pv, "title_de") if lang == "de" else pv.title
                assert f"| `{key}` | {label} |" in text
                if pv.unit and pv.unit.has_quantity_kind:
                    assert f"| {pv.unit.has_quantity_kind.split(':')[-1]} |" in text
    else:
        for slot in schema.terms():
            label = schema.annotation(slot, "title_de") if lang == "de" else slot.title
            assert f"| `{slot.name}` | {label} |" in text


def test_reference_to_other_namespace_is_a_link(pages):
    text = page(pages, "en", ROOT / "src/linkml/type/product.yaml")
    assert "| `containedIn` | Located in | Location the product is in. | {ref}`ifdd-model-location` |" in text


def test_units_listed_by_name(pages):
    text = page(pages, "de", ROOT / "src/linkml/type/breaker.grid.example.ifdd.de.yaml")
    assert "Einheiten KiloV, V" in text
