"""Turn the output of ``gen-jsonld-context`` into an IFDD JSON-LD context.

``gen-jsonld-context`` (LinkML 1.12.1) produces a valid context, but it differs
from what IFDD needs in five points. This step fixes exactly these:

1. It always sets ``@vocab`` to the schema namespace. With ``@vocab`` every
   unknown term expands into the namespace, so ``ifdd-ct check`` cannot report
   undefined terms and a typo becomes a valid term. ``@vocab`` is removed and
   every term gets an explicit ``prefix:term`` IRI instead.
2. It writes a term for every class (``Breaker``, ``Location``, ...). IFDD
   contexts have no class terms; they are removed.
3. It coerces every slot with a class range to ``@type: @id``, also when the
   value is an embedded object (``inlined: true``, e.g. ``QuantityValue``).
   For embedded objects the coercion is dropped.
4. It emits the ``linkml:`` prefix, which IFDD data never uses; removed.
5. It writes only the ``@context``. IFDD context documents also carry
   ``@version: 1.1``, the alias ``type`` for ``@type``, the term
   ``schemaVersion`` and a header node (``rdfs:Class``) with label, comment
   and version. These are added from the LinkML source.

Usage: ``python -m ifdd_model.context SCHEMA.yaml RAW_CONTEXT.jsonld OUT.jsonld``
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from ifdd_model.schema import IfddSchema

DROPPED_PREFIXES = {"linkml"}


def build(schema: IfddSchema, raw: dict) -> dict:
    main = schema.main_class
    if main is None:
        raise ValueError(f"{schema.path}: no class in the own namespace, so no context")
    raw_ctx = raw["@context"]
    alias = schema.alias
    prefixes = {p: raw_ctx[p] for p in schema.view.schema.prefixes if p not in DROPPED_PREFIXES}
    if "rdfs" not in prefixes:
        raise ValueError(f"{schema.path}: prefix rdfs is needed for the header node")

    ctx: dict = {"@version": 1.1}
    ctx[alias] = prefixes.pop(alias)
    ctx.update(prefixes)
    ctx["type"] = "@type"
    ctx["schemaVersion"] = f"{alias}:schemaVersion"

    classes = set(schema.view.all_classes(imports=False))
    for slot in schema.terms():
        if slot.name not in raw_ctx:
            raise ValueError(f"{schema.path}: term {slot.name} missing in the generated context")
        definition = dict(raw_ctx[slot.name])
        iri = definition["@id"]
        if ":" not in iri:
            definition["@id"] = f"{alias}:{iri}"
        if slot.range in classes and slot.inlined:
            definition.pop("@type", None)
        ordered = {"@id": definition.pop("@id")}
        ordered.update(definition)
        ctx[slot.name] = ordered["@id"] if len(ordered) == 1 else ordered

    if not schema.view.schema.version:
        raise ValueError(f"{schema.path}: version is needed for schemaVersion")
    return {
        "@context": ctx,
        "@id": schema.expand(main.class_uri),
        "@type": "rdfs:Class",
        "rdfs:label": schema.name,
        "rdfs:comment": main.description,
        "schemaVersion": schema.view.schema.version,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    schema = IfddSchema.load(argv[0])
    raw = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    out = Path(argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(build(schema, raw), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
