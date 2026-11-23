(ifdd-model-build-release)=
# Bau und Freigabe

## Bau

| Rezept | Macht |
|---|---|
| `just json` | `just base` und `just relocate` |
| `just base` | Contexts, Vokabulare und Einheiten mit den Basis-URLs nach `output/base` |
| `just relocate` | kopiert `output/base` nach `output/<dienst>/json-ld/<version>` mit den URLs aus `.env` |
| `just compare` | vergleicht `output/base` nach Bedeutung mit `tests/reference` |
| `just docs` | MyST-Seiten jedes Namensraums und ihr HTML mit PlantUML-Diagrammen |
| `just check-docs` | gleiche Dateien, Labels und Überschriften in beiden Sprachen, Sphinx-Bau mit `-W` |
| `just build` | alles zusammen, nach `just clean` und `just lint` |

Jedes Rezept gibt die Befehle aus, die es aufruft. Die Seite
{ref}`ifdd-model-linkml` erklärt, was jeder Schritt mit den Quellen macht.

## Das Modell ändern

1. Eine Datei in `src/linkml` bearbeiten.
2. `just json compare` aufrufen und die gemeldeten Unterschiede lesen.
3. Sind sie gewollt, `just accept` aufrufen: Die Ausgabe wird die neue
   Referenz. Quellen und Referenzen zusammen committen.
4. `just test` und `just docs` aufrufen.

Ein neuer Namensraum ist eine neue Datei; einen Context bekommt er nur mit
einer Klasse, deren `class_uri` im eigenen Namensraum `<präfix>:schema` ist.

## Freigabe

Die Instanz baut kein Image und kein Paket; der Webdienst nutzt das
Upstream-Image `{{ cookiecutter.ifdd_nginx_image }}`. Eine Freigabe des Modells ist ein
Commit der Quellen und Referenzen, danach `just publish` und Commits in den
Content-Repos. Die Versionen der Werkzeuge stehen in `requirements.txt` und
im `justfile` (PlantUML); Dependabot schlägt Updates der Python-Pakete vor.
