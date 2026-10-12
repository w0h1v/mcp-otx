"""Fail if an sdist contains local-only files (secrets, venvs, logs, workspace files)."""

import re
import sys
import tarfile

FORBIDDEN = re.compile(
    r"(^|/)("
    r"\.env(?!\.example$)[^/]*$"  # .env, .env.local, ... but not .env.example
    r"|\.venv/"
    r"|logs/"
    r"|project\.(json|ya?ml)$"
    r"|\.mcpregistry_"
    r")"
)

paths = sys.argv[1:]
if not paths:
    sys.exit("usage: check_sdist.py DIST.tar.gz [...]")

bad = []
for path in paths:
    with tarfile.open(path) as tar:
        names = tar.getnames()
    print(f"{path}: {len(names)} entries")
    bad += [f"{path}: {name}" for name in names if FORBIDDEN.search(name)]

if bad:
    print("::error::sdist contains local files:\n" + "\n".join(bad))
    sys.exit(1)
print("sdist contents OK")
