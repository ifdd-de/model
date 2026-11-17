(ifdd-model-index)=
# {{ cookiecutter.ifdd_model_prj_name }} (model)

The model of an IFDD installation: LinkML sources, one file per namespace,
from which the JSON-LD contexts of the schema service, the vocabularies of
the type service and the units of the unit service are generated, together
with a documentation of every namespace. It runs no service: it is a build
that writes files into the content repositories of these three services.
This chapter describes the instance `{{ cookiecutter.ifdd_model_prj_slug }}`,
generated from the template `ifdd-de/model`.

| | |
|---|---|
| Sources | `src/linkml/type/*.yaml`, `src/linkml/unit/*.yaml` (instance-owned) |
| schema URL | `{{ cookiecutter.ifdd_schema_url }}` (default of `IFDD_MODEL_SCHEMA_URL` in `.env`) |
| type URL | `{{ cookiecutter.ifdd_type_url }}` (default of `IFDD_MODEL_TYPE_URL`) |
| unit URL | `{{ cookiecutter.ifdd_unit_url }}` (default of `IFDD_MODEL_UNIT_URL`) |
| Output | `output/` (not in Git); `just publish` copies it into the content directories |

## What the instance contains

The LinkML sources with examples, the reference files the build is checked
against (`tests/reference`), the build itself (`justfile`, the Python
package `ifdd_model`, the page template in `docgen/`), tests and this
documentation. The sources and references belong to the instance and are on
the cruft skip list; everything else comes from the template.

## Architecture

```{mermaid}
flowchart LR
  Src[src/linkml] --> Base[output/base]
  Base -->|just compare| Ref[(tests/reference)]
  Base -->|URLs from .env| Out[output/schema, type, unit]
  Out -->|just publish| Content[(content repositories)]
  Content --> Services[schema, type, unit services]
  Src --> Docs[output/docs]
```

| Who | Uses this repository for |
|---|---|
| domain experts | editing terms, labels and units in the LinkML sources |
| maintainers of the installation | building, checking and publishing into the content repositories |
| backend, UI, ct | indirectly: they read the contexts and vocabularies from the services |

```{toctree}
:maxdepth: 1

setup
build-release
operations
security
troubleshooting
reference
linkml
```
