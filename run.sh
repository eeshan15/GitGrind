#!/bin/sh
# ---------------------------------------------------------------------------
# GitGrind - development launcher.
#
# This is for running from source while you are changing the code. For daily
# use, build the binary once and run that instead:
#
#     python3 tools/build_exe.py
#     ./dist/GitGrind
# ---------------------------------------------------------------------------
set -e
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "Python 3.8 or newer is required but was not found."
  exit 1
fi

echo "Starting GitGrind from source..."
exec "$PY" app.py "$@"
