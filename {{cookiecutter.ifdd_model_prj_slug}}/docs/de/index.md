(ifdd-model-index)=
# {{ cookiecutter.ifdd_model_prj_name }} (model)

Das Modell einer IFDD-Installation: LinkML-Quellen, eine Datei je
Namensraum, aus denen die JSON-LD-Contexts des schema-Dienstes, die
Vokabulare des type-Dienstes und die Einheiten des unit-Dienstes erzeugt
werden, dazu eine Dokumentation jedes Namensraums. Es läuft kein Dienst: Es
ist ein Build, der Dateien in die Content-Repos dieser drei Dienste
schreibt. Dieses Kapitel beschreibt die Instanz
`{{ cookiecutter.ifdd_model_prj_slug }}`, erzeugt aus dem Template
`ifdd-de/model`.

| | |
|---|---|
| Quellen | `src/linkml/type/*.yaml`, `src/linkml/unit/*.yaml` (gehören der Instanz) |
| schema-URL | `{{ cookiecutter.ifdd_schema_url }}` (Vorgabe von `IFDD_MODEL_SCHEMA_URL` in `.env`) |
| type-URL | `{{ cookiecutter.ifdd_type_url }}` (Vorgabe von `IFDD_MODEL_TYPE_URL`) |
| unit-URL | `{{ cookiecutter.ifdd_unit_url }}` (Vorgabe von `IFDD_MODEL_UNIT_URL`) |
| Ausgabe | `output/` (nicht in Git); `just publish` kopiert sie in die Content-Verzeichnisse |

## Was die Instanz enthält

Die LinkML-Quellen mit Beispielen, die Referenzdateien, gegen die der Build
geprüft wird (`tests/reference`), den Build selbst (`justfile`, das
Python-Paket `ifdd_model`, die Seitenvorlage in `docgen/`), Tests und diese
Dokumentation. Quellen und Referenzen gehören der Instanz und stehen auf der
Skip-Liste von cruft; alles andere kommt aus dem Template.

## Architektur

```{uml}
@startuml
left to right direction
  rectangle "src/linkml" as Src
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
