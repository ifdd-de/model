(ifdd-model-troubleshooting)=
# Troubleshooting

| Message | Cause and fix |
|---|---|
| `DIFFERS output/base/...` | the generated file no longer means the same as its reference; read the listed terms or triples; if the change is wanted, `just accept` |
| `NO REFERENCE ...` | a new namespace; check its output, then `just accept` |
| `MISSING ...` | a reference without generated file, for example after deleting a source; `just accept` removes the reference |
| `error: type: URL ...` | a URL in `.env` with trailing slash, query, spaces or without version path |
| `IFDD_MODEL_TYPE_TARGET is not set in .env` | `just publish` needs all three content directories |
| `SHA-256 mismatch for ...plantuml...jar` | the downloaded file is not the pinned one; delete `.cache/` and retry, or check the proxy |
| `IFDD_PLANTUML_JAR must point to plantuml.jar` | run the docs through `just`, which downloads the jar first |
| Sphinx `error while running plantuml` | Java or Graphviz (`dot`) missing |
| `linkml-lint` findings | the source breaks a LinkML rule; `.linkmllint.yaml` lists the rules that are off and why |
| `terms without rank` | every term needs a `rank` (its order in the vocabulary) |
