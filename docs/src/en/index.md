(ifdd-model-index)=
# IFDD model

The LinkML sources in `src/linkml` describe the namespaces of the IFDD
services schema, type and unit. One source file per namespace is the single
point of truth; from it the build generates the JSON-LD context (schema
service), the vocabulary (type service) or the units (unit service), and
this documentation.

{ref}`ifdd-model-mapping` explains how LinkML elements become JSON-LD.

## Namespaces of the type service

```{toctree}
:maxdepth: 1
:glob:

type/*
```

## Namespaces of the unit service

```{toctree}
:maxdepth: 1
:glob:

unit/*
```

## Background

```{toctree}
:maxdepth: 1

mapping
```
