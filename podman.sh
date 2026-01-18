#!/usr/bin/env bash
set -euo pipefail

# Lade Pfade aus der .env Datei
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found. Please create one."
    exit 1
fi

echo "=== ArboLab Reset ==="
echo "Target Workspace: $ARBO_WORKSPACE_DIR"

# Sicherheitsabfrage
if [[ ! "$ARBO_WORKSPACE_DIR" == *"/dev_workspaces/"* ]]; then
    echo "SAFETY STOP: Workspace path seems wrong. Must contain '/dev_workspaces/'."
    exit 1
fi

echo "Stopping containers..."
# Try podman-compose, fallback to docker compose
if command -v podman-compose &> /dev/null; then
    COMPOSE_CMD="podman-compose"
else
    COMPOSE_CMD="docker compose"
fi

$COMPOSE_CMD down

echo "Cleaning Workspace Data (DB & Files)..."
# Lösche Inhalte, behalte aber die Ordner-Struktur
sudo rm -rf "$ARBO_WORKSPACE_DIR/data"/*
sudo rm -rf "$ARBO_WORKSPACE_DIR/postgres"/*

# Stelle sicher, dass Ordner existieren (falls rm zu aggressiv war)
mkdir -p "$ARBO_WORKSPACE_DIR/data"
mkdir -p "$ARBO_WORKSPACE_DIR/postgres"

echo "Rebuilding & Starting (Dev Mode)..."
$COMPOSE_CMD -f compose.yaml up --build -d

echo "Done. App running at http://localhost:8000"
