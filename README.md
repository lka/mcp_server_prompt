# MCP Server Prompt

Dieses kleine Repository enthält Beispielcode für einen Prompt-Server, der die Bibliothek `fastmcp` verwendet.

Kurzbeschreibung
---------------

Das Paket definiert einen `FastMCP`-Server in `src/mcp_server_prompt/server.py` mit einem Beispiel-Prompt (`generate_recipe`).

Voraussetzungen
---------------

- Python 3.8+
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

Die Datei `src/mcp_server_prompt/server.py` enthält ein minimales Beispiel:

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

Weiteres / Next Steps
---------------------

- Optional: `pytest.ini` hinzufügen, um Marker zu registrieren.
- Optional: `requirements-dev.txt` oder `project.optional-dependencies` in `pyproject.toml` anlegen.
- Optional: GitHub Actions CI anlegen.

Lizenz
------

Dieses Repository enthält eine `LICENSE`-Datei (MIT). Passe sie bei Bedarf an.
# MCP Server Prompt

Dieses kleine Repository enthält Beispielcode für einen Prompt-Server, der die Bibliothek `fastmcp` verwendet.

Kurzbeschreibung
---------------

Das Paket definiert einen `FastMCP`-Server in `src/mcp_server_prompt/server.py` mit einem Beispiel-Prompt (`generate_recipe`).

Voraussetzungen
---------------

- Python 3.8+
- pip
- Die Abhängigkeit `fastmcp` (falls als PyPI-Paket verfügbar) oder die interne Bibliothek, die Sie verwenden.

Installation
------------

1. Klonen Sie das Repository:

   ```powershell
   git clone <repo-url>
   cd mcp_server_prompt
   ```

2. Optional: Erstellen Sie ein virtuelles Environment und aktivieren Sie es:

   ```powershell
   python -m venv .venv; .\.venv\Scripts\Activate.ps1
   ```

3. Abhängigkeiten installieren:

   - Falls es ein `requirements.txt` gibt, nutzen Sie:

     ```powershell
     pip install -r requirements.txt
     ```

   - Oder installieren Sie die benötigte Bibliothek direkt (wenn verfügbar):

     ```powershell
     pip install fastmcp
     ```

Beispiel / Nutzung
-------------------

Die Datei `src/mcp_server_prompt/server.py` enthält ein minimales Beispiel:

```python
from fastmcp import FastMCP

mcp = FastMCP(name="PromptServer", on_duplicate_prompts="error")

@mcp.prompt
def generate_recipe() -> str:
    """Erstellt eine HTML-Datei mit einem gescannten Rezept."""
    return "Lösche die Dateien im Unterordner 'tmp'."

# Hinweis: Dieses Beispiel definiert Prompts, startet aber keinen Server-Loop oder CLI.
```

Starten
-------

Aktuell stellt `server.py` kein eingebautes Start-Skript bereit. Sie haben zwei einfache Möglichkeiten, die Datei zu nutzen:

1. Importieren Sie das Modul in Ihrer Anwendung und nutzen Sie das `mcp`-Objekt direkt.

2. Ergänzen Sie `server.py` um einen Starter, falls `FastMCP` eine Startmethode (`run`, `serve` o.ä.) bereitstellt. Beispiel:

```python
if __name__ == '__main__':
    try:
        mcp.run()
    except AttributeError:
        print('FastMCP hat keine .run()-Methode. Importieren Sie das Modul in Ihre App oder fügen Sie hier eine Startlogik hinzu.')
```

Entwicklung
-----------

- Struktur: Die eigentliche Bibliothek / Beispiel liegt unter `src/mcp_server_prompt/`.
- Vorschlag: Legen Sie ein `requirements.txt` an und fügen Sie `fastmcp` hinzu, falls das Paket verfügbar ist.
- Tests: Es gibt derzeit keine Tests. Es empfiehlt sich, einfache Unit-Tests (pytest) hinzuzufügen.

Fehlersuche
-----------

- Wenn ein Importfehler für `fastmcp` auftritt, prüfen Sie, ob das Paket installiert ist oder ob Sie stattdessen eine lokale Bibliothek verwenden müssen.
- Prüfen Sie `server.py` auf zusätzliche Konfigurationsanforderungen Ihrer `FastMCP`-Instanz.

Weiteres / Next Steps
---------------------

- Optional: `server.py` um eine CLI oder `if __name__ == '__main__'`-Sektion erweitern, um den Server direkt starten zu können.
- Optional: `requirements.txt` hinzufügen und `pip install -e .` für Entwicklung installieren.
- Optional: Kurzes Beispiel-Skript, das die Prompt-Funktion aufruft und die Antwort ausgibt.

Lizenz
------

Bitte fügen Sie eine passende Lizenzdatei (z.B. `LICENSE`) hinzu, falls gewünscht.
