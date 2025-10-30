# -*- coding: utf-8 -*-
"""MCP Prompt Server für Rezept-Extraktion aus PDFs."""
from fastmcp import FastMCP

# from fastmcp.prompts.prompt import Message, PromptMessage, TextContent

mcp = FastMCP(name="PromptServer", on_duplicate_prompts="error")


# Basic prompt returning a string (converted to user message automatically)
@mcp.prompt
def generate_recipe() -> str:
    """Erstellt eine HTML-Datei mit einem gescannten Rezept aus einer PDF."""
    return """
# Rezept-Extraktion aus PDF

## Ziel
Extrahiere ein Rezept aus einer PDF-Datei und erstelle eine formatierte HTML-Seite.

## Arbeitsverzeichnisse
- **Temporaere Dateien**: `tmp/`
- **Eingabe**: `Eingang/` (enthaelt PDF-Dateien)
- **Ausgabe**: `Ausgang/` (HTML-Dateien und Bilder)
- **Template**: `Ausgang/Template.html`

## Schritt-fuer-Schritt Anleitung

### 1. PDF-Analyse
- Oeffne die erste PDF-Datei aus dem Verzeichnis `Eingang/`
- Zeige die PDF-Seite(n) an
- Lasse mich interaktiv die Regionen auswaehlen fuer:
  - Rezepttext (Zutaten, Zubereitung, etc.)
  - Rezeptbild (Foto des fertigen Gerichts)

### 2. Text-Extraktion
- Falls kein Text extrahiert wurde, fuehre OCR auf den ausgewaehlten Textregionen durch
- Strukturiere den extrahierten Text nach:
  - Rezeptname
  - Zutaten
  - Zubereitung
  - Weitere Metadaten (Portionen, Zeit, Schwierigkeit)

### 3. Bild-Verarbeitung
- Finde das Rezeptbild aus der ausgewaehlten Region im Ordner `tmp/`
- Bewege das Bild mit `move_file` nach: `Ausgang/Images/<rezeptname>.png`
- Verwende UTF-8 sichere Dateinamen (ersetze Umlaute):
- Entferne oder ersetze Sonderzeichen durch Unterstriche

### 4. HTML-Generierung
- Lade das Template aus `Ausgang/Template.html`
- Verwende alle im Template definierten TAGs (wie <TITLE>, <INGREDIENTS>, <INSTRUCTIONS>, etc.)
- Fuelle die TAGs mit den extrahierten Daten
- Referenziere das Bild mit relativem Pfad: `Images/<bildname>.png`
- Stelle sicher, dass alle Umlaute und Sonderzeichen im HTML korrekt als UTF-8 kodiert sind
- Speichere die HTML-Datei als: `Ausgang/<rezeptname>.html`

### 5. Index aktualisieren
- Oeffne die Datei `Ausgang/index.html`
- Fuege einen neuen Link zur erstellten Rezeptseite hinzu
- Sortiere die Links alphabetisch (falls moeglich)

### 6. Qualitaetspruefung
- Oeffne im Edge-Browser:
  - Die Original-PDF aus `Eingang/`
  - Die neu erstellte HTML-Datei aus `Ausgang/`
- Vergleiche visuell, ob alle Informationen korrekt uebertragen wurden

## Fehlerbehandlung
- Falls keine PDF im `Eingang/` Verzeichnis vorhanden ist: Melde dies und beende
- Falls Template.html fehlt: Melde dies und frage nach einem Basis-Template
- Falls OCR fehlschlaegt: Melde die betroffenen Regionen und biete manuelle Eingabe an
"""


def main() -> None:
    """Versuche, den FastMCP-Server zu starten.

    Diese Funktion kapselt die Logik, die beim direkten Start des Moduls
    ausgeführt werden soll. Sie versucht, eine der üblichen Starter-Methoden
    (`run`, `serve`, `start`) am `mcp`-Objekt aufzurufen.
    """
    # Versuche, den Server zu starten, falls FastMCP eine solche
    # Methode bereitstellt.
    for starter in ("run", "serve", "start"):
        fn = getattr(mcp, starter, None)
        if callable(fn):
            print(f"Starte FastMCP mit mcp.{starter}()...")
            try:
                fn()
            except Exception as e:
                print(f"Fehler beim Starten von mcp.{starter}(): {e}")
            break
    else:
        print("Keine Startmethode an mcp gefunden.")
        print("Importiere dieses Modul in deine Anwendung.")
        print("Oder füge hier eigene Startlogik hinzu.")


if __name__ == "__main__":
    main()
