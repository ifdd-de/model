"""Pre-generation hook: reject values that would render but not work.

cookiecutter renders this file with Jinja before running it.
Requires the standard library only.
"""

import re
import sys
from urllib.parse import urlsplit

SLUG = "{{ cookiecutter.ifdd_model_prj_slug }}"
URLS = {
    "ifdd_schema_url": "{{ cookiecutter.ifdd_schema_url }}",
    "ifdd_type_url": "{{ cookiecutter.ifdd_type_url }}",
    "ifdd_unit_url": "{{ cookiecutter.ifdd_unit_url }}",
}

errors = []
if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", SLUG):
    errors.append(f"ifdd_model_prj_slug: letters, digits, '.', '_', '-' only: {SLUG!r}")
for name, url in URLS.items():
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        errors.append(f"{name}: must start with http:// or https:// and name a host: {url!r}")
    elif url.endswith("/") or parts.query or parts.fragment or re.search(r"[\s'\"]", url):
        errors.append(f"{name}: no trailing slash, query, fragment, spaces or quotes: {url!r}")
    elif not parts.path.strip("/"):
        errors.append(f"{name}: needs a path with the version, e.g. https://type/v1: {url!r}")

if errors:
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    sys.exit(1)
