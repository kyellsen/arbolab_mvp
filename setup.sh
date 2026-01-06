#!/usr/bin/env bash
set -euo pipefail

echo "=== arbolab: Initializing development environment ==="

# 1) Verify that uv is installed
if ! command -v uv >/dev/null 2>&1; then
    echo "Error: 'uv' is not installed."
    echo "Install uv with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 2) Optionally delete the old venv
if [ -d ".venv" ]; then
    echo "Existing .venv found."
    read -p "Delete the old .venv and recreate it? [y/N]: " answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        rm -rf .venv
        echo "Old .venv deleted."
    else
        echo "Aborted."
        exit 0
    fi
fi

# 3) Create a new venv
echo "Creating new uv venv ..."
uv venv --python 3.12 .venv

# 4) Sync workspace packages plus dev tools
echo "Installing workspace dependencies ..."
uv sync --all-packages --group dev

# 5) Done
echo "=== Setup complete ==="
echo
echo "Activate the environment:"
echo "    source .venv/bin/activate"
echo
echo "Run tests:"
echo "    uv run pytest --cov"
echo
echo "Ruff / linting:"
echo "    uv run ruff check --fix packages/"
echo
echo "Mypy type checking:"
echo "    uv run mypy packages/"
echo
echo "Good luck with your arbolab workspace!"
