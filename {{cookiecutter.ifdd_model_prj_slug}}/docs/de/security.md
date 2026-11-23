(ifdd-model-security)=
# Sicherheit

Das Modell beschreibt Terme; es enthält keine Daten und keine Secrets. Was es
erzeugt, liefern die Dienste schema, type und unit an alle aus, die sie
erreichen.

| Thema | Hier |
|---|---|
| wer die Ausgabe lesen darf | alle, die die Dienste lesen können; nichts in die Quellen schreiben, was nicht öffentlich sein soll |
| Secrets | keine; `.env` enthält nur URLs, Pfade und die Einstellungen des Webdienstes |
| der Webdienst | liefert die Quellen nur lesend an alle aus, die `{{ cookiecutter.ifdd_model_host }}` erreichen; Container schreibgeschützt, alle Capabilities entzogen, keine neuen Rechte, nichts aus `.env` im Container; versteckte Dateien wie `.git` werden nie ausgeliefert |
| Schreiben in Content-Repos | `just publish` überschreibt nur selbst erzeugte Dateien und löscht nie |
| PlantUML | beim Bau aus dem GitHub-Release geladen, gegen den SHA-256 im `justfile` geprüft, lokal ausgeführt; kein Diagramm-Server |
| Rechte an Domänen-Contexts | nicht Teil des Modells: das Backend vergibt sie nach dem Context-Namen |

```{note}
**Nicht getestet:** Der SHA-256 des PlantUML-Jars wurde beim ersten Download
ermittelt, nicht mit einer von PlantUML veröffentlichten Prüfsumme
verglichen.
```

Ein Context-Name entscheidet, wer die Werte eines Domänen-Contexts lesen
darf. Namen unter der Context-Wurzel der Installation wählen; einen Namen
ohne Punkt lehnt das Backend ab, außer `base` und den Aspekten.
