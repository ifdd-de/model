"""Pre-generation hook: reject values that would render but not work.

cookiecutter renders this file with Jinja before running it.
Requires the standard library only.
"""

import re
import sys
from urllib.parse import urlsplit

URLS = {
    "ifdd_schema_url": "{{ cookiecutter.ifdd_schema_url }}",
    "ifdd_type_url": "{{ cookiecutter.ifdd_type_url }}",
    "ifdd_unit_url": "{{ cookiecutter.ifdd_unit_url }}",
}
VALUES = {
    "ifdd_model_prj_slug": """{{ cookiecutter.ifdd_model_prj_slug }}""",
    "ifdd_model_host": """{{ cookiecutter.ifdd_model_host }}""",
    "ifdd_model_dev_port": """{{ cookiecutter.ifdd_model_dev_port }}""",
    "ifdd_model_autoindex": """{{ cookiecutter.ifdd_model_autoindex }}""",
    "ifdd_model_cors_origin": """{{ cookiecutter.ifdd_model_cors_origin }}""",
    "ifdd_model_cache_max_age": """{{ cookiecutter.ifdd_model_cache_max_age }}""",
    "ifdd_model_memory_limit": """{{ cookiecutter.ifdd_model_memory_limit }}""",
    "ifdd_model_content_dir": """{{ cookiecutter.ifdd_model_content_dir }}""",
    "ifdd_nginx_image": """{{ cookiecutter.ifdd_nginx_image }}""",
    "ifdd_proxy_network": """{{ cookiecutter.ifdd_proxy_network }}""",
}

# (pattern, explanation); the same rules as in ifdd-de/schema
CHECKS = {
    # Directory name and name of the Traefik router: no dots.
    "ifdd_model_prj_slug": (r"[A-Za-z_][A-Za-z0-9_-]+", "letters, digits, _ and -, not starting with a digit or -"),
    "ifdd_model_host": (r"[A-Za-z0-9]([A-Za-z0-9.-]*[A-Za-z0-9])?", "a host name"),
    "ifdd_model_dev_port": (r"[0-9]{1,5}", "a port number"),
    "ifdd_model_autoindex": (r"[yn]", "y or n"),
    "ifdd_model_cors_origin": (r"\*|https?://[A-Za-z0-9.-]+(:[0-9]+)?", "* or one origin such as https://ui.example.org"),
    "ifdd_model_cache_max_age": (r"[0-9]+", "seconds, 0 for no-cache"),
    "ifdd_model_memory_limit": (r"[0-9]+[bkmgBKMG]?", "a compose memory limit such as 128M"),
    # compose reads a value without ./, ../ or / as a volume name.
    "ifdd_model_content_dir": (r"(\.{1,2}/|/)[^\s'\"$]*", "a path starting with ./, ../ or /"),
    "ifdd_nginx_image": (r"\S+", "an image reference without spaces"),
    "ifdd_proxy_network": (r"[A-Za-z0-9][A-Za-z0-9_.-]*", "a Docker network name"),
}

errors = []
for name, (pattern, explanation) in CHECKS.items():
    if not re.fullmatch(pattern, VALUES[name]):
        errors.append(f"{name}: expected {explanation}: {VALUES[name]!r}")
if re.fullmatch(r"[0-9]{1,5}", VALUES["ifdd_model_dev_port"]) and not 1 <= int(VALUES["ifdd_model_dev_port"]) <= 65535:
    errors.append(f"ifdd_model_dev_port: outside 1-65535: {VALUES['ifdd_model_dev_port']}")
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
