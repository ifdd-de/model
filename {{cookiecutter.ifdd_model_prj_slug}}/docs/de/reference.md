(ifdd-model-reference)=
# Referenz

Die Variablen des Templates stehen in der README von `ifdd-de/model`. Diese
Seite nennt, was keine Template-Variable ist.

## Aufbau

| Pfad | Zweck |
|---|---|
| `src/linkml/type/*.yaml` | eine Quelle je Namensraum des type-Dienstes (gehört der Instanz) |
| `src/linkml/unit/*.yaml` | Einheiten und Größenarten (gehört der Instanz) |
| `tests/reference/` | erwartete Ausgabe mit den Basis-URLs (gehört der Instanz) |
| `ifdd_model/` | Nachschritt des Contexts, Vokabular, URL-Ersetzung, Vergleich |
| `docgen/` | Seitenvorlage für `gen-doc`, Sphinx-Konfiguration und Übersichtsseiten der erzeugten Doku |
| `justfile` | der Build |
| `dotenv.dist` → `.env` | URLs und Content-Verzeichnisse |
| `docs/en`, `docs/de` | diese Dokumentation |

## Einstellungen in `.env`

| Variable | Bedeutung |
|---|---|
| `IFDD_MODEL_SCHEMA_URL` | URL des schema-Dienstes; ihr Pfad ist das Verzeichnis unter `json-ld/` der Contexts |
| `IFDD_MODEL_TYPE_URL` | URL des type-Dienstes; ersetzt `https://type/v1` in allen erzeugten Dateien |
| `IFDD_MODEL_UNIT_URL` | URL des unit-Dienstes; ersetzt `https://unit/v1` |
| `IFDD_MODEL_SCHEMA_TARGET`, `IFDD_MODEL_TYPE_TARGET`, `IFDD_MODEL_UNIT_TARGET` | Content-Verzeichnisse für `just publish` |

Nicht gesetzte oder leere URLs bedeuten die Basis-URLs.

## Ausgabe

| Pfad | Inhalt |
|---|---|
| `output/raw/<name>.jsonld` | Context, wie `gen-jsonld-context` ihn schreibt |
| `output/base/...` | alles mit den Basis-URLs, verglichen mit `tests/reference` |
| `output/schema/json-ld/<version>/<name>.jsonld` | JSON-LD-Contexts |
| `output/type/json-ld/<version>/<name>/index.jsonld` | Vokabulare |
| `output/unit/json-ld/<version>/<name>/index.jsonld` | Einheiten, Größenarten |
| `output/docs/en`, `output/docs/de` | MyST-Seiten; HTML in `output/docs/_build` |

Die erzeugten Seiten haben Labels mit `ifdd-model-ns-`; diese Dokumentation
nutzt `ifdd-model-`.

## Versionen

Python-Pakete: `requirements.txt`. PlantUML: `plantuml_version` und
`plantuml_sha256` im `justfile`.
