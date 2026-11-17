(ifdd-model-index)=
# IFDD-Modell

Die LinkML-Quellen in `src/linkml` beschreiben die Namensräume der
IFDD-Dienste schema, type und unit. Je Namensraum gibt es genau eine
Quelldatei als Single Point of Truth. Aus ihr erzeugt der Build den
JSON-LD-Context (schema-Dienst), das Vokabular (type-Dienst) oder die
Einheiten (unit-Dienst) sowie diese Dokumentation.

{ref}`ifdd-model-mapping` erklärt, wie aus LinkML-Elementen JSON-LD wird.

## Namensräume des type-Dienstes

```{toctree}
:maxdepth: 1
:glob:

type/*
```

## Namensräume des unit-Dienstes

```{toctree}
:maxdepth: 1
:glob:

unit/*
```

## Hintergrund

```{toctree}
:maxdepth: 1

mapping
```
