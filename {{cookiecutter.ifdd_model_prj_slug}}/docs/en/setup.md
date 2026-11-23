(ifdd-model-setup)=
# Setup

## Requirements

| | |
|---|---|
| Python | 3.13 or newer |
| Java | to run PlantUML while building the documentation |
| Graphviz | `dot`, the layout of the PlantUML class diagrams |
| curl | `just plantuml` downloads the pinned PlantUML jar |
| Docker with Compose | the web service runs as a container |
| the external network `{{ cookiecutter.ifdd_proxy_network }}` and a running proxy instance | Traefik routes `{{ cookiecutter.ifdd_model_host }}` to the web service by its labels |

The Python packages, including `just` (package `rust-just`), are pinned in
`requirements.txt`.

## Environment

```shell
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

`.env` was created from `dotenv.dist` when the instance was generated. It
holds the URLs of the three services, the content directories for
`just publish`, and the host, content directory and development port of the
web service; see {ref}`ifdd-model-reference`. Variables set in the
environment win over `.env`.

## First build

```shell
just build
```

This lints the sources, generates the JSON-LD files, compares them with
`tests/reference`, builds the documentation and checks it. The HTML is in
`output/docs/_build/en` and `output/docs/_build/de`.

```{note}
**Not tested:** downloading the PlantUML jar behind a proxy that replaces
certificates. curl then needs the CA of the proxy (for example in
`CURL_CA_BUNDLE`), pip as well (`PIP_CERT`).
```

## Content directories

Set `IFDD_MODEL_SCHEMA_TARGET`, `IFDD_MODEL_TYPE_TARGET` and
`IFDD_MODEL_UNIT_TARGET` in `.env` to the content directories of the three
services, the directories that contain the version directory (such as
`v1/`). Usually these are clones of the content repositories of the
installation. Without them `just publish` refuses to run.

## LinkML sources

The sources live in their own content repository, cloned separately on the
host. `IFDD_MODEL_CONTENT_DIR` in `.env` names the directory with `type/`
and `unit/`; the web service serves it and `just` builds from it, so both
always use the same files:

```bash
git clone <model content repository> /srv/ifdd/model-content
# in .env:
IFDD_MODEL_CONTENT_DIR=/srv/ifdd/model-content
```

`/srv/ifdd/model-content` is an example.

- Use an absolute path, or a relative one starting with `./` or `../`.
  Without that prefix compose reads the value as a volume name and refuses
  to start (`refers to undefined volume`).
- The container runs as UID 101 and needs read access: files must be
  readable for "others", which a clone with the usual `umask 022` is.
- Hidden files and directories (`.git`, ...) are never served, so mounting
  the root of a clone is safe.
- Empty, `just` builds from `src/linkml`, the examples of the template.

## Web service

```bash
docker network create {{ cookiecutter.ifdd_proxy_network }}   # once per host, unless the proxy already did
docker compose -f docker-compose-production.yml up -d
docker compose -f docker-compose-production.yml ps
```

Without `IFDD_MODEL_HOST` or `IFDD_MODEL_CONTENT_DIR` in `.env`,
`docker compose` refuses to start with a message naming the variable. `ps`
should report the service as healthy. For local development:

```bash
docker compose -f docker-compose-development.yml up -d
curl http://127.0.0.1:{{ cookiecutter.ifdd_model_dev_port }}/v1/
```

Development serves `src/linkml` unless `IFDD_MODEL_CONTENT_DIR` is set; the
port is bound to 127.0.0.1 only.

The labels announce one router and one service, both named
`{{ cookiecutter.ifdd_model_prj_slug }}`, for `Host(${IFDD_MODEL_HOST})` on
port 8080, with the middlewares `security-headers@file` and `csp-api@file` of
the proxy in production. There are deliberately no `tls` or `entrypoints`
labels: TLS and certificates are set on the proxy entry point. Services that
read the sources from inside a container need `{{ cookiecutter.ifdd_model_host }}`
in the internal hosts of the proxy.

```{note}
**Not tested:** the web service behind a running IFDD proxy. The CI of the
template starts the container and checks it from the host.
```
