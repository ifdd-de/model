# Changelog

All notable changes to this template are documented in this file.

## [26.11.1] - 2026-11-14

### Added

- cookiecutter/cruft template for the model of an IFDD installation, with
  the variables `ifdd_model_prj_name`, `ifdd_model_prj_slug` and the shared
  `ifdd_schema_url`, `ifdd_type_url`, `ifdd_unit_url`; hooks validate the
  values and create `.env`.
- LinkML sources for the example namespaces of the schema, type and unit
  templates: base, product, function, location, organisation, the domains
  breaker.grid.example.ifdd.de and maintenance.ops.example.ifdd.de, the
  time-series vocabulary climate.ops.example.ifdd.de, units and quantity
  kinds.
- Generation of the JSON-LD contexts (`gen-jsonld-context` plus
  post-processing), the type vocabularies and the unit vocabularies, first
  with base URLs and compared by meaning with reference files, then for the
  URLs of the installation.
- `just publish`: copies the generated files into the content directories
  of schema, type and unit; never deletes.
- Documentation of the namespaces (Sphinx, English and German, PlantUML
  diagrams) and operating documentation of the instance.
- CI: template test with both fixtures, template update test, instance CI.
