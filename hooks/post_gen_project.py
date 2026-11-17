"""Post-generation hook: create .env from dotenv.dist.

An existing .env is never touched (it is on the skip list of the instance).
The file holds no secrets; it is created with mode 0600 like in the other
IFDD templates. Requires the standard library only.
"""

import os
import shutil
from pathlib import Path

source = Path("dotenv.dist")
target = Path(".env")
if not target.exists():
    shutil.copyfile(source, target)
    os.chmod(target, 0o600)
