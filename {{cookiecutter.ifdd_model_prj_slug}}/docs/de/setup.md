(ifdd-model-setup)=
# Einrichtung

## Voraussetzungen

| | |
|---|---|
| Python | 3.13 oder neuer |
| Java | für PlantUML beim Bau der Dokumentation |
| Graphviz | `dot`, das Layout der PlantUML-Klassendiagramme |
| curl | `just plantuml` lädt das festgelegte PlantUML-Jar |

Die Python-Pakete, auch `just` (Paket `rust-just`), sind in
`requirements.txt` festgelegt.

## Umgebung

```shell
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

`.env` ist beim Erzeugen der Instanz aus `dotenv.dist` entstanden. Sie enthält
die URLs der drei Dienste und die Content-Verzeichnisse für `just publish`;
siehe {ref}`ifdd-model-reference`. In der Umgebung gesetzte Variablen haben
Vorrang vor `.env`.

## Erster Build

```shell
just build
```

Das prüft die Quellen, erzeugt die JSON-LD-Dateien, vergleicht sie mit
`tests/reference`, baut die Dokumentation und prüft sie. Das HTML liegt in
`output/docs/_build/en` und `output/docs/_build/de`.

```{note}
**Nicht getestet:** der Download des PlantUML-Jars hinter einem Proxy, der
Zertifikate ersetzt. curl braucht dann die CA des Proxys (etwa in
`CURL_CA_BUNDLE`), pip ebenso (`PIP_CERT`).
```

## Content-Verzeichnisse

`IFDD_MODEL_SCHEMA_TARGET`, `IFDD_MODEL_TYPE_TARGET` und
`IFDD_MODEL_UNIT_TARGET` in `.env` auf die Content-Verzeichnisse der drei
Dienste setzen, also die Verzeichnisse mit dem Versionsverzeichnis (etwa
`v1/`). Meist sind das Klone der Content-Repos der Installation. Ohne sie
verweigert `just publish` die Arbeit.
