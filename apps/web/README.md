# Arbolab SaaS Frontend

This directory contains the frontend and authentication layer for Arbolab SaaS.

## Entwicklungsumgebung aktivieren

Bevor du das Frontend startest, stelle sicher, dass du dich im Root-Verzeichnis des Projekts befindest und die Umgebung eingerichtet hast:

```bash
# Projekt-Setup (einmalig)
./setup.sh

# Umgebung aktivieren
source .venv/bin/activate
```

## Frontend starten

Um den Entwicklungs-Server zu starten, führe folgenden Befehl aus dem **Projekt-Root** aus:

```bash
uv run uvicorn apps.web.main:app --reload --reload-exclude "apps/web/tests/*" --reload-exclude "packages/*"
```

## Aufrufen

Sobald der Server läuft, kannst du das Frontend im Browser unter folgender Adresse aufrufen:

[http://127.0.0.1:8000](http://127.0.0.1:8000)

Standardmäßig wirst du zur Login-Seite weitergeleitet, da noch kein Benutzer angemeldet ist.

## Fehlersuche (Troubleshooting)

### Port bereits belegt (Address already in use)

Falls du die Fehlermeldung `[Errno 98] Address already in use` erhältst, ist Port 8000 bereits von einem anderen Prozess belegt.

**Lösung 1: Anderen Port verwenden**
Du kannst das Frontend einfach auf einem anderen Port starten (z.B. 8001):
```bash
uv run uvicorn apps.web.main:app --reload --reload-exclude "apps/web/tests/*" --reload-exclude "packages/*" --port 8001
```

**Lösung 2: Prozess auf Port 8000 finden und beenden**
```bash
# Prozess finden (PID steht in der letzten Spalte)
lsof -i :8000

# Prozess beenden (ersetze <PID> durch die gefundene Nummer)
kill -9 <PID>
```
