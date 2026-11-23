(ifdd-model-security)=
# Security

The model describes terms; it holds no data and no secrets. What it
generates is served by the schema, type and unit services to everyone who
reaches them.

| Concern | Here |
|---|---|
| who may read the output | everyone who can read the services; put nothing into the sources that is not meant to be public |
| secrets | none; `.env` holds URLs, paths and the settings of the web service only |
| the web service | serves the sources read-only to everyone who reaches `{{ cookiecutter.ifdd_model_host }}`; container read-only, all capabilities dropped, no new privileges, nothing from `.env` inside; hidden files such as `.git` are never served |
| writing to content repositories | `just publish` only overwrites files it generated and never deletes |
| PlantUML | downloaded at build time from the GitHub release, checked against the SHA-256 in the `justfile`, run locally; no diagram server |
| access rights of domain contexts | not part of the model: the backend grants them by context name |

```{note}
**Not tested:** the SHA-256 of the PlantUML jar was recorded at the first
download, not compared with a checksum published by PlantUML.
```

A context name decides who may read the values of a domain context. Choose
names under the context root of the installation; a name without a dot is
refused by the backend unless it is `base` or an aspect.
