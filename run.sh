#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
MIN_PYTHON_MAJOR=3
MIN_PYTHON_MINOR=11

# --- find a suitable Python -----------------------------------------------

find_python() {
    for cmd in python3 python; do
        if command -v "$cmd" &>/dev/null; then
            local ver
            ver="$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')" 2>/dev/null || continue
            local major minor
            major="${ver%%.*}"
            minor="${ver#*.}"
            if [ "$major" -ge "$MIN_PYTHON_MAJOR" ] && [ "$minor" -ge "$MIN_PYTHON_MINOR" ]; then
                echo "$cmd"
                return
            fi
        fi
    done
    return 1
}

# --- main ------------------------------------------------------------------

if [ $# -eq 0 ]; then
    echo "Usage: ./run.sh <character.json> [options]"
    echo ""
    echo "Examples:"
    echo "  ./run.sh wizard.json"
    echo "  ./run.sh wizard.json --theme dark --page-size a4"
    echo "  ./run.sh wizard.json -o sheets/my_wizard.html"
    echo ""
    echo "Run './run.sh --help' for all options."
    exit 1
fi

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    PYTHON="$(find_python)" || {
        echo "Error: Python $MIN_PYTHON_MAJOR.$MIN_PYTHON_MINOR+ is required but not found."
        echo ""
        echo "Install Python with one of:"
        echo "  macOS:  brew install python@3.13"
        echo "  Linux:  sudo apt install python3  (or use pyenv)"
        echo "  pyenv:  pyenv install 3.13"
        exit 1
    }
    echo "Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

# Install/update the package if needed
if [ ! -f "$VENV_DIR/.installed" ] || [ "$SCRIPT_DIR/pyproject.toml" -nt "$VENV_DIR/.installed" ]; then
    echo "Installing dependencies..."
    "$VENV_DIR/bin/python" -m pip install --quiet -e "$SCRIPT_DIR"
    touch "$VENV_DIR/.installed"
fi

# Run the tool
exec "$VENV_DIR/bin/p2e-character-one-pager" build "$@"
