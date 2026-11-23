(ifdd-model-index)=
# {{ cookiecutter.ifdd_model_prj_name }} (model)

Das Modell einer IFDD-Installation: LinkML-Quellen, eine Datei je
Namensraum, aus denen die JSON-LD-Contexts des schema-Dienstes, die
Vokabulare des type-Dienstes und die Einheiten des unit-Dienstes erzeugt
werden, dazu eine Dokumentation jedes Namensraums. Es ist ein Build, der
Dateien in die Content-Repos dieser drei Dienste schreibt, und ein kleiner
Webdienst, der die LinkML-Quellen selbst nur lesend unter `/v1/` ausliefert.
Dieses Kapitel beschreibt die Instanz
`{{ cookiecutter.ifdd_model_prj_slug }}`, erzeugt aus dem Template
`ifdd-de/model`.

| | |
|---|---|
| Quellen | `type/*.yaml` und `unit/*.yaml` im Content-Verzeichnis `IFDD_MODEL_CONTENT_DIR` (Vorgabe `{{ cookiecutter.ifdd_model_content_dir }}`; `src/linkml` enthält die Beispiele) |
| Webdienst | Host `{{ cookiecutter.ifdd_model_host }}` (`IFDD_MODEL_HOST`), die Quellen unter `/v1/` als `application/yaml` |
| schema-URL | `{{ cookiecutter.ifdd_schema_url }}` (Vorgabe von `IFDD_MODEL_SCHEMA_URL` in `.env`) |
| type-URL | `{{ cookiecutter.ifdd_type_url }}` (Vorgabe von `IFDD_MODEL_TYPE_URL`) |
| unit-URL | `{{ cookiecutter.ifdd_unit_url }}` (Vorgabe von `IFDD_MODEL_UNIT_URL`) |
| Ausgabe | `output/` (nicht in Git); `just publish` kopiert sie in die Content-Verzeichnisse |

## Was die Instanz enthält

Die LinkML-Quellen mit Beispielen, den Webdienst (Compose-Dateien und
`nginx/`), die Referenzdateien, gegen die der Build
geprüft wird (`tests/reference`), den Build selbst (`justfile`, das
Python-Paket `ifdd_model`, die Seitenvorlage in `docgen/`), Tests und diese
Dokumentation. Quellen und Referenzen gehören der Instanz und stehen auf der
Skip-Liste von cruft; alles andere kommt aus dem Template.

## Architektur

```{uml}
@startuml
left to right direction
  rectangle "Content-Verzeichnis" as Src
  rectangle "model-Dienst" as Model
  Src --> Model : /v1/
  rectangle "output/base" as Base
  Src --> Base
  database "tests/reference" as Ref
  Base --> Ref : just compare
  rectangle "output/schema, type, unit" as Out
  Base --> Out : URLs aus .env
  database "Content-Repos" as Content
  Out --> Content : just publish
  rectangle "Dienste schema, type, unit" as Services
  Content --> Services
  rectangle "output/docs" as Docs
  Src --> Docs
@enduml
```

| Wer | Nutzt dieses Repo für |
|---|---|
| Fachleute | Pflege von Termen, Bezeichnungen und Einheiten in den LinkML-Quellen |
| Betreuer der Installation | Bauen, Prüfen und Veröffentlichen in die Content-Repos |
| Backend, UI, ct | mittelbar: sie lesen Contexts und Vokabulare aus den Diensten |
| Nutzer, Notebooks, Werkzeuge | lesen die LinkML-Quellen aus dem model-Dienst |

```{toctree}
:maxdepth: 1

setup
build-release
operations
security
troubleshooting
reference
linkml
```
