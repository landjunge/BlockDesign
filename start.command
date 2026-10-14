#!/bin/zsh
set -eu
cd "${0:A:h}"
bd_python=/usr/local/bin/python3.12
if [[ ! -x "$bd_python" ]]; then
  bd_python=/Users/landjunge/threaddesk/.venv/bin/python
fi
if [[ "${1:-}" == "--setup" ]]; then
  exec "$bd_python" scripts/host.py setup
fi
if [[ ! -f .runtime/binding.json ]]; then
  "$bd_python" scripts/host.py setup
fi
exec "$bd_python" scripts/server.py "$@"
