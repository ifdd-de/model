"""Shared helpers of the instance tests.

The tests run `just` like a user would. They set every IFDD_MODEL_* variable
themselves, so a local .env of the instance does not change the result
(variables in the environment win over .env).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SETTINGS = ("SCHEMA_URL", "TYPE_URL", "UNIT_URL", "SCHEMA_TARGET", "TYPE_TARGET", "UNIT_TARGET", "CONTENT_DIR")


def just(*args: str, env: dict[str, str] | None = None, check: bool = True) -> subprocess.CompletedProcess:
    environ = dict(os.environ)
    environ.update({f"IFDD_MODEL_{name}": "" for name in SETTINGS})
    environ.update(env or {})
    return subprocess.run(["just", *args], cwd=ROOT, env=environ, check=check, capture_output=True, text=True)


@pytest.fixture(scope="session")
def built(tmp_path_factory) -> Path:
    """Output of `just json` with the base URLs."""
    out = tmp_path_factory.mktemp("out")
    just(f"out={out}", "json")
    return out
