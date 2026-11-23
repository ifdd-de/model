(ifdd-model-build-release)=
# Build and release

## Build

| Recipe | Does |
|---|---|
| `just json` | `just base` and `just relocate` |
| `just base` | contexts, vocabularies and units with the base URLs into `output/base` |
| `just relocate` | copies `output/base` to `output/<service>/json-ld/<version>` with the URLs from `.env` |
| `just compare` | compares `output/base` with `tests/reference` by meaning |
| `just docs` | MyST pages of every namespace and their HTML with PlantUML diagrams |
| `just check-docs` | same files, labels and headings in both languages, Sphinx build with `-W` |
| `just build` | all of the above, after `just clean` and `just lint` |

Every recipe prints the commands it runs. The page
{ref}`ifdd-model-linkml` explains what each step does with the sources.

## Changing the model

1. Edit a file in `src/linkml`.
2. Run `just json compare` and read the reported differences.
3. When they are wanted, run `just accept`: the output becomes the new
   reference. Commit sources and references together.
4. Run `just test` and `just docs`.

A new namespace is a new file; it gets a context only if it has a class
whose `class_uri` is `<prefix>:schema` in its own namespace.

## Release

The instance builds no image and no package; the web service uses the
upstream image `{{ cookiecutter.ifdd_nginx_image }}`. A release of the model is a
commit of the sources and references, followed by `just publish` and commits
in the content repositories. The versions of the tools are pinned in
`requirements.txt` and in the `justfile` (PlantUML); Dependabot proposes
updates of the Python packages.
