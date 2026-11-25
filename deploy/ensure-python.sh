#!/usr/bin/env bash
set -euo pipefail

if [[ "$EUID" -ne 0 ]]; then
  echo "Der Python-Laufzeitinstaller muss als root laufen." >&2
  exit 1
fi

UPDATER_DIR="/opt/meeting-manager-updater"
UV_ENV="$UPDATER_DIR/uv-venv"
UV_BIN="$UV_ENV/bin/uv"
PYTHON_DIR="$UPDATER_DIR/python"
UV_VERSION="0.12.22"

install -d -o root -g root -m 0755 "$UPDATER_DIR" "$PYTHON_DIR"
if [[ ! -x "$UV_BIN" ]]; then
  echo "==> Installiere uv $UV_VERSION für die verwaltete Python-Laufzeit" >&2
  python3 -m venv "$UV_ENV"
  "$UV_ENV/bin/python" -m pip install --upgrade pip
  "$UV_ENV/bin/python" -m pip install "uv==$UV_VERSION"
fi

# uv downloads an isolated CPython build; the distribution's /usr/bin/python3
# remains unchanged. UV_PYTHON_INSTALL_DIR makes the runtime stable across
# root and meetingapp invocations.
UV_PYTHON_INSTALL_DIR="$PYTHON_DIR" "$UV_BIN" python install 3.12 --install-dir "$PYTHON_DIR" >&2
PYTHON_BIN="$(UV_PYTHON_INSTALL_DIR="$PYTHON_DIR" "$UV_BIN" python find 3.12)"
"$PYTHON_BIN" -c 'import sys; assert sys.version_info >= (3, 12) and sys.version_info < (3, 13)'
printf '%s\n' "$PYTHON_BIN"
