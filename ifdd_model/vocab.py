"""Write the vocabulary (``index.jsonld``) of one namespace for type or unit.

The type and unit services answer every IRI below a namespace with this one
document (all nodes in ``@graph``). LinkML has no generator for this shape,
so it is written here from the LinkML source:

=============================  =============================================
Vocabulary                     LinkML source
=============================  =============================================
``owl:Ontology`` node          schema: ``id``, ``title``, ``description``
``rdfs:Class`` node            class in the own namespace: ``class_uri``,
                               ``title``
``rdf:Property`` nodes         attributes of that class (without a class:
                               top-level slots): ``slot_uri``, ``title``,
                               ``description``, ``rank`` -> ``sh:order``,
                               ``range`` -> ``rdfs:range``,
                               ``minimum_value``/``maximum_value`` ->
                               ``sh:minInclusive``/``sh:maxInclusive``
``qudt:Unit`` /                permissible values of an enum with
``qudt:QuantityKind`` nodes    ``enum_uri``: ``meaning``, ``title``,
                               ``description``, ``unit.symbol``,
                               ``unit.has_quantity_kind``, ``exact_mappings``
German texts                   annotations ``title_de``, ``description_de``
``qudt:hasQuantityKind``,      annotations ``quantity_kind`` and
``qudt:applicableUnit``        ``applicable_units`` (IRIs, space-separated)
=============================  =============================================

For quantity kinds, ``qudt:applicableUnit`` is derived from the units whose
``unit.has_quantity_kind`` points to them (pass the unit sources with
``--units``).

Usage: ``python -m ifdd_model.vocab SCHEMA.yaml OUT.jsonld [--units UNIT.yaml ...]``
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from ifdd_model.schema import IfddSchema

VOCAB_CONTEXT = {
    "@version": 1.1,
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "sh": "http://www.w3.org/ns/shacl#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "qudt": "http://qudt.org/schema/qudt/",
    "label": {"@id": "rdfs:label", "@container": "@language"},
    "comment": {"@id": "rdfs:comment", "@container": "@language"},
    "range": {"@id": "rdfs:range", "@type": "@id"},
    "definedBy": {"@id": "rdfs:isDefinedBy", "@type": "@id"},
    "order": {"@id": "sh:order", "@type": "xsd:integer"},
    "quantityKind": {"@id": "qudt:hasQuantityKind", "@type": "@id"},
    "applicableUnit": {"@id": "qudt:applicableUnit", "@type": "@id", "@container": "@set"},
    "symbol": "qudt:symbol",
    "exactMatch": {"@id": "skos:exactMatch", "@type": "@id"},
}
VOCAB_PREFIXES = {k: v for k, v in VOCAB_CONTEXT.items() if isinstance(v, str) and v.endswith(("/", "#"))}
NO_RANGE = {"string", "uriorcurie"}


def compact(iri: str) -> str:
    """Write IRIs of the vocabulary context's prefixes as CURIEs."""
    for prefix, ns in VOCAB_PREFIXES.items():
        if iri.startswith(ns):
            return f"{prefix}:{iri[len(ns):]}"
    return iri


def texts(schema: IfddSchema, element, with_comment: bool = True) -> dict:
    out = {}
    label = {"en": element.title, "de": schema.annotation(element, "title_de")}
    label = {k: v for k, v in label.items() if v}
    if label:
        out["label"] = label
    if with_comment:
        comment = {"en": element.description, "de": schema.annotation(element, "description_de")}
        comment = {k: v for k, v in comment.items() if v}
        if comment:
            out["comment"] = comment
    return out


def value(v):
    """Numbers from LinkML come as int/float subclasses; write plain JSON numbers."""
    if isinstance(v, bool):
        return v
    if isinstance(v, int):
        return int(v)
    if isinstance(v, float):
        return float(v)
    return v


