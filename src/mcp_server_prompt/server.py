# -*- coding: utf-8 -*-
"""MCP Prompt Server für Rezept-Extraktion aus PDFs."""
from fastmcp import FastMCP

# from fastmcp.prompts.prompt import Message, PromptMessage, TextContent

mcp = FastMCP(name="PromptServer", on_duplicate_prompts="error")


# Basic prompt returning a string (converted to user message automatically)
@mcp.prompt
def generate_recipe() -> str:
    """Erstellt eine HTML-Datei mit einem gescannten Rezept aus einer PDF."""
    return r"""
# Rezept-Extraktion aus PDF - Workflow mit recipe-index Konnektor (v2)

## Ziel
Extrahiere Rezepte aus PDF-Dateien und erstelle formatierte HTML-Seiten mit automatischer OCR-Unterstützung und automatisierter Index-Verwaltung.

## Arbeitsverzeichnisse
- **tmp/**: Temporäre Dateien (wird vom image-selector beim Start automatisch geleert!)
- **Eingang/**: PDF-Dateien (bleiben erhalten - können mehrere Rezepte enthalten!)
- **Ausgang/**: HTML-Dateien und Bilder
- **Ausgang/Images/**: Rezeptbilder
- **Ausgang/Template.html**: HTML-Vorlage

## Verfügbare Konnektoren
- **filesystem**: Datei-/Verzeichnis-Operationen (list, read, save, append, delete, move, edit)
- **image-selector**: Interaktive Region-Auswahl mit automatischem OCR
- **recipe-index**: Automatisierte Index-Verwaltung
  - add_recipe_to_index: Fügt Rezept hinzu (sortiert, kategorisiert, aktualisiert Counter)
  - check_duplicate_recipe: Prüft ob Rezept existiert
  - suggest_recipe_category: Schlägt Kategorie vor
  - list_index_categories: Listet alle Kategorien
  - count_recipes: Zählt Rezepte gesamt und pro Kategorie
  - list_all_recipes: Listet alle Rezepte (optional gefiltert)
  - remove_recipe_from_index: Entfernt Rezept
- **windows-launcher**: Dateien in Microsoft Edge öffnen
- **tesseract**: OCR-Fallback

---

## Workflow-Logik (Ein PDF pro Durchlauf)

### Ablauf:
```
1. Wähle EIN PDF
2. Öffne image-selector für dieses PDF
   → tmp/ wird automatisch geleert!
3. Markiere ALLE Regionen für EIN Rezept
4. Alle Text-Regionen → automatisch konkateniert
5. Erstes Foto → automatisch verwendet
6. HTML erstellt, Index aktualisiert, Protokolliert
7. Für nächstes Rezept: Zurück zu Schritt 1
   → tmp/ wird wieder automatisch geleert
```

### Dateimanagement:
- tmp/ wird vom image-selector beim Start automatisch geleert
- Pro PDF-Durchlauf: Nur Regionen aus diesem einen PDF
- Keine manuelle Bereinigung nötig
- Alle gefundenen Text-Regionen werden automatisch verwendet
- Erstes gefundenes Foto wird automatisch verwendet

### Mehrere Rezepte aus einem PDF:
Falls ein PDF mehrere Rezepte enthält:
1. Erster Durchlauf: Markiere nur Regionen für Rezept 1
2. Nach Abschluss: Wiederholen
3. Zweiter Durchlauf: Gleiches PDF öffnen
   → tmp/ wird automatisch geleert
   → Markiere Regionen für Rezept 2
4. Wiederholen für weitere Rezepte

---

## Workflow

### 0. Vorbereitung

**Aktionen**:
1. Verwende `filesystem:list_directory` um Verzeichnisse zu prüfen: tmp/, Eingang/, Ausgang/, Ausgang/Images/

2. Liste verfügbare PDFs:
   ```
   filesystem:list_directory in "Eingang/"
   Sortiere PDFs alphabetisch
   Zeige nummerierte Liste
   ```

3. Status-Ausgabe:
   ```
   recipe-index:count_recipes

   📋 Status:
   • X PDF(s) gefunden: [Liste]
   • Template.html vorhanden: Ja/Nein
   • Anzahl Rezepte in Index: X (aus Y Kategorien)
   ```

4. Prüfe ob `Ausgang/Template.html` existiert - falls NEIN: Erstelle Basis-Template

---

### 1. PDF-Auswahl

**Aktionen**:
1. Bei 1 PDF: Automatisch auswählen
2. Bei mehreren PDFs: Frage Nutzer welches PDF

3. Merke PDF-Namen: `current_pdf_name`

---

### 2. PDF-Analyse mit image-selector

**Aktionen**:
1. Verwende `image-selector:select_image_regions`:
   ```
   Parameter: image_path: "Eingang/<current_pdf_name>.pdf"
   ```

2. Instruktionen für Nutzer:
   ```
   Markiere ALLE Regionen für EIN Rezept:
   - Als 'text': Rezeptname, Zutaten, Zubereitung, Metadaten, Tipps
   - Als 'foto': Hauptbild
   ```

3. Nach Abschluss automatisch erstellt in tmp/:
   - `<pdf-name>_<timestamp>_region01_text.txt` (OCR durchgeführt)
   - `<pdf-name>_<timestamp>_region02_text.txt` (weitere Textregionen)
   - `<pdf-name>_<timestamp>_regionXX_foto.png` (Bildregion)

4. Validierung: `image-selector:list_exported_regions`

**Wichtig**: tmp/ wurde beim Start des image-selectors automatisch geleert!

---

### 3. Text-Extraktion

**Aktionen**:

1. **Liste ALLE Text-Regionen** aus tmp/:
   ```
   filesystem:list_directory in "tmp/"
   Filtere nach: *_region*_text.txt
   Sortiere numerisch nach region-Nummer
   ```

2. **Lese ALLE Text-Dateien automatisch**:
   ```
   filesystem:read_file für JEDE *_text.txt Datei
   Konkateniere in numerischer Reihenfolge (region01, region02, ...)
   Speichere in Variable: full_recipe_text
   ```

   **Keine Rückfragen** - alle gefundenen Text-Regionen werden verwendet!

3. **Strukturiere den Text** (Pattern-Erkennung):

   **a) Rezeptname**:
   - Erste Überschrift, meist am Anfang
   - Fallback: Frage Nutzer
   - Variable: `recipe_name`

   **b) Portionen**:
   - Suche: "für X Personen", "Portionen:", "Ergibt:", "X Stück"
   - Variable: `portions` (oder "N/A")

   **c) Untertitel** (optional):
   - Kurzbeschreibung unter Rezeptnamen
   - Variable: `subtitle` (oder leer)

   **d) Zeitangaben**:
   - **Vorbereitungszeit**: Suche "Vorbereitungszeit:", "Vorbereitung:"
     - Variable: `prep_time`, `prep_time_iso` (z.B. "PT10M")
   - **Zubereitungszeit**: Suche "Zubereitungszeit:", "Backzeit:", "Kochzeit:"
     - Variable: `cook_time`, `cook_time_iso`
   - **Wartezeit**: Suche "Wartezeit:", "Ruhezeit:", "Kühlzeit:"
     - Variable: `wait_time`, `wait_time_iso`
   - **Gesamtzeit**: Berechne oder suche "Gesamtzeit:"
     - Variable: `total_time`, `total_time_iso`

   **e) Zutaten**:
   - Beginnt mit: "Zutaten:", "Für den Teig:", "Du brauchst:"
   - Zeilen mit Mengenangaben: g, kg, ml, l, EL, TL, Prise, Stück
   - Variable: `ingredients` (Liste von Strings)

   **WICHTIG - Leerzeichen zwischen Menge und Einheit**:
   - Korrigiere "250g" → "250 g"
   - Regex: `(\d+)(g|kg|ml|l|EL|TL)` → `$1 $2`

   **f) Zubereitung**:
   - Beginnt mit: "Zubereitung:", "Anleitung:", "So geht's:"
   - Nummerierte Schritte oder Absätze mit Imperativ-Verben
   - Variable: `instructions` (Liste von Strings)

   **g) Tipps**:
   - Meist am Ende, markiert mit "Tipp:", "Hinweis:", "Info:"
   - Variable: `tips` (oder "Keine Tipps verfügbar")

   **h) Nährwerte** (optional):
   - Suche: "Nährwerte pro Portion:", "Kalorien:", "kcal"
   - Variable: `nutrition` (oder leer)

4. **Validierung**:
   - Rezeptname gefunden? Falls NEIN: Nutze PDF-Name oder frage Nutzer
   - Mindestens 3 Zutaten? Falls NEIN: Warnung
   - Zubereitungsschritte vorhanden? Falls NEIN: Warnung

---

### 4. Bild-Verarbeitung

**Aktionen**:

1. **Finde Foto**:
   ```
   filesystem:list_directory in "tmp/"
   Filtere: *_region*_foto.png
   Sortiere alphabetisch
   ```

2. **Foto-Auswahl automatisch**:
   ```
   Bei 0 Fotos: Setze image_available = false
   Bei 1+ Fotos: Verwende das ERSTE gefundene Foto automatisch
   ```

   **Keine Rückfragen** - erstes verfügbares Foto wird verwendet!

3. **Erstelle sicheren Dateinamen** aus `recipe_name`:
   ```
   Umlaute: ä→ae, ö→oe, ü→ue, ß→ss
   Sonderzeichen entfernen: / \ : * ? " < > | ' ! @ # $ % & ( ) [ ] { } = + , ; ` ~
   Leerzeichen → -
   toLowerCase()
   Max. 50 Zeichen
   Variable: safe_image_name
   ```

4. **Verschiebe Bild**:
   ```
   filesystem:move_file
   source: "tmp/<erstes_foto>.png"
   destination: "Ausgang/Images/<safe_image_name>.png"
   ```

5. Bei Konflikt: Füge Suffix hinzu (_2, _3, _4)

6. Falls kein Foto: Setze `image_available = false`

---

### 5. HTML-Generierung

**Aktionen**:
1. Template laden:
   ```
   filesystem:read_file von "Ausgang/Template.html"
   Speichere in: template_content
   ```

2. **TAG-Ersetzung**:

   | TAG | Ersetzen mit |
   |-----|--------------|
   | `<TITLE>` | recipe_name |
   | `<RECIPE_NAME>` | recipe_name |
   | `<SUBTITLE>` | subtitle (oder leer) |
   | `<IMAGE_PATH>` | "Images/" + safe_image_name (oder Platzhalter) |
   | `<PREP_TIME>` | prep_time |
   | `<PREP_TIME_ISO>` | prep_time_iso |
   | `<COOK_TIME>` | cook_time |
   | `<COOK_TIME_ISO>` | cook_time_iso |
   | `<WAIT_TIME>` | wait_time |
   | `<WAIT_TIME_ISO>` | wait_time_iso |
   | `<TOTAL_TIME>` | total_time |
   | `<TOTAL_TIME_ISO>` | total_time_iso |
   | `<PORTIONS>` | portions |
   | `<INGREDIENTS>` | HTML Liste aus ingredients |
   | `<INSTRUCTIONS>` | HTML Liste aus instructions |
   | `<TIPS>` | tips |
   | `<NUTRITION>` | nutrition (oder leer) |

3. **Zutaten formatieren**:
   ```html
   <ul>
     <li>250 g Mehl</li>
     <li>100 ml Milch</li>
   </ul>
   ```

4. **Zubereitung formatieren**:
   ```html
   <ol>
     <li>Ofen auf 180°C vorheizen.</li>
     <li>Mehl und Milch vermischen.</li>
   </ol>
   ```

5. **ISO-Zeitformat**:
   ```
   Minuten → PTxM  (z.B. "10 Minuten" → "PT10M")
   Stunden → PTxH  (z.B. "2 Stunden" → "PT2H")
   Gemischt → PTxHyM (z.B. "1h 30min" → "PT1H30M")
   ```

6. **Kein Bild vorhanden**:
   ```html
   Falls image_available = false:
   Füge hinzu: <div class="no-image">📷 Kein Bild verfügbar</div>
   Oder verstecke <img> Tag mit CSS: display: none;
   ```

7. Speichern:
   ```
   filesystem:save_file
   file_path: "Ausgang/<safe_recipe_name>.html"
   content: befülltes HTML (UTF-8)
   ```

---

### 6. Index aktualisieren (recipe-index)

**Aktionen**:

#### 6.1 Duplikatsprüfung
```
recipe-index:check_duplicate_recipe
Parameter: recipe_name: <recipe_name>
```

**Wenn Duplikat gefunden**:
```
Frage Nutzer: "Rezept existiert bereits. Was tun?"
a) Überschreiben: remove_recipe_from_index → weiter zu 6.2
b) Suffix: recipe_name → "<recipe_name> v2", safe_recipe_name → "_v2"
c) Abbrechen
```

#### 6.2 Kategorie bestimmen
```
recipe-index:suggest_recipe_category
Parameter: recipe_name: <recipe_name>
Speichere in: suggested_category

Optional: recipe-index:list_index_categories
Frage Nutzer: Vorschlag nutzen oder andere Kategorie?
Speichere Wahl in: chosen_category
```

**Kategorien**:
- Salate, Suppen, Vorspeisen & Snacks, Hauptgerichte, Brot & Gebäck, Desserts & Kuchen, Sonstiges

#### 6.3 Rezept hinzufügen
```
recipe-index:add_recipe_to_index
Parameter:
  - recipe_file: "<safe_recipe_name>.html"
  - recipe_name: <recipe_name>
  - category: <chosen_category> (optional)
```

#### 6.4 Validierung
```
recipe-index:count_recipes
Ausgabe: Gesamtzahl und Anzahl pro Kategorie
```

---

### 7. Qualitätsprüfung

**Aktionen**:
1. Dateien öffnen:
   ```
   windows-launcher:open_in_edge
   file_paths: [
     "Eingang/<current_pdf_name>.pdf",
     "Ausgang/<safe_recipe_name>.html"
   ]
   ```

2. Checkliste präsentieren:
   ```
   ✓ Inhalt: Rezeptname, Zutaten, Schritte, Metadaten korrekt?
   ✓ Darstellung: Bild korrekt, Umlaute korrekt?
   ✓ OCR-Fehler: "0" statt "O", "rn" statt "m", "l" statt "I"?
   ✓ Format: Doppelte Leerzeichen, Zeilenumbrüche, Listen?
   ```

3. Bei Fehlern:
   ```
   filesystem:edit_file - Korrigiere HTML

   Falls Rezeptname geändert:
   recipe-index:remove_recipe_from_index (alter Name)
   recipe-index:add_recipe_to_index (neuer Name)
   ```

---

### 8. Protokollierung

**Aktionen**:
```
filesystem:append_file
file_path: "Ausgang/processing_log.txt"
```

**Log-Template Erfolg**:
```
═══════════════════════════════════════════════════════
[2026-01-09 15:30:45] ✓ ERFOLG
PDF: <current_pdf_name>.pdf
Rezept: <recipe_name>
HTML: <safe_recipe_name>.html
Bild: <safe_image_name>.png (oder "Kein Bild")
Kategorie: <chosen_category>
Textregionen: X
OCR-Qualität: ✓ Gut
Zutaten: X
Zubereitungsschritte: X
Index: Aktualisiert (Gesamt: X Rezepte)
═══════════════════════════════════════════════════════
```

---

### 9. Weitere Rezepte?

**Aktionen**:

1. **Frage**: "Weiteres Rezept aus einem anderen PDF extrahieren?"

2. **Bei JA**: Springe zu Schritt 1 (PDF-Auswahl)
   - tmp/ wird automatisch vom image-selector beim nächsten Start geleert!

3. **Bei NEIN**: Springe zu Schritt 10 (Abschluss)

**Hinweis**: Keine manuelle Bereinigung nötig - der image-selector übernimmt das automatisch beim nächsten Aufruf.

---

### 10. Aufräumen

**Aktionen**:

1. **Keine Bereinigung von tmp/ nötig**:
   - Der image-selector leert tmp/ automatisch beim nächsten Start
   - Temporäre Dateien können dort verbleiben

2. **NICHT löschen**: PDFs (Eingang/), HTML-Dateien, Bilder, index.html

3. Abschlussmeldung:
   ```
   ✅ Verarbeitung abgeschlossen!

   Erstellt:
   • HTML: Ausgang/<safe_recipe_name>.html
   • Bild: Ausgang/Images/<safe_image_name>.png (falls vorhanden)
   • Index: Aktualisiert (Kategorie: <chosen_category>)
   • Log: Eintrag in processing_log.txt

   recipe-index:count_recipes
   Statistik: X Rezepte in Y Kategorien

   💡 Hinweis: tmp/ wird beim nächsten Start automatisch bereinigt
   ```

---

## Fehlerbehebung

### recipe-index Fehler
**Ursachen**: Ungültige Zeichen, HTML fehlt, Index korrupt
**Lösung**:
1. Prüfe recipe_name auf ungültige Zeichen
2. Prüfe ob HTML existiert: `filesystem:list_directory in "Ausgang/"`
3. Falls Index fehlt: Erstelle neuen Basis-Index

### Falsche Kategorie
**Lösung**:
```
1. recipe-index:remove_recipe_from_index
2. recipe-index:add_recipe_to_index (mit korrekter Kategorie)
```

### Falscher Rezeptname
**Lösung**:
```
1. recipe-index:remove_recipe_from_index (alter Name)
2. filesystem:edit_file (korrigiere HTML)
3. recipe-index:add_recipe_to_index (neuer Name)
```

### Kein Foto gefunden
**Normal**: Rezept wird ohne Bild erstellt
**Wenn Foto erwartet**: Prüfe tmp/ auf *_foto.png Dateien

---

## Best Practices

1. **Ein PDF pro Durchlauf**: Pro Rezept ein PDF öffnen, alle Regionen markieren

2. **Automatische Verarbeitung**: Alle Text-Regionen und erstes Foto werden automatisch verwendet

3. **Duplikate prüfen**: IMMER `check_duplicate_recipe` VOR `add_recipe_to_index`

4. **Kategorien konsistent**: `suggest_recipe_category` nutzen, existierende Kategorien bevorzugen

5. **Validierung**: Nach `add_recipe_to_index` immer `count_recipes` aufrufen

6. **Fehlerbehandlung**: Tool-Aufrufe in try-catch, informative Meldungen

7. **Logging**: Alle Index-Änderungen protokollieren

8. **tmp/-Management**: Wird automatisch vom image-selector bereinigt - keine manuelle Intervention nötig
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
