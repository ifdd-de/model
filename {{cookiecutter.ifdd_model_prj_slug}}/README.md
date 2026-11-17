# {{ cookiecutter.ifdd_model_prj_name }}

The model of an IFDD installation: LinkML sources in `src/linkml`, one file
per namespace. The build generates the JSON-LD contexts of the schema
service, the vocabularies of the type service, the units of the unit service
and a documentation of every namespace.

Generated from the template `ifdd-de/model`.

## Quick start

```shell
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
just build      # lint, JSON-LD, compare with tests/reference, docs
just publish    # copy into the content repositories set in .env
```

Java and Graphviz are needed for the diagrams of the documentation. `just`
lists all recipes; every recipe prints the commands it runs.

## Documentation

The operating documentation is in `docs/en` and `docs/de`: setup, build and
release, operations, security, troubleshooting, reference, and how LinkML
becomes JSON-LD. `just docs` generates the documentation of the namespaces
into `output/docs`.

## Kept as in the examples

The example sources reproduce the example files of the templates
`ifdd-de/schema`, `ifdd-de/type` and `ifdd-de/unit`, including points that
may deserve a later decision:

- `publisher` is a list only in `base`;
- `implementedBy` is a list in `function`, a single reference in `product`;
- some references have no target class and are plain IRIs (`product`:
  `implementedBy`, `usedBy`; `function`: `consumer`, `usedBy`);
- `properties` is a list of text, its members `prop_id`, `prop_val`,
  `prop_validity` are separate terms;
- the prefix `schema:` (schema.org) is declared in `base` and the aspect
  contexts but not used.

## AI assistance

Parts of this repository, in particular tests, test data and documentation,
were developed or improved with the help of large language models. The
maintainer has reviewed and approved them.

## License

BSD-3-Clause, see `LICENSE`.
