# ifdd-de/model

cookiecutter/cruft template for the **model** of an IFDD installation:
LinkML sources, one file per namespace, from which the build generates

- the JSON-LD contexts of the `schema` service (`gen-jsonld-context` plus a
  short post-processing step),
- the vocabularies of the `type` service (labels and comments in English and
  German, order, ranges, quantity kinds, units, bounds),
- the units and quantity kinds of the `unit` service,
- a Sphinx documentation of every namespace in English and German with
  PlantUML diagrams.

An instance is the model repository of one installation. `just publish`
copies the generated files into the content repositories of `schema`, `type`
and `unit`. A small web service (upstream `nginx-unprivileged`, like
`schema`, `type` and `unit`) serves the LinkML sources themselves, read-only,
below `/v1/` as `application/yaml`; the sources come from a content
directory that the build reads as well. The template brings the example
namespaces of these three templates as LinkML sources; the build reproduces
their example files.

**Status: prototype.** The structure and the names may still change.

## Generate an instance

```bash
cruft create --no-input --checkout <tag> \
  --config-file cookiecutter_all.yaml \
  --skip .env --skip src/linkml --skip tests/reference \
  --output-dir ../instances https://github.com/ifdd-de/model
```

The skip list keeps the settings, the LinkML sources and the reference files,
all instance-owned, out of every later `cruft update`. Then set the content
directories in `.env` of the instance (see its documentation, page "Setup").

## Variables

| Variable | Default | Meaning |
|---|---|---|
| `ifdd_model_prj_name`, `ifdd_model_prj_slug` | `IFDD Model Content`, derived | name; the slug names the directory |
| `ifdd_schema_url` | `http://schema/v1` | URL of the `schema` service; its path is the directory of the contexts below `json-ld/` |
| `ifdd_type_url` | `http://type/v1` | URL of the `type` service; replaces `https://type/v1` in the generated files |
| `ifdd_unit_url` | `http://unit/v1` | URL of the `unit` service; replaces `https://unit/v1` |
| `ifdd_model_host` | `model` | host name the proxy routes to the web service (`IFDD_MODEL_HOST`) |
| `ifdd_model_dev_port` | `8084` | port on 127.0.0.1 in development (`IFDD_MODEL_DEV_PORT`) |
| `ifdd_model_autoindex` | `y` | directory listings below `/v1/` |
| `ifdd_model_cors_origin` | `*` | `Access-Control-Allow-Origin`: `*` or one origin |
| `ifdd_model_cache_max_age` | `300` | `Cache-Control: max-age` in seconds, `0` for no-cache |
| `ifdd_model_memory_limit` | `128M` | memory limit of the container in production |
| `ifdd_model_content_dir` | `./src/linkml` | default of `IFDD_MODEL_CONTENT_DIR`: the directory with the LinkML sources, served and built from |
| `ifdd_nginx_image` | `nginx/nginx-unprivileged:1.30.8-alpine-slim` | image of the web service (shared with `schema`, `type`, `unit`) |
| `ifdd_proxy_network` | `proxy-net` | external Docker network of the proxy (shared) |

The three URLs are shared with the other templates and have no trailing
slash. They become the defaults of `IFDD_MODEL_*_URL` in `.env`. The
pre-generation hook rejects URLs without host or version path, slugs with
characters other than letters, digits, `_` and `-` (the slug names the
Traefik router), and values of the web service that would not work (the
same rules as in `ifdd-de/schema`).

## Layout

| Path | Purpose |
|---|---|
| `cookiecutter.json` | variables |
| `hooks/` | validation before, `.env` after generation |
| `{{cookiecutter.ifdd_model_prj_slug}}/` | the instance, see its README and documentation |
| `tests/test_template.py` | renders the fixtures, checks the hooks, and runs counter-checks bound to the example sources |
| `{{cookiecutter.ifdd_model_prj_slug}}/tests/test_config.py`, `smoke.sh` | the web service: static checks (and nginx itself, when installed), the running container |
| `tests/check_docs.py`, `tests/docs/` | used by `template-test.yml`: the documentation of the instance |
| `tests/fixtures/` | `defaults`, `custom` (other slug and URLs, a unit URL with a sub-path) |

`.github`, `docgen`, `ifdd_model`, `justfile`, `src` and `tests` inside the
instance are on the copy-without-render list: GitHub Actions expressions,
`just` syntax and the `gen-doc` page template collide with Jinja.

## Documentation of the instance

Two kinds:

- **Operating documentation** in `docs/en` and `docs/de` (MyST, labels
  `ifdd-model-`): `index`, `setup`, `build-release`, `operations`,
  `security`, `troubleshooting`, `reference` and `linkml` (how LinkML
  becomes JSON-LD). cookiecutter fills in the values of the instance; like
  in the other templates, the pages are meant to be copied into a Sphinx
  project that documents all services, which needs `myst_parser` and
  `sphinxcontrib.plantuml` (PlantUML with Java and Graphviz). For
  `tests/check_docs.py`, `tests/docs/get_plantuml.sh` downloads the pinned
  PlantUML jar and prints its path:
  `export IFDD_PLANTUML_JAR="$(tests/docs/get_plantuml.sh)"`.
- **Documentation of the namespaces**, generated by `just docs` from the
  LinkML sources into `output/docs` (labels `ifdd-model-ns-`), with PlantUML
  diagrams.

Rules for editing the pages in the template: change both languages in the
same commit; no Jinja syntax in examples; do not write the text
`cookiecutter` followed by a dot literally (the CI greps for it).

## CI

| Workflow | Does |
|---|---|
| `template-test.yml` | renders each fixture, checks for leftover placeholders, checks the documentation of the instance, runs `just build` and `just test` in the instance, checks the compose files and starts the web service (`tests/smoke.sh`, development and production); runs `tests/` of the template |
| `template-update-test.yml` | generates from the latest tag, applies the current template with `cruft update`, fails on reject files, builds and tests the updated instance; does nothing while there is no tag |

## AI assistance

Parts of this repository, in particular tests, test data and documentation,
were developed or improved with the help of large language models. The
maintainer has reviewed and approved them.

## License

BSD-3-Clause, see `LICENSE`. PlantUML is downloaded at build time and not
part of this repository.
