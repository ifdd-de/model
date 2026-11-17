# Reference files

The expected output of `just base` (`output/base`), with the base URLs
`https://schema/v1`, `https://type/v1` and `https://unit/v1`. `just compare`
and `tests/test_build.py` compare the generated files with these by meaning.

| Directory | Content |
|---|---|
| `schema/<name>.jsonld` | JSON-LD context |
| `type/<name>/index.jsonld` | vocabulary |
| `unit/<name>/index.jsonld` | units, quantity kinds |

After a change of a LinkML source, `just json compare` shows the
differences. Once they are wanted, `just accept` makes the output the new
reference; commit both together.

The references of the template examples are the example files of the
templates `ifdd-de/schema` (commit `29c4fea`), `ifdd-de/type` (`81afb99`)
and `ifdd-de/unit` (`cdd4e74`), with their URL placeholders replaced by the
base URLs.
