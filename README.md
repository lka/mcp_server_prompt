# MCP Server Prompt

Dieses Repository enthält einen Prompt-Server, der die Bibliothek `fastmcp` verwendet.

Kurzbeschreibung
---------------

Das Paket definiert einen `FastMCP`-Server in `src/mcp_server_prompt/server.py` mit einem Prompt (`generate_recipe`).

Voraussetzungen
---------------

- Python 3.10+
- pip
- optional: virtuelle Umgebung (venv)

Installation
------------

1. Klonen Sie das Repository:

  ```powershell
  git clone <repo-url>
  cd mcp_server_prompt
  ```

2. Optional: Erstellen Sie ein virtuelles Environment und aktivieren Sie es:

  ```powershell
  python -m venv venv; .\venv\Scripts\Activate.ps1
  ```

3. Abhängigkeiten installieren:

  ```powershell
  pip install -r requirements.txt
  ```

4. Für die Entwicklung (editable install):

  ```powershell
  pip install -e .
  ```

Beispiel / Nutzung
-------------------

Die Datei `src/mcp_server_prompt/server.py` enthält einen FastMCP-Prompt-Server:

```python
from fastmcp import FastMCP

mcp = FastMCP(name="PromptServer", on_duplicate_prompts="error")

@mcp.prompt
def generate_recipe() -> str:
   """Erstellt eine HTML-Datei mit einem gescannten Rezept."""
   return "Lösche die Dateien im Unterordner 'tmp'."

def main() -> None:
   """Starter-Funktion: versucht mcp.run/serve/start aufzurufen."""

if __name__ == '__main__':
   main()
```

Entry-point / CLI
-----------------

Der Entry-point `promptServer` ist in `pyproject.toml` definiert und zeigt auf
`mcp_server_prompt.server:main`. Nach Installation per `pip install .` steht der
CLI-Befehl `promptServer` zur Verfügung. Alternativ kann das Modul direkt gestartet werden:

```powershell
python -m mcp_server_prompt.server
```

Tests
-----

Das Projekt enthält Unit-Tests und einen optionalen Integrationstest.

- Unit-Tests: `tests/test_server.py` verwendet ein Fake-`fastmcp`-Modul und läuft ohne
  zusätzliche Abhängigkeiten.
- Integrationstest: `tests/test_integration.py` läuft nur, wenn die Umgebungsvariable
  `RUN_INTEGRATION=1` gesetzt ist und `fastmcp` installiert ist.

Unit-Tests ausführen:

```powershell
python -m pytest -q
```

Integrationstest ausführen (wenn `fastmcp` installiert):

```powershell
#$env:RUN_INTEGRATION = '1'; python -m pytest -q -m integration
```

Hinweis: Die Integrationstests sind mit einem Pytest-Marker `integration` versehen. Um
Markerwarnungen zu vermeiden, kannst du eine `pytest.ini` mit den Markern anlegen.

Packaging & Veröffentlichung
----------------------------

1. Erstelle Build-Artefakte:

```powershell
pip install build
python -m build
```

2. Metadaten prüfen:

```powershell
pip install twine
python -m twine check dist/*
```

Continuous Integration (optional)
--------------------------------

Ein einfacher GitHub Actions Workflow kann bei jedem Push `pip install -e .` ausführen
und `pytest` starten. Wenn gewünscht, erstelle ich eine `.github/workflows/ci.yml` Datei
mit einem Basis-Workflow.

Fehlersuche
-----------

- ImportError für `fastmcp`: Stelle sicher, dass das Paket installiert ist oder nutze eine lokale
  Variante.
- Entry-point funktioniert nicht: prüfe, ob `pyproject.toml` den korrekten Pfad zur `main()`-Funktion enthält.

Lizenz
------

Dieses Repository enthält eine `LICENSE`-Datei (MIT). Passe sie bei Bedarf an.
