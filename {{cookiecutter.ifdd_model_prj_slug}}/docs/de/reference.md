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
| `docker-compose-production.yml`, `docker-compose-development.yml` | der Webdienst |
| `nginx/default.conf`, `nginx/mime.types` | seine Konfiguration |
| `dotenv.dist` → `.env` | URLs, Content-Verzeichnisse, Einstellungen des Webdienstes |
| `docs/en`, `docs/de` | diese Dokumentation |

## Einstellungen in `.env`

| Variable | Bedeutung |
|---|---|
| `IFDD_MODEL_SCHEMA_URL` | URL des schema-Dienstes; ihr Pfad ist das Verzeichnis unter `json-ld/` der Contexts |
| `IFDD_MODEL_TYPE_URL` | URL des type-Dienstes; ersetzt `https://type/v1` in allen erzeugten Dateien |
| `IFDD_MODEL_UNIT_URL` | URL des unit-Dienstes; ersetzt `https://unit/v1` |
| `IFDD_MODEL_SCHEMA_TARGET`, `IFDD_MODEL_TYPE_TARGET`, `IFDD_MODEL_UNIT_TARGET` | Content-Verzeichnisse für `just publish` |
| `IFDD_MODEL_HOST` | Hostname, unter dem der proxy an den Webdienst leitet; Pflicht |
| `IFDD_MODEL_CONTENT_DIR` | Verzeichnis mit den LinkML-Quellen; unter `/v1/` ausgeliefert und von `just` gelesen; Pflicht in Produktion, leer heißt für `just` `src/linkml` |
| `IFDD_MODEL_DEV_PORT` | Port auf 127.0.0.1 in der Entwicklung |

Nicht gesetzte oder leere URLs bedeuten die Basis-URLs.

## Webdienst

| Pfad | Antwort |
|---|---|
| `/v1/<pfad>` | die Datei `<pfad>` des Content-Verzeichnisses; `.yaml` als `application/yaml` |
| `/v1/<verzeichnis>/` | eine Verzeichnisliste (hier {{ "an" if cookiecutter.ifdd_model_autoindex == "y" else "aus" }}) |
| `/healthz` | `ok`, für den Health-Check |
| versteckte Dateien, alles andere | 404 |

Jede Antwort unter `/v1/` trägt `Access-Control-Allow-Origin: {{ cookiecutter.ifdd_model_cors_origin }}`,
auch bei Fehlern; ein Preflight (`OPTIONS`) antwortet mit 204.

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
