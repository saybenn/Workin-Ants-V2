#!/usr/bin/env bash
# Install the exact Linux CPython 3.12 PostgreSQL parser used in Cloud F0.
set -euo pipefail
umask 077
test "$(uname -s)" = Linux
test "$(uname -m)" = x86_64
python -c 'import sys; assert sys.implementation.name == "cpython" and sys.version_info[:2] == (3, 12)'
stage=$(mktemp -d /workspace/scratch/workin-ants-f0-parser.XXXXXX)
printf '%s\n' 'pglast==7.21 --hash=sha256:2006f89ab517700e33c9f81d3dee6ae2ce0888b91e2e0be59d008fb37e8cc2a0' > "$stage/requirements.txt"
python -m pip --disable-pip-version-check --no-cache-dir install --require-hashes --only-binary=:all: \
  --no-deps --no-compile --target "$stage/python" -r "$stage/requirements.txt"
PYTHONPATH="$stage/python" python -B - <<'PY'
from hashlib import sha256
from pathlib import Path
import pglast
from pglast import parser

assert pglast.__version__ == "v7.21"
assert sha256(Path(pglast.__file__).read_bytes()).hexdigest() == "e085f1a529eedc4e9ddeecbd406255ed8580f4cef00b13a33e7fd056d8374084"
assert sha256(Path(parser.__file__).read_bytes()).hexdigest() == "c2ab2648a942b314ffcd7ab38f25c052ca08adc323fa556b0ed68b727320e711"
PY
printf 'export PYTHONPATH=%q\n' "$stage/python"
