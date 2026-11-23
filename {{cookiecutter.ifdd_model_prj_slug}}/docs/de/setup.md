(ifdd-model-setup)=
# Einrichtung

## Voraussetzungen

| | |
|---|---|
| Python | 3.13 oder neuer |
| Java | für PlantUML beim Bau der Dokumentation |
| Graphviz | `dot`, das Layout der PlantUML-Klassendiagramme |
| curl | `just plantuml` lädt das festgelegte PlantUML-Jar |
| Docker mit Compose | der Webdienst läuft als Container |
| das externe Netz `{{ cookiecutter.ifdd_proxy_network }}` und eine laufende proxy-Instanz | Traefik leitet `{{ cookiecutter.ifdd_model_host }}` anhand der Labels an den Webdienst |

Die Python-Pakete, auch `just` (Paket `rust-just`), sind in
`requirements.txt` festgelegt.

## Umgebung

```shell
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

`.env` ist beim Erzeugen der Instanz aus `dotenv.dist` entstanden. Sie enthält
die URLs der drei Dienste, die Content-Verzeichnisse für `just publish` sowie
Host, Content-Verzeichnis und Entwicklungs-Port des Webdienstes; siehe {ref}`ifdd-model-reference`. In der Umgebung gesetzte Variablen haben
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

## LinkML-Quellen

Die Quellen liegen in einem eigenen Content-Repo, getrennt auf dem Host
geklont. `IFDD_MODEL_CONTENT_DIR` in `.env` nennt das Verzeichnis mit `type/`
und `unit/`; der Webdienst liefert es aus und `just` baut daraus, beide
nutzen also immer dieselben Dateien:

```bash
git clone <Content-Repo des Modells> /srv/ifdd/model-content
# in .env:
IFDD_MODEL_CONTENT_DIR=/srv/ifdd/model-content
```

`/srv/ifdd/model-content` ist ein Beispiel.

- Einen absoluten Pfad nehmen oder einen relativen, der mit `./` oder `../`
  beginnt. Ohne dieses Präfix liest compose den Wert als Volume-Namen und
  startet nicht (`refers to undefined volume`).
- Der Container läuft als UID 101 und braucht Lesezugriff: Die Dateien
  müssen für „andere“ lesbar sein, wie bei einem Klon mit der üblichen
  `umask 022`.
- Versteckte Dateien und Verzeichnisse (`.git`, …) werden nie ausgeliefert;
  die Wurzel eines Klons einzuhängen ist daher sicher.
- Leer baut `just` aus `src/linkml`, den Beispielen des Templates.

## Webdienst

```bash
docker network create {{ cookiecutter.ifdd_proxy_network }}   # einmal je Host, falls der proxy es nicht schon tat
docker compose -f docker-compose-production.yml up -d
docker compose -f docker-compose-production.yml ps
```

Ohne `IFDD_MODEL_HOST` oder `IFDD_MODEL_CONTENT_DIR` in `.env` startet
`docker compose` nicht und nennt die Variable. `ps` sollte den Dienst als
healthy melden. Für die lokale Entwicklung:

```bash
docker compose -f docker-compose-development.yml up -d
curl http://127.0.0.1:{{ cookiecutter.ifdd_model_dev_port }}/v1/
```

Die Entwicklung liefert `src/linkml`, solange `IFDD_MODEL_CONTENT_DIR` nicht
gesetzt ist; der Port ist nur an 127.0.0.1 gebunden.

Die Labels melden einen Router und einen Service, beide
`{{ cookiecutter.ifdd_model_prj_slug }}`, für `Host(${IFDD_MODEL_HOST})` auf
Port 8080, in Produktion mit den Middlewares `security-headers@file` und
`csp-api@file` des proxy. `tls`- oder `entrypoints`-Labels gibt es bewusst
nicht: TLS und Zertifikate sind am Entrypoint des proxy gesetzt. Dienste, die
die Quellen aus einem Container lesen, brauchen
`{{ cookiecutter.ifdd_model_host }}` in den internen Hosts des proxy.

```{note}
**Nicht getestet:** der Webdienst hinter einem laufenden IFDD-proxy. Die CI
des Templates startet den Container und prüft ihn vom Host aus.
```
