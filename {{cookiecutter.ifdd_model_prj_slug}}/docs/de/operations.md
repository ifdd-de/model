(ifdd-model-operations)=
# Betrieb

## Veröffentlichen in die Content-Repos

```shell
just publish
```

Das Rezept erzeugt die JSON-LD-Dateien und kopiert
`output/<dienst>/json-ld/` in das Verzeichnis aus
`IFDD_MODEL_<DIENST>_TARGET`. Es prüft alle drei Ziele, bevor es etwas
kopiert, überschreibt Dateien, die es erzeugt hat, und löscht nie. Dateien in
einem Ziel, die nicht aus dem Modell stammen, werden aufgelistet und bleiben
unverändert. Committen und Pushen in den Content-Repos ist ein eigener
Schritt.

Die Dienste liefern die Dateien aus ihren Content-Verzeichnissen aus; sonst
muss nichts erzeugt werden.

```{note}
**Nicht getestet:** das Veröffentlichen in die Content-Klone laufender
schema-, type- und unit-Dienste und wie lange deren Caches die vorigen
Dateien halten.
```

## Webdienst

```bash
docker compose -f docker-compose-production.yml up -d
docker compose -f docker-compose-production.yml ps
docker compose -f docker-compose-production.yml logs
docker compose -f docker-compose-production.yml down
```

Der Dienst braucht beim Start das proxy-Netz und sonst nichts. Sein
Health-Check ruft alle 30 s `wget` auf `http://127.0.0.1:8080/healthz` auf.
Neue oder geänderte Quellen (`git pull` im Content-Klon) liefert er sofort
aus; nur Änderungen an `nginx/` brauchen `docker compose restart`. Clients
dürfen eine Antwort `Cache-Control: max-age` Sekunden lang halten (hier
{{ cookiecutter.ifdd_model_cache_max_age }}) und prüfen sie dann mit dem ETag.

## Template-Updates

```shell
cruft update
```

`src/linkml`, `tests/reference` und `.env` stehen auf der Skip-Liste und
bleiben unverändert. Neue Einträge in `dotenv.dist` erreichen eine
bestehende `.env` nicht; sie sind von Hand zu übernehmen. Nach einem Update
`just build` und `just test` aufrufen.

## Einen Namensraum entfernen

Seine Quelldatei löschen, `just json accept` aufrufen und die erzeugten
Dateien in den Content-Repos von Hand löschen: `just publish` listet sie auf,
löscht aber nie.
