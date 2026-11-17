(ifdd-model-setup)=
# Setup

## Requirements

| | |
|---|---|
| Python | 3.13 or newer |
| Java | to run PlantUML while building the documentation |
| Graphviz | `dot`, the layout of the PlantUML class diagrams |
| curl | `just plantuml` downloads the pinned PlantUML jar |

The Python packages, including `just` (package `rust-just`), are pinned in
`requirements.txt`.

## Environment

```shell
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

`.env` was created from `dotenv.dist` when the instance was generated. It
holds the URLs of the three services and the content directories for
`just publish`; see {ref}`ifdd-model-reference`. Variables set in the
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
