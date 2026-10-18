#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if [ -n "${BD_PYTHON:-}" ]; then
  bd_python=$BD_PYTHON
else
  bd_python=$(command -v python3.12 || command -v python3 || true)
fi
if [ -z "$bd_python" ] || [ ! -x "$bd_python" ]; then
  echo 'Python 3.12 fehlt / Python 3.12 is required. Setze / set BD_PYTHON.' >&2
  exit 2
fi
exec "$bd_python" scripts/launch.py "$@"