def range_iri(schema: IfddSchema, slot) -> str | None:
    rng = slot.range
    if rng in NO_RANGE or rng is None:
        return None
    view = schema.view
    if rng in view.all_classes():
        return compact(schema.expand(view.get_class(rng).class_uri))
    if rng in view.all_types():
        return compact(schema.expand(view.get_type(rng).uri))
    raise ValueError(f"{schema.path}: range {rng} of {slot.name} is neither class nor type")


def property_nodes(schema: IfddSchema) -> list[dict]:
    nodes = []
    for slot in schema.terms():
        node = {"@id": schema.expand(slot.slot_uri), "@type": "rdf:Property"}
        node.update(texts(schema, slot))
        node["definedBy"] = schema.namespace
        node["order"] = int(slot.rank)
        rng = range_iri(schema, slot)
        if rng:
            node["range"] = rng
        qk = schema.annotation(slot, "quantity_kind")
        if qk:
            node["quantityKind"] = schema.expand(qk)
        units = schema.annotation(slot, "applicable_units")
        if units:
            node["applicableUnit"] = [schema.expand(u) for u in units.split()]
        if slot.minimum_value is not None:
            node["sh:minInclusive"] = value(slot.minimum_value)
        if slot.maximum_value is not None:
            node["sh:maxInclusive"] = value(slot.maximum_value)
        nodes.append(node)
    return nodes


def units_by_kind(unit_schemas: list[IfddSchema]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for us in unit_schemas:
        for enum in us.view.all_enums(imports=False).values():
            for pv in enum.permissible_values.values():
                if pv.unit and pv.unit.has_quantity_kind:
                    kind = us.expand(pv.unit.has_quantity_kind)
                    result.setdefault(kind, []).append(us.expand(pv.meaning))
    return result


def enum_nodes(schema: IfddSchema, unit_schemas: list[IfddSchema]) -> list[dict]:
    by_kind = units_by_kind(unit_schemas)
    nodes = []
    for enum in schema.view.all_enums(imports=False).values():
        if not enum.enum_uri:
            raise ValueError(f"{schema.path}: enum {enum.name} needs enum_uri (the type of its nodes)")
        for pv in enum.permissible_values.values():
            iri = schema.expand(pv.meaning)
            node = {"@id": iri, "@type": compact(schema.expand(enum.enum_uri))}
            node.update(texts(schema, pv))
            if pv.unit and pv.unit.symbol:
                node["symbol"] = pv.unit.symbol
            if pv.unit and pv.unit.has_quantity_kind:
                node["quantityKind"] = schema.expand(pv.unit.has_quantity_kind)
            if iri in by_kind:
                node["applicableUnit"] = by_kind[iri]
            matches = [schema.expand(m) for m in pv.exact_mappings or []]
            if matches:
                node["exactMatch"] = matches[0] if len(matches) == 1 else matches
            node["definedBy"] = schema.namespace
            nodes.append(node)
    return nodes


def build(schema: IfddSchema, unit_schemas: list[IfddSchema] | None = None) -> dict:
    s = schema.view.schema
    graph = [{"@id": schema.namespace, "@type": "owl:Ontology", **texts(schema, s)}]
    main = schema.main_class
    if main is not None:
        graph.append({"@id": schema.expand(main.class_uri), "@type": "rdfs:Class",
                      **texts(schema, main, with_comment=False), "definedBy": schema.namespace})
    if schema.view.all_enums(imports=False):
        graph.extend(enum_nodes(schema, unit_schemas or []))
    else:
        graph.extend(property_nodes(schema))
    return {"@context": VOCAB_CONTEXT, "@graph": graph}


def main(argv: list[str]) -> int:
    units: list[IfddSchema] = []
    args = list(argv)
    if "--units" in args:
        i = args.index("--units")
        units = [IfddSchema.load(p) for p in args[i + 1:]]
        args = args[:i]
    if len(args) != 2:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    schema = IfddSchema.load(args[0])
    out = Path(args[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = build(schema, units)
    out.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
