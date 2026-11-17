(ifdd-model-mapping)=
# From LinkML to JSON-LD

## One source per namespace

Every namespace has exactly one LinkML file. It stands alone: terms that
every context needs (`objType`, `objName`, `origin`, `publisher`, the `c_*`
terms …) are written out in each file, because each context defines them in
its own namespace. The backend finds the namespace of a context by expanding
its `c_*` terms. A shared imported module would put these terms into one
namespace for all contexts.

| LinkML | schema service | type or unit service |
|---|---|---|
| schema `id` | prefix of the own namespace | `owl:Ontology` node |
| schema `name` | file name `<name>.jsonld` (context name) | directory `<name>/` |
| class with `class_uri: <prefix>:schema` | header node `rdfs:Class` | `rdfs:Class` node |
| attributes of that class | terms with `@type`/`@container` | `rdf:Property` nodes |
| other classes (only `class_uri`) | target of `@type: @id` | `rdfs:range` |
| enum with `enum_uri` (units) | – | one node per permissible value |

A schema without a class in its own namespace (for example the climate
vocabulary for time series) gets a vocabulary but no context.

## JSON-LD context

The context comes from `gen-jsonld-context` with the options
`--no-metadata --fix-multivalue-containers --xsd-anyuri-as-iri`. A short
post-processing step (`ifdd_model.context`) then:

- removes `@vocab`, so that undefined terms stay undefined and `ifdd-ct check`
  can report them, and writes every term as `prefix:term`;
- removes the terms LinkML writes for classes;
- removes `@type: @id` from embedded values (`inlined: true`, e.g.
  `QuantityValue`);
- removes the `linkml:` prefix;
- adds `@version: 1.1`, the alias `type`, the term `schemaVersion` and the
  header node with the class description and the schema version.

Ranges: `datetime`, `date` and the own types `gyear`, `duration` give
`@type` with the XSD datatype; a class range or `uriorcurie` gives
`@type: @id`; `multivalued: true` gives `@container: @set`.

## Vocabulary

The vocabulary is written by `ifdd_model.vocab`:

| Vocabulary | LinkML |
|---|---|
| `rdfs:label` (en, de) | `title`, annotation `title_de` |
| `rdfs:comment` (en, de) | `description`, annotation `description_de` |
| `sh:order` | `rank` |
| `rdfs:range` | `range` (not for text and `uriorcurie`) |
| `qudt:hasQuantityKind` | annotation `quantity_kind` |
| `qudt:applicableUnit` | annotation `applicable_units` (IRIs, separated by spaces) |
| `sh:minInclusive`, `sh:maxInclusive` | `minimum_value`, `maximum_value` |
| `qudt:symbol` (units) | `unit.symbol` |
| `qudt:hasQuantityKind` (units) | `unit.has_quantity_kind` |
| `skos:exactMatch` (units) | `exact_mappings` |

For quantity kinds, `qudt:applicableUnit` is derived from the units that
point to them.
