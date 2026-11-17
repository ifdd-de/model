(ifdd-model-reference)=
# Reference

The variables of the template are listed in the README of `ifdd-de/model`.
This page lists what is not a template variable.

## Layout

| Path | Purpose |
|---|---|
| `src/linkml/type/*.yaml` | one source per namespace of the type service (instance-owned) |
| `src/linkml/unit/*.yaml` | units and quantity kinds (instance-owned) |
| `tests/reference/` | expected output with the base URLs (instance-owned) |
| `ifdd_model/` | post-processing of the context, vocabulary writer, URL replacement, comparison |
| `docgen/` | page template for `gen-doc`, Sphinx configuration and index pages of the generated documentation |
| `justfile` | the build |
| `dotenv.dist` → `.env` | URLs and content directories |
| `docs/en`, `docs/de` | this documentation |

## Settings in `.env`

| Variable | Meaning |
|---|---|
| `IFDD_MODEL_SCHEMA_URL` | URL of the schema service; its path is the directory below `json-ld/` of the contexts |
| `IFDD_MODEL_TYPE_URL` | URL of the type service; replaces `https://type/v1` in all generated files |
| `IFDD_MODEL_UNIT_URL` | URL of the unit service; replaces `https://unit/v1` |
| `IFDD_MODEL_SCHEMA_TARGET`, `IFDD_MODEL_TYPE_TARGET`, `IFDD_MODEL_UNIT_TARGET` | content directories for `just publish` |

Unset or empty URLs mean the base URLs.

## Output

| Path | Content |
|---|---|
| `output/raw/<name>.jsonld` | context as `gen-jsonld-context` writes it |
| `output/base/...` | everything with the base URLs, compared with `tests/reference` |
| `output/schema/json-ld/<version>/<name>.jsonld` | JSON-LD contexts |
| `output/type/json-ld/<version>/<name>/index.jsonld` | vocabularies |
| `output/unit/json-ld/<version>/<name>/index.jsonld` | units, quantity kinds |
| `output/docs/en`, `output/docs/de` | MyST pages; HTML in `output/docs/_build` |

The generated pages use labels starting with `ifdd-model-ns-`; this
documentation uses `ifdd-model-`.

## Versions

Python packages: `requirements.txt`. PlantUML: `plantuml_version` and
`plantuml_sha256` in the `justfile`.
