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
