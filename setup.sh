#!/usr/bin/env bash
set -euo pipefail

echo "=== arbolab: Initializing/Updating development environment ==="

# 1) Verify that uv is installed
if ! command -v uv >/dev/null 2>&1; then
    echo "Error: 'uv' is not installed."
    echo "Install uv with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 2) Handle .venv recreation
if [ -d ".venv" ]; then
    echo "Existing .venv found."
    read -p "Delete the old .venv and recreate it? (Recommended if dependencies changed significantly) [y/N]: " answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        rm -rf .venv
        echo "Old .venv deleted."
        uv venv --python 3.12 .venv
    fi
else
    echo "Creating new uv venv ..."
    uv venv --python 3.12 .venv
fi

# 3) Sync workspace packages plus dev tools
echo "Syncing workspace dependencies and dev tools ..."
uv sync --all-packages --all-extras --group dev

# 4) Done
echo "=== Setup/Sync complete ==="
echo
echo "Activate the environment:"
echo "    source .venv/bin/activate"
echo
echo "To run all quality checks (Linter, Type Checker, Tests):"
echo "    cat ci.txt | bash"
echo
echo "Good luck with your arbolab workspace!"
