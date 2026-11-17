# Build the IFDD JSON-LD files and docs from the LinkML sources.
# `just` lists the recipes. Every recipe shows the plain CLI calls it runs,
# so each step can also be run by hand.

set shell := ["bash", "-euo", "pipefail", "-c"]

src := "src/linkml"
out := "output"

# PlantUML runs locally while building the docs (Java needed, Graphviz for the layout).
plantuml_version := "1.2026.10"
plantuml_url := "https://github.com/plantuml/plantuml/releases/download/v" + plantuml_version + "/plantuml-" + plantuml_version + ".jar"
plantuml_sha256 := "e9bc9e6b2eb715e8c0c929f3dcb5fc1923be13f37599b09c293c66d354e88686"
plantuml_jar := justfile_directory() / ".cache" / "plantuml-" + plantuml_version + ".jar"

_default:
    @just --list --unsorted --justfile {{ justfile() }}

# Everything: clean, lint, JSON-LD, compare with the references, docs and their check
build: clean lint json compare docs check-docs

# Remove the output directory
clean:
    rm -rf {{ out }}

# Check the LinkML sources
lint:
    linkml-lint --config .linkmllint.yaml {{ src }}

# Generate contexts, vocabularies and units
json: contexts vocabularies units

# JSON-LD contexts (schema service): gen-jsonld-context, then the IFDD post-processing
contexts:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p {{ out }}/raw {{ out }}/schema/json-ld/v1
    for f in {{ src }}/type/*.yaml; do
        name=$(basename "$f" .yaml)
        if ! python -m ifdd_model.schema has-context "$f"; then
            echo "skip $name (no class, vocabulary only)"
            continue
        fi
        set -x
        gen-jsonld-context --log_level ERROR --no-metadata --fix-multivalue-containers --xsd-anyuri-as-iri \
            "$f" > "{{ out }}/raw/$name.jsonld"
        python -m ifdd_model.context "$f" "{{ out }}/raw/$name.jsonld" "{{ out }}/schema/json-ld/v1/$name.jsonld"
        { set +x; } 2>/dev/null
    done

# Vocabularies (type service)
vocabularies:
    #!/usr/bin/env bash
    set -euo pipefail
    for f in {{ src }}/type/*.yaml; do
        name=$(basename "$f" .yaml)
        set -x
        python -m ifdd_model.vocab "$f" "{{ out }}/type/json-ld/v1/$name/index.jsonld"
        { set +x; } 2>/dev/null
    done

# Units and quantity kinds (unit service)
units:
    #!/usr/bin/env bash
    set -euo pipefail
    for f in {{ src }}/unit/*.yaml; do
        name=$(basename "$f" .yaml)
        set -x
        python -m ifdd_model.vocab "$f" "{{ out }}/unit/json-ld/v1/$name/index.jsonld" --units {{ src }}/unit/*.yaml
        { set +x; } 2>/dev/null
    done

# Compare the generated JSON-LD with the reference files by meaning
compare:
    #!/usr/bin/env bash
    set -euo pipefail
    status=0
    for ref in $(cd tests/reference && find . -name '*.jsonld' | sort); do
        service=${ref#./}; service=${service%%/*}
        rel=${ref#./$service/}
        gen="{{ out }}/$service/json-ld/$rel"
        if [ ! -f "$gen" ]; then echo "MISSING $gen"; status=1; continue; fi
        if python -m ifdd_model.compare "$gen" "tests/reference/$service/$rel"; then
            echo "same    $gen"
        else
            echo "DIFFERS $gen"; status=1
        fi
    done
    exit $status

# Run the tests
test:
    python -m pytest -q tests

# Download the pinned PlantUML jar into .cache/ and check its SHA-256
plantuml:
    #!/usr/bin/env bash
    set -euo pipefail
    jar="{{ plantuml_jar }}"
    if [ ! -f "$jar" ]; then
        mkdir -p "$(dirname "$jar")"
        set -x
        curl -fsSL -o "$jar.part" "{{ plantuml_url }}"
        { set +x; } 2>/dev/null
        mv "$jar.part" "$jar"
    fi
    python -c 'import hashlib, sys; h = hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest(); sys.exit(0 if h == sys.argv[2] else f"SHA-256 mismatch for {sys.argv[1]}: {h}")' "$jar" "{{ plantuml_sha256 }}"
    echo "PlantUML {{ plantuml_version }}: $jar"

# MyST pages in English and German, one per namespace (gen-doc with own templates)
docs-pages:
    #!/usr/bin/env bash
    set -euo pipefail
    for lang in en de; do
        mkdir -p "{{ out }}/docs/$lang"
        cp docs/src/$lang/*.md "{{ out }}/docs/$lang/"
        for service in type unit; do
            mkdir -p "{{ out }}/docs/$lang/$service"
            for f in {{ src }}/$service/*.yaml; do
                name=$(basename "$f" .yaml)
                tmp="{{ out }}/docgen/$lang/$service/$name"
                set -x
                gen-doc --log_level ERROR --dialect myst --template-directory "docs/templates/$lang" \
                    --diagram-type plantuml_class_diagram --index-name ifdd_page -d "$tmp" "$f" > /dev/null
                { set +x; } 2>/dev/null
                cp "$tmp/ifdd_page.md" "{{ out }}/docs/$lang/$service/$name.md"
            done
        done
    done

# Sphinx docs in English and German (HTML with PlantUML diagrams)
docs: docs-pages plantuml
    #!/usr/bin/env bash
    set -euo pipefail
    for lang in en de; do
        set -x
        IFDD_PLANTUML_JAR="{{ plantuml_jar }}" sphinx-build -q -W -c docs -D language=$lang -b html \
            "{{ out }}/docs/$lang" "{{ out }}/docs/_build/$lang"
        { set +x; } 2>/dev/null
    done
    echo "HTML: {{ out }}/docs/_build/en/index.html, {{ out }}/docs/_build/de/index.html"

# Check the docs like the IFDD templates do (same files, labels, headings; sphinx -W)
check-docs: plantuml
    IFDD_PLANTUML_JAR="{{ plantuml_jar }}" python tests/check_docs.py {{ out }} --prefix ifdd-model-
