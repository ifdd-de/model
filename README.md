# IFDD model (prototype)

LinkML sources for the namespaces of the IFDD services **schema**, **type**
and **unit**. One YAML file per namespace is the single point of truth; from
it the build generates

- the **JSON-LD context** for the schema service (`gen-jsonld-context` plus a
  short post-processing step),
- the **vocabulary** for the type service (labels and comments in English and
  German, order, ranges, quantity kinds, units, bounds),
- the **units and quantity kinds** for the unit service,
- **Sphinx documentation** in English and German with PlantUML diagrams.

The sources reproduce the example files of the templates `ifdd-de/schema`,
`ifdd-de/type` and `ifdd-de/unit`; `just compare` checks this by meaning.

This is a prototype to try things out. Paths, names and the place of the
sources (own repository or part of a content repository) may change.

## Layout

| Path | Content |
|---|---|
| `src/linkml/type/*.yaml` | one schema per namespace of the type service; with a class in its own namespace it also gets a context |
| `src/linkml/unit/*.yaml` | units and quantity kinds as enums |
| `ifdd_model/` | post-processing of the context, vocabulary writer, comparison |
| `docs/` | Sphinx configuration, page template for `gen-doc`, hand-written pages |
| `tests/` | tests, reference files, documentation check |
| `output/` | generated files (not in Git) |

Output layout, matching the content directories of the services:

```text
output/schema/json-ld/v1/<name>.jsonld
output/type/json-ld/v1/<name>/index.jsonld
output/unit/json-ld/v1/<name>/index.jsonld
output/raw/<name>.jsonld            context as gen-jsonld-context writes it
output/docs/{en,de}/                MyST pages
output/docs/_build/{en,de}/         HTML
```

## Requirements

- Python 3.13 or newer
- Java (to run PlantUML) and Graphviz (`dot`, for the diagram layout)
- `curl` (`just plantuml` downloads the pinned PlantUML jar into `.cache/`
  and checks its SHA-256)

```shell
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```shell
just              # list the recipes
just build        # clean, lint, JSON-LD, compare, docs, docs check
just json         # only the JSON-LD files
just compare      # compare output/ with tests/reference by meaning
just test         # pytest
```

Every recipe prints the plain commands it runs. The main steps by hand:

```shell
# context
gen-jsonld-context --no-metadata --fix-multivalue-containers --xsd-anyuri-as-iri \
    src/linkml/type/product.yaml > output/raw/product.jsonld
python -m ifdd_model.context src/linkml/type/product.yaml output/raw/product.jsonld \
    output/schema/json-ld/v1/product.jsonld

# vocabulary, units
python -m ifdd_model.vocab src/linkml/type/product.yaml output/type/json-ld/v1/product/index.jsonld
python -m ifdd_model.vocab src/linkml/unit/quantitykind.yaml \
    output/unit/json-ld/v1/quantitykind/index.jsonld --units src/linkml/unit/*.yaml

# compare one file
python -m ifdd_model.compare output/schema/json-ld/v1/product.jsonld tests/reference/schema/v1/product.jsonld

# documentation page of one namespace
gen-doc --dialect myst --template-directory docs/templates/en \
    --diagram-type plantuml_class_diagram --index-name ifdd_page -d /tmp/doc src/linkml/type/product.yaml
```

To try a change: edit a YAML file, run `just json compare`, and look at the
reported differences. `output/raw/` shows what LinkML generates before the
post-processing.

## How LinkML maps to JSON-LD

The page "From LinkML to JSON-LD" of the documentation (`docs/src/en/mapping.md`)
describes the mapping. In short:

- schema `id` = namespace, schema `name` = context name;
- the class with `class_uri: <prefix>:schema` is the header node of the
  context and the `rdfs:Class` of the vocabulary; its attributes are the
  terms;
- other classes only carry the URI of a reference target in another
  namespace;
- German texts are the annotations `title_de` and `description_de`;
  `rank` is the order; quantity kind and units are annotations
  `quantity_kind` and `applicable_units`.

`gen-jsonld-context` (LinkML 1.12.1) always writes `@vocab`, writes terms
for classes and coerces embedded values to `@id`. `ifdd_model.context`
removes these, because with `@vocab` undefined terms become valid and
`ifdd-ct check` could not report them.

## Kept as in the examples

The sources reproduce the examples of the templates, including points that
may deserve a later decision:

- `publisher` is a list only in `base`;
- `implementedBy` is a list in `function`, a single reference in `product`;
- some references have no target class in the vocabulary and are plain IRIs
  (`product`: `implementedBy`, `usedBy`; `function`: `consumer`, `usedBy`);
- `properties` is a list of text, its members `prop_id`, `prop_val`,
  `prop_validity` are separate terms;
- the prefix `schema:` (schema.org) is declared in `base` and the aspect
  contexts but not used;
- the URLs are the values of the shared configuration (`https://type/v1`,
  `https://unit/v1`), not template placeholders.

## AI assistance

Parts of this repository, in particular tests, test data and documentation,
were developed or improved with the help of large language models. The
maintainer has reviewed and approved them.

## License

BSD-3-Clause, see `LICENSE`. PlantUML is downloaded at build time and not
part of this repository.
