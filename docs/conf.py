# Sphinx configuration of the model documentation (HTML).
#
# The pages are generated into output/docs/<lang> by `just docs`; this file
# is passed with `sphinx-build -c docs`. The settings follow
# json-ld-docu-gen (conf/base.py and the PlantUML part of conf/acme.py),
# without branding and without the LaTeX/PDF settings.
import os
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

project = "IFDD model"
copyright = "ifdd.de contributors"
master_doc = "index"

extensions = ["myst_parser", "sphinxcontrib.plantuml"]

myst_enable_extensions = [
    "deflist",
    "fieldlist",
    "colon_fence",
    "smartquotes",
    "replacements",
    "strikethrough",
    "substitution",
    "tasklist",
    "attrs_inline",
    "attrs_block",
]
myst_title_to_header = False
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", ".venv"]
html_theme = "alabaster"
# Wider body than the alabaster default (940px) for the term tables.
html_theme_options = {"page_width": "1200px"}

# -- PlantUML ----------------------------------------------------------------
# PlantUML runs locally (java -jar) while building; no diagram server.
# `just plantuml` downloads the pinned jar and sets IFDD_PLANTUML_JAR.
_jar = os.environ.get("IFDD_PLANTUML_JAR", "")
if not _jar or not Path(_jar).is_file():
    raise RuntimeError("IFDD_PLANTUML_JAR must point to plantuml.jar (run `just plantuml`)")
plantuml = (
    f"java -DPLANTUML_LIMIT_SIZE=8192 -jar {shlex.quote(_jar)}"
    f" -config {shlex.quote(str(ROOT / 'docs' / 'plantuml.cfg'))}"
)
plantuml_output_format = "svg_img"
plantuml_batch_size = 100
