(ifdd-model-troubleshooting)=
# Fehlersuche

| Meldung | Ursache und Abhilfe |
|---|---|
| `DIFFERS output/base/...` | die erzeugte Datei bedeutet nicht mehr dasselbe wie ihre Referenz; die gelisteten Terme oder Tripel lesen; ist die Änderung gewollt, `just accept` |
| `NO REFERENCE ...` | ein neuer Namensraum; seine Ausgabe prüfen, dann `just accept` |
| `MISSING ...` | eine Referenz ohne erzeugte Datei, etwa nach dem Löschen einer Quelle; `just accept` entfernt die Referenz |
| `error: type: URL ...` | eine URL in `.env` mit Schrägstrich am Ende, Query, Leerzeichen oder ohne Versionspfad |
| `IFDD_MODEL_TYPE_TARGET is not set in .env` | `just publish` braucht alle drei Content-Verzeichnisse |
| `SHA-256 mismatch for ...plantuml...jar` | die geladene Datei ist nicht die festgelegte; `.cache/` löschen und wiederholen oder den Proxy prüfen |
| `IFDD_PLANTUML_JAR must point to plantuml.jar` | die Doku über `just` bauen, das vorher das Jar lädt |
| Sphinx `error while running plantuml` | Java oder Graphviz (`dot`) fehlt |
| Befunde von `linkml-lint` | die Quelle verletzt eine LinkML-Regel; `.linkmllint.yaml` nennt die abgeschalteten Regeln mit Grund |
| `terms without rank` | jeder Term braucht einen `rank` (seine Reihenfolge im Vokabular) |
| `set IFDD_MODEL_CONTENT_DIR in .env` | Produktion braucht das Content-Verzeichnis, siehe {ref}`ifdd-model-setup` |
| `refers to undefined volume` | `IFDD_MODEL_CONTENT_DIR` ohne führendes `./`, `../` oder `/` |
| `network {{ cookiecutter.ifdd_proxy_network }} declared as external, but could not be found` | das Netz anlegen oder zuerst den proxy starten |
| 404 für eine Quelle | dem Pfad fehlt `/v1/`, oder die Datei liegt nicht im Content-Verzeichnis |
| 403 für eine Quelle | die Datei ist für UID 101 nicht lesbar (`chmod o+r`) |
