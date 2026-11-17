# Sphinx configuration for tests/check_docs.py (a copy of the check of the
# IFDD templates). It uses exactly the settings of docs/conf.py, so the check
# builds the pages as `just docs` does. __file__ is set to docs/conf.py so
# that its relative paths (plantuml.cfg) resolve there.
from pathlib import Path

__file__ = str(Path(__file__).resolve().parents[2] / "docs" / "conf.py")
exec(Path(__file__).read_text(encoding="utf-8"))  # noqa: S102 - own file in this repository
