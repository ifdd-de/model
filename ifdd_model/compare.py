"""Compare generated JSON-LD files with reference files by meaning, not by text.

Two checks, both with PyLD (a JSON-LD 1.1 processor):

* **Term definitions** (contexts only): every term of both contexts is
  processed into its IRI, ``@type`` coercion and ``@container``. Terms that
  are missing, extra or different are reported.
* **Graph**: both documents are canonicalised (RDF Dataset Canonicalization,
  URDNA2015) and the resulting N-Quads are compared. This covers the header
  node of a context and every node of a vocabulary.

Reference files may contain the cookiecutter placeholders of the templates;
they are replaced by the URLs given with ``--type-url`` and ``--unit-url``.

Usage: ``python -m ifdd_model.compare GENERATED REFERENCE [--type-url URL] [--unit-url URL]``
Exit code 0 when equal, 1 with a list of differences otherwise.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pyld import jsonld

PLACEHOLDERS = {
    "ifdd_type_url": ("{{ cookiecutter.ifdd_type_url }}", "{{cookiecutter.ifdd_type_url}}"),
    "ifdd_unit_url": ("{{ cookiecutter.ifdd_unit_url }}", "{{cookiecutter.ifdd_unit_url}}"),
}
OPTIONS = {"processingMode": "json-ld-1.1"}


def _no_remote(url, options=None):
    raise jsonld.JsonLdError(f"remote documents are not loaded: {url}", "loading document failed")


def render(text: str, type_url: str, unit_url: str) -> str:
    values = {"ifdd_type_url": type_url, "ifdd_unit_url": unit_url}
    for var, spellings in PLACEHOLDERS.items():
        for spelling in spellings:
            text = text.replace(spelling, values[var])
    return text


def load(path: Path, type_url: str, unit_url: str) -> dict:
    return json.loads(render(path.read_text(encoding="utf-8"), type_url, unit_url))


def term_definitions(context: dict) -> dict[str, tuple]:
    """Process a context and return term -> (IRI, @type, @container)."""
    processor = jsonld.JsonLdProcessor()
    options = {**OPTIONS, "documentLoader": _no_remote}
    # PyLD has no public call that returns the processed context;
    # _get_initial_context is used as in PyLD's own processing.
    active = processor.process_context(processor._get_initial_context(options), context, options)
    result = {}
    for term, definition in active["mappings"].items():
        if not definition:
            continue
        container = definition.get("@container") or []
        result[term] = (definition.get("@id"), definition.get("@type"), tuple(sorted(container)))
    # Context-wide keywords are not terms but change the meaning of every
    # undefined key (@vocab) or relative IRI (@base).
    for keyword in ("@vocab", "@base", "@language", "@direction"):
        if active.get(keyword) is not None:
            result[keyword] = (active[keyword],)
    return result


def nquads(doc: dict) -> set[str]:
    options = {**OPTIONS, "algorithm": "URDNA2015", "format": "application/n-quads", "documentLoader": _no_remote}
    return set(filter(None, jsonld.normalize(doc, options).splitlines()))


def compare(generated: dict, reference: dict) -> list[str]:
    diffs: list[str] = []
    if "@graph" not in reference:
        gen_terms = term_definitions(generated["@context"])
        ref_terms = term_definitions(reference["@context"])
        for term in sorted(set(gen_terms) | set(ref_terms)):
            g, r = gen_terms.get(term), ref_terms.get(term)
            if g is None:
                diffs.append(f"term {term}: missing (reference {r})")
            elif r is None:
                diffs.append(f"term {term}: extra (generated {g})")
            elif g != r:
                diffs.append(f"term {term}: generated {g} != reference {r}")
    gen_q, ref_q = nquads(generated), nquads(reference)
    diffs += [f"graph: missing {q}" for q in sorted(ref_q - gen_q)]
    diffs += [f"graph: extra {q}" for q in sorted(gen_q - ref_q)]
    return diffs


def main(argv: list[str]) -> int:
    args = list(argv)
    urls = {"--type-url": "https://type/v1", "--unit-url": "https://unit/v1"}
    for flag in list(urls):
        if flag in args:
            i = args.index(flag)
            urls[flag] = args[i + 1]
            del args[i:i + 2]
    if len(args) != 2:
        print(__doc__.strip().splitlines()[-2], file=sys.stderr)
        return 2
    type_url, unit_url = urls["--type-url"], urls["--unit-url"]
    diffs = compare(load(Path(args[0]), type_url, unit_url), load(Path(args[1]), type_url, unit_url))
    for d in diffs:
        print(d)
    return 1 if diffs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
