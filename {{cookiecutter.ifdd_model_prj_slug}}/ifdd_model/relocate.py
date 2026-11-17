"""Move generated files from the base URLs to the URLs of this installation.

The LinkML sources and the reference files always use the base URLs
``https://schema/v1``, ``https://type/v1`` and ``https://unit/v1``. The build
first writes everything with these URLs (``output/base``), compares it with
the references, and then copies it to the URLs of the installation:

* every occurrence of ``<base URL>/`` in a file becomes ``<URL>/``;
* the files of a service land below ``json-ld/<path of its URL>``, the way
  nginx serves the content directory (``https://type/v2`` -> ``json-ld/v2``).

The URLs come from the environment (``.env``, loaded by ``just``):
``IFDD_MODEL_SCHEMA_URL``, ``IFDD_MODEL_TYPE_URL``, ``IFDD_MODEL_UNIT_URL``.
Unset means the base URL.

Usage:
  ``python -m ifdd_model.relocate copy SRC DST``  copy a tree, replacing URLs
  ``python -m ifdd_model.relocate path SERVICE``  print the URL path of a service, e.g. ``v1``
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from urllib.parse import urlsplit

BASE_URLS = {
    "schema": "https://schema/v1",
    "type": "https://type/v1",
    "unit": "https://unit/v1",
}
TEXT_SUFFIXES = {".jsonld", ".json", ".md"}


def check_url(service: str, url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise ValueError(f"{service}: URL must start with http:// or https:// and name a host: {url!r}")
    if url.endswith("/") or parts.query or parts.fragment or any(c.isspace() for c in url):
        raise ValueError(f"{service}: URL without trailing slash, query, fragment or spaces expected: {url!r}")
    if not parts.path.strip("/"):
        raise ValueError(f"{service}: URL needs a path (the version), e.g. https://type/v1: {url!r}")
    return url


def urls(environ: dict[str, str] | None = None) -> dict[str, str]:
    """Target URL per service, from the environment or the base URL."""
    env = os.environ if environ is None else environ
    return {
        service: check_url(service, env.get(f"IFDD_MODEL_{service.upper()}_URL") or base)
        for service, base in BASE_URLS.items()
    }


def replace_urls(text: str, targets: dict[str, str]) -> str:
    for service, base in BASE_URLS.items():
        text = text.replace(base + "/", targets[service] + "/")
    return text


def url_path(url: str) -> str:
    return urlsplit(url).path.strip("/")


def copy_tree(src: Path, dst: Path, targets: dict[str, str]) -> int:
    count = 0
    for path in sorted(p for p in src.rglob("*") if p.is_file()):
        out = dst / path.relative_to(src)
        out.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix in TEXT_SUFFIXES:
            out.write_text(replace_urls(path.read_text(encoding="utf-8"), targets), encoding="utf-8")
        else:
            shutil.copyfile(path, out)
        count += 1
    return count


def main(argv: list[str]) -> int:
    try:
        targets = urls()
        if len(argv) == 3 and argv[0] == "copy":
            copy_tree(Path(argv[1]), Path(argv[2]), targets)
            return 0
        if len(argv) == 2 and argv[0] == "path" and argv[1] in BASE_URLS:
            print(url_path(targets[argv[1]]))
            return 0
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(__doc__.strip().split("Usage:")[1].rstrip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
