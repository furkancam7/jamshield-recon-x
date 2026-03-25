#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
REQUIRED_MODULES=("yaml")

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python interpreter '$PYTHON_BIN' not found." >&2
  echo "Set PYTHON_BIN to a valid interpreter, for example: PYTHON_BIN=python3.13" >&2
  exit 1
fi

PYTHONPATH_PREFIX="$ROOT_DIR/src"
case ":${PYTHONPATH:-}:" in
  *":$PYTHONPATH_PREFIX:"*) ;;
  *)
    export PYTHONPATH="$PYTHONPATH_PREFIX${PYTHONPATH:+:$PYTHONPATH}"
    ;;
esac

for module_name in "${REQUIRED_MODULES[@]}"; do
  if ! "$PYTHON_BIN" -c "import ${module_name}" >/dev/null 2>&1; then
    echo "Missing Python dependency '${module_name}'." >&2
    echo "Install with: $PYTHON_BIN -m pip install pyyaml" >&2
    exit 1
  fi
done

"$PYTHON_BIN" --version
echo "PYTHON_BIN=$PYTHON_BIN"
echo "PYTHONPATH=$PYTHONPATH"
echo "Dependency check passed: pyyaml"
echo "JamShield Recon-X Sim bootstrap complete."
