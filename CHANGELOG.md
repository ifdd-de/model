# Changelog

All notable changes to this template are documented in this file.

## [26.11.11] - 2026-11-24

### Version

- Version aligned across all ifdd-de repositories (26.11.11); this section
  also covers the web service tagged as v26.11.6.
- `ifdd_nginx_image` `nginx/nginx-unprivileged:1.30.8-alpine-slim` (was
  `nginxinc/nginx-unprivileged:1.30.6-alpine-slim`, stable branch). The image
  moved to the Docker Hub namespace `nginx`; `nginxinc` gets no newer releases
  (README of nginx/docker-nginx-unprivileged).

### Added

- Web service: the instance serves its LinkML sources read-only below
  `/v1/` (`/v1/type/<name>.yaml` as `application/yaml`, RFC 9512) with the
  upstream image `nginx-unprivileged`, like `schema`, `type` and `unit`:
  compose files for development and production, `nginx/default.conf` and
  `nginx/mime.types`, CORS on every answer, hidden files never served,
  nothing outside `/v1/`, `/healthz`. New variables `ifdd_model_host`,
  `ifdd_model_dev_port`, `ifdd_model_autoindex`, `ifdd_model_cors_origin`,
  `ifdd_model_cache_max_age`, `ifdd_model_memory_limit`,
  `ifdd_model_content_dir` and the shared `ifdd_nginx_image`,
  `ifdd_proxy_network`; new `.env` settings `IFDD_MODEL_HOST`,
  `IFDD_MODEL_CONTENT_DIR`, `IFDD_MODEL_DEV_PORT`.
- `IFDD_MODEL_CONTENT_DIR`, usually a clone of the model content repository,
  is also the source of `just`; unset or empty it is `src/linkml`.
- Tests of the instance: `tests/test_config.py` (compose and nginx, and
  nginx itself when installed), `tests/smoke.sh` (the container); the CI of
  the template checks the compose files and runs both smoke modes.

### Changed

- The pre-generation hook also checks the values of the web service. The
  slug now allows letters, digits, `_` and `-` only and must not start with
  a digit or `-` (it names the Traefik router; dots broke the labels).

### Upgrade

- Existing instances: copy `IFDD_MODEL_HOST`, `IFDD_MODEL_CONTENT_DIR` and
  `IFDD_MODEL_DEV_PORT` from `dotenv.dist` into `.env` by hand (`.env` is on
  the skip list). Without `IFDD_MODEL_CONTENT_DIR` in `.env` `just` keeps
  building from `src/linkml`.

### CI

- CI: GitHub Actions pinned to commit SHAs (version as comment),
  `persist-credentials: false` on every checkout; the same in the workflows of
  the instance.

## [26.11.1] - 2026-11-14

### Added

- cookiecutter/cruft template for the model of an IFDD installation, with
  the variables `ifdd_model_prj_name`, `ifdd_model_prj_slug` and the shared
  `ifdd_schema_url`, `ifdd_type_url`, `ifdd_unit_url`; hooks validate the
  values and create `.env`.
- LinkML sources for the example namespaces of the schema, type and unit
  templates: base, product, function, location, organisation, the domains
  breaker.grid.example.ifdd.de and maintenance.ops.example.ifdd.de, the
  time-series vocabulary climate.ops.example.ifdd.de, units and quantity
  kinds.
- Generation of the JSON-LD contexts (`gen-jsonld-context` plus
  post-processing), the type vocabularies and the unit vocabularies, first
  with base URLs and compared by meaning with reference files, then for the
  URLs of the installation.
- `just publish`: copies the generated files into the content directories
  of schema, type and unit; never deletes.
- Documentation of the namespaces (Sphinx, English and German, PlantUML
  diagrams) and operating documentation of the instance.
- CI: template test with both fixtures, template update test, instance CI.
