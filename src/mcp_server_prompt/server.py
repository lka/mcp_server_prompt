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
- **Temporäre Dateien**: `tmp/`
- **Eingabe**: `Eingang/` (enthält PDF-Dateien)
- **Ausgabe**: `Ausgang/` (HTML-Dateien und Bilder)
- **Template**: `Ausgang/Template.html`

## Schritt-für-Schritt Anleitung

### 1. PDF-Analyse
- Öffne die erste PDF-Datei aus dem Verzeichnis `Eingang/`
- Zeige die PDF-Seite(n) an
- Lasse mich interaktiv die Regionen auswählen für:
  - Rezepttext (Zutaten, Zubereitung, etc.)
  - Rezeptbild (Foto des fertigen Gerichts)

### 2. Text-Extraktion
- Führe OCR auf den ausgewählten Textregionen durch
- Strukturiere den extrahierten Text nach:
  - Rezeptname
  - Zutaten
  - Zubereitung
  - Weitere Metadaten (Portionen, Zeit, Schwierigkeit)

### 3. Bild-Verarbeitung
- Extrahiere das Rezeptbild aus der ausgewählten Region
- Speichere das Bild unter: `Ausgang/Images/<rezeptname>.jpg`
- Verwende UTF-8 sichere Dateinamen (ersetze Umlaute: ä→ae, ö→oe, ü→ue, ß→ss)
- Entferne oder ersetze Sonderzeichen durch Unterstriche

### 4. HTML-Generierung
- Lade das Template aus `Ausgang/Template.html`
- Verwende alle im Template definierten TAGs (wie <TITLE>, <INGREDIENTS>, <INSTRUCTIONS>, etc.)
- Fülle die TAGs mit den extrahierten Daten
- Referenziere das Bild mit relativem Pfad: `Images/<bildname>.jpg`
- Stelle sicher, dass alle Umlaute und Sonderzeichen im HTML korrekt als UTF-8 kodiert sind
- Speichere die HTML-Datei als: `Ausgang/<rezeptname>.html`

### 5. Index aktualisieren
- Öffne die Datei `Ausgang/index.html`
- Füge einen neuen Link zur erstellten Rezeptseite hinzu
- Sortiere die Links alphabetisch (falls möglich)

### 6. Qualitätsprüfung
- Öffne im Edge-Browser:
  - Die Original-PDF aus `Eingang/`
  - Die neu erstellte HTML-Datei aus `Ausgang/`
- Vergleiche visuell, ob alle Informationen korrekt übertragen wurden

## Fehlerbehandlung
- Falls keine PDF im `Eingang/` Verzeichnis vorhanden ist: Melde dies und beende
- Falls Template.html fehlt: Melde dies und frage nach einem Basis-Template
- Falls OCR fehlschlägt: Melde die betroffenen Regionen und biete manuelle Eingabe an
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
