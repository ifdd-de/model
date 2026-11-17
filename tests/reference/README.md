# Reference files

Copies of the example files of the IFDD templates, unchanged, with their
cookiecutter placeholders. The build must reproduce their meaning
(`just compare`, `tests/test_build.py`).

| Directory | Template | Path in the template | Commit |
|---|---|---|---|
| `schema/v1` | `ifdd-de/schema` | `{{cookiecutter.ifdd_schema_prj_slug}}/examples/json-ld/v1` | `29c4fea` |
| `type/v1` | `ifdd-de/type` | `{{cookiecutter.ifdd_type_prj_slug}}/examples/json-ld/v1` | `81afb99` |
| `unit/v1` | `ifdd-de/unit` | `{{cookiecutter.ifdd_unit_prj_slug}}/examples/json-ld/v1` | `cdd4e74` |

When a LinkML source is changed on purpose, `just compare` reports the
difference. Once the change is wanted, the generated file replaces the
example in the template, and the reference here is updated with it.
