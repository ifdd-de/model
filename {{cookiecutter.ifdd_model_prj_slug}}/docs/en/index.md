(ifdd-model-index)=
# {{ cookiecutter.ifdd_model_prj_name }} (model)

The model of an IFDD installation: LinkML sources, one file per namespace,
from which the JSON-LD contexts of the schema service, the vocabularies of
the type service and the units of the unit service are generated, together
with a documentation of every namespace. It is a build that writes files
into the content repositories of these three services, and a small web
service that serves the LinkML sources themselves, read-only, below `/v1/`.
This chapter describes the instance `{{ cookiecutter.ifdd_model_prj_slug }}`,
generated from the template `ifdd-de/model`.

| | |
|---|---|
| Sources | `type/*.yaml` and `unit/*.yaml` in the content directory `IFDD_MODEL_CONTENT_DIR` (default `{{ cookiecutter.ifdd_model_content_dir }}`; `src/linkml` holds the examples) |
| Web service | host `{{ cookiecutter.ifdd_model_host }}` (`IFDD_MODEL_HOST`), the sources below `/v1/` as `application/yaml` |
| schema URL | `{{ cookiecutter.ifdd_schema_url }}` (default of `IFDD_MODEL_SCHEMA_URL` in `.env`) |
| type URL | `{{ cookiecutter.ifdd_type_url }}` (default of `IFDD_MODEL_TYPE_URL`) |
| unit URL | `{{ cookiecutter.ifdd_unit_url }}` (default of `IFDD_MODEL_UNIT_URL`) |
| Output | `output/` (not in Git); `just publish` copies it into the content directories |

## What the instance contains

The LinkML sources with examples, the web service (compose files and
`nginx/`), the reference files the build is checked
against (`tests/reference`), the build itself (`justfile`, the Python
package `ifdd_model`, the page template in `docgen/`), tests and this
documentation. The sources and references belong to the instance and are on
the cruft skip list; everything else comes from the template.

## Architecture

```{uml}
@startuml
left to right direction
  rectangle "content directory" as Src
  rectangle "model service" as Model
  Src --> Model : /v1/
  rectangle "output/base" as Base
  Src --> Base
  database "tests/reference" as Ref
  Base --> Ref : just compare
  rectangle "output/schema, type, unit" as Out
  Base --> Out : URLs from .env
  database "content repositories" as Content
  Out --> Content : just publish
  rectangle "schema, type, unit services" as Services
  Content --> Services
  rectangle "output/docs" as Docs
  Src --> Docs
@enduml
```

| Who | Uses this repository for |
|---|---|
| domain experts | editing terms, labels and units in the LinkML sources |
| maintainers of the installation | building, checking and publishing into the content repositories |
| backend, UI, ct | indirectly: they read the contexts and vocabularies from the services |
| users, notebooks, tools | read the LinkML sources from the model service |

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
