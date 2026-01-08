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
# Rezept-Extraktion aus PDF - Optimierte Version

## Ziel
Extrahiere Rezepte aus PDF-Dateien und erstelle formatierte HTML-Seiten mit automatischer OCR-Unterstützung.

## Arbeitsverzeichnisse
- **tmp/**: Temporäre Dateien (wird vom image-selector beim Start automatisch geleert!)
- **Eingang/**: PDF-Dateien (bleiben erhalten - können mehrere Rezepte enthalten!)
- **Ausgang/**: HTML-Dateien und Bilder
- **Ausgang/Images/**: Rezeptbilder
- **Ausgang/Template.html**: HTML-Vorlage

## Verfügbare Konnektoren
- **filesystem**: Datei-/Verzeichnis-Operationen (list, read, save, append, delete, move, edit)
- **image-selector**: Interaktive Region-Auswahl mit automatischem OCR
- **windows-launcher**: Dateien in Microsoft Edge öffnen
- **tesseract**: OCR-Fallback (falls image-selector nicht ausreicht)

---

## Schritt-für-Schritt Workflow

### 0. Vorbereitung
**Ziel**: Projekt-Struktur prüfen und PDFs identifizieren

**Aktionen**:
1. Verwende `filesystem:list_directory` um Verzeichnisse zu prüfen:
   - tmp/ (existiert? - wird bei image-selector Start geleert)
   - Eingang/ (existiert?)
   - Ausgang/ (existiert?)
   - Ausgang/Images/ (existiert?)

2. Liste verfügbare PDFs:
   - `filesystem:list_directory` in "Eingang/"
   - Sortiere PDFs alphabetisch
   - Zeige nummerierte Liste

3. Status-Ausgabe:
   ```
   📋 Status:
   • X PDF(s) gefunden: [Liste]
   • Template.html vorhanden: Ja/Nein
   • Anzahl Rezepte in Index: X

   ℹ️ Hinweis: Ein PDF kann mehrere Rezepte enthalten.
   ```

4. Prüfe ob `Ausgang/Template.html` existiert:
   - Falls NEIN: Erstelle Basis-Template (siehe Anhang A)

---

### 1. PDF-Auswahl
**Ziel**: PDF für Verarbeitung auswählen

**Aktionen**:
1. Bei nur 1 PDF: Automatisch auswählen
2. Bei mehreren PDFs: Frage Nutzer welches PDF verarbeitet werden soll

3. Wichtige Information an Nutzer:
   ```
   ℹ️ Das ausgewählte PDF: [Name]

   Kann dieses PDF mehrere Rezepte enthalten?
   - Falls JA: Wir verarbeiten jetzt ein Rezept. Du kannst
     danach das gleiche PDF erneut öffnen für weitere Rezepte.
   - Falls NEIN/Unklar: Normal fortfahren.
   ```

4. Merke PDF-Namen für spätere Schritte: `current_pdf_name`

---

### 2. PDF-Analyse mit image-selector
**Ziel**: Interaktive Region-Auswahl mit automatischem OCR

**⚠️ WICHTIG**:
- Der image-selector löscht ALLE Dateien in tmp/ beim Start!
- Dies ist normales Verhalten - vorherige Daten sollten bereits gesichert sein

**Aktionen**:
1. Verwende `image-selector:select_image_regions`:
   ```
   Parameter:
   - image_path: "Eingang/<current_pdf_name>.pdf"
   ```

2. **GUI öffnet sich** - Instruktionen für Nutzer:
   ```
   📌 Bitte markiere für EIN EINZIGES Rezept:

   Als 'text' markieren:
   • Rezeptname/Titel
   • Zutaten-Liste
   • Zubereitungsschritte
   • Metadaten (Portionen, Zeit, etc.)
   • Tipps/Hinweise

   Als 'foto' markieren:
   • Das Hauptbild des Rezepts

   ⚠️ Falls mehrere Rezepte auf der Seite:
   → Markiere nur EIN Rezept jetzt!
   → Weitere Rezepte später separat verarbeiten
   ```

3. Nach Abschluss: Automatisch erstellt in tmp/:
   - `<pdf-name>_region01_text.txt` (OCR bereits durchgeführt!)
   - `<pdf-name>_region02_text.txt` (weitere Textregionen)
   - `<pdf-name>_region03_text.txt` (optional)
   - `<pdf-name>_regionXX_foto.png` (Bildregion)

4. Validierung:
   ```
   Verwende: image-selector:list_exported_regions
   Erwartete Ausgabe: Liste aller exportierten Dateien
   ```

5. Falls keine Regionen exportiert:
   - Nutzer hat abgebrochen oder nichts markiert
   - Frage: "Möchtest du es nochmal versuchen?"
   - Alternative: "Möchtest du das Rezept manuell eingeben?"

---

### 3. Text-Extraktion aus OCR-Dateien
**Ziel**: Text aus automatisch erstellten .txt Dateien einlesen und strukturieren

**Aktionen**:
1. Liste tmp/ Verzeichnis:
   ```
   Verwende: filesystem:list_directory in "tmp/"
   Filtere nach: *_region*_text.txt
   Sortiere nach: region01, region02, region03, ...
   ```

2. Für jede Text-Datei:
   ```
   Verwende: filesystem:read_file für jede *_text.txt Datei
   Beispiele:
   - "tmp/Kochbuch_region01_text.txt"
   - "tmp/Kochbuch_region02_text.txt"
   ```

3. Konkateniere alle Texte:
   - In numerischer Reihenfolge (region01 + region02 + ...)
   - Mit Zeilenumbruch zwischen Regionen
   - Gesamttext speichern in Variable: `full_recipe_text`

4. **Strukturiere den Text** (Pattern-Erkennung):

   **a) Rezeptname**:
   - Erste Überschrift, größte Schrift, fett gedruckt
   - Meist am Anfang der ersten Region
   - Fallback: Frage Nutzer: "Ich habe keinen Rezeptnamen gefunden. Wie heißt das Rezept?"
   - Variable: `recipe_name`

   **b) Portionen**:
   - Suche nach: "für X Personen", "Portionen:", "Ergibt:", "X Stück"
   - Beispiele: "4 Personen", "12 Muffins", "1 Backblech"
   - Variable: `portions` (oder "N/A")

   **c) Untertitel/Beschreibung** (optional):
   - Kurze Beschreibung unter dem Rezeptnamen
   - Oft in kursiv oder als erster Satz
   - Beispiele: "Die vegetarische Variante aus Soja ist fein abgeschmeckt"
   - Variable: `subtitle` (oder leer)

   **d) Zeitangaben**:
   - **Vorbereitungszeit**: Suche nach "Vorbereitungszeit:", "Vorbereitung:"
     - Beispiel: "10 Minuten"
     - Variable: `prep_time` (oder "N/A")
     - ISO-Format: Konvertiere zu "PT10M" in Variable `prep_time_iso`

   - **Zubereitungszeit**: Suche nach "Zubereitungszeit:", "Backzeit:", "Kochzeit:"
     - Beispiel: "45 Minuten"
     - Variable: `cook_time` (oder "N/A")
     - ISO-Format: Konvertiere zu "PT45M" in Variable `cook_time_iso`

   - **Wartezeit** (optional): Suche nach "Wartezeit:", "Ruhezeit:", "Kühlzeit:"
     - Beispiel: "5 Minuten"
     - Variable: `wait_time` (oder "N/A")
     - ISO-Format: Konvertiere zu "PT5M" in Variable `wait_time_iso`

   - **Gesamtzeit**: Berechne oder suche nach "Gesamtzeit:"
     - Beispiel: "60 Minuten" (Vorbereitung + Zubereitung + Wartezeit)
     - Variable: `total_time` (oder "N/A")
     - ISO-Format: Konvertiere zu "PT60M" in Variable `total_time_iso`

   **e) Zutaten**:
   - Beginnt oft mit: "Zutaten:", "Für den Teig:", "Du brauchst:"
   - Zeilen mit Mengenangaben: g, kg, ml, l, EL, TL, Prise, Stück
   - Meist vor der Zubereitung
   - Unterabschnitte beachten: "Für den Teig:", "Für die Füllung:"
   - Jede Zeile = eine Zutat
   - Variable: `ingredients` (Liste von Strings)

   **WICHTIGE FORMATIERUNGSREGEL für Zutaten**:
   - **Zwischen Menge und Einheit MUSS immer ein Leerzeichen stehen**
   - Richtig: "250 g Mehl", "100 ml Milch", "2 EL Öl"
   - Falsch: "250g Mehl", "100ml Milch", "2EL Öl"
   - Falls OCR das Leerzeichen vergessen hat, ergänze es automatisch
   - Regex-Pattern zum Korrigieren: `(\d+)(g|kg|ml|l|EL|TL)` → `$1 $2`
   - Beispiel-Korrekturen:
     - "250g" → "250 g"
     - "100ml" → "100 ml"
     - "2EL" → "2 EL"
     - "1TL" → "1 TL"

   **f) Zubereitung**:
   - Beginnt mit: "Zubereitung:", "Anleitung:", "So geht's:"
   - Nummerierte Schritte (1., 2., 3.) oder
   - Absätze mit Imperativ-Verben (Heizen, Mischen, Rühren, Backen)
   - Jeder Schritt = ein Listenelement
   - Variable: `instructions` (Liste von Strings)

   **g) Tipps/Hinweise**:
   - Meist am Ende
   - Markiert mit: "Tipp:", "Hinweis:", "Info:", "Variante:", "Fettbetter Fact:"
   - Variable: `tips` (oder "Keine Tipps verfügbar")

   **h) Nährwerte** (optional):
   - Suche nach: "Nährwerte pro Portion:", "Kalorien:", "kcal"
   - Format: "X kcal | X g Fett | X g Kohlenhydrate | X g Eiweiß"
   - Beispiel: "630 kcal | 18 g Fett | 80 g Kohlenhydrate | 31 g Eiweiß"
   - Variable: `nutrition` (oder leer)

5. **Validierung**:
   - ❓ Rezeptname gefunden?
     - Falls NEIN: Nutze PDF-Name als Fallback oder frage Nutzer
   - ❓ Mindestens 3 Zutaten?
     - Falls NEIN: Warnung "⚠️ Nur X Zutaten gefunden - bitte prüfen"
   - ❓ Zubereitungsschritte vorhanden?
     - Falls NEIN: Warnung "⚠️ Keine Zubereitung gefunden"
   - ❓ OCR-Qualität:
     - Viele "?", "�", unvollständige Wörter?
     - Warnung: "⚠️ OCR-Qualität niedrig - manuelle Prüfung empfohlen"

6. **Fallback bei leeren .txt Dateien**:
   - Alle .txt Dateien leer → OCR komplett fehlgeschlagen
   - Optionen:
     - Wiederhole image-selector (vielleicht bessere Regionen?)
     - Manuelle Texteingabe anbieten
     - Nutze `tesseract:extract_text_from_image` auf die region*_text.png Bilder

---

### 4. Bild-Verarbeitung
**Ziel**: Rezeptbild finden und sicher in Ausgang/Images/ verschieben

**Aktionen**:
1. Finde Foto-Dateien:
   ```
   Verwende: filesystem:list_directory in "tmp/"
   Filtere nach: *_region*_foto.png
   Normalfall: 1 Foto
   Sonderfall: Mehrere Fotos → Wähle erstes oder frage Nutzer
   ```

2. **Erstelle sicheren Dateinamen** aus `recipe_name`:

   **Konvertierungsregeln**:
   ```
   Umlaute:
   ä → ae, ö → oe, ü → ue, ß → ss
   Ä → Ae, Ö → Oe, Ü → Ue

   Akzente:
   é → e, è → e, ê → e, à → a, â → a, ô → o, î → i, ç → c

   Sonderzeichen entfernen:
   / \ : * ? " < > | ' ! @ # $ % & ( ) [ ] { } = + , ; ` ~ → Entfernen

   Leerzeichen & Bindestriche:
   Leerzeichen → _
   - → _ (optional: behalten als -)

   Cleanup:
   Mehrfache Unterstriche → einzelner _
   Führende/trailing Unterstriche → entfernen
   toLowerCase() für Konsistenz
   Max. 50 Zeichen (ohne Extension)
   ```

   **Beispiele**:
   ```
   "Oma's Käse-Spätzle!" → "omas_kaese_spaetzle.png"
   "Crème Brûlée" → "creme_brulee.png"
   "Tiramisu à la Mama" → "tiramisu_a_la_mama.png"
   "Schoko-Muffins (vegan)" → "schoko_muffins_vegan.png"
   ```

   Variable: `safe_image_name`

3. **Verschiebe Bild**:
   ```
   Verwende: filesystem:move_file
   Parameter:
   - source_path: "tmp/<pdf-name>_regionXX_foto.png"
   - destination_path: "Ausgang/Images/<safe_image_name>.png"
   ```

4. **Bei Konflikt** (Datei existiert bereits):
   ```
   Prüfe: filesystem:list_directory in "Ausgang/Images/"
   Falls <safe_image_name>.png existiert:
   → Füge Suffix hinzu: "_2.png", "_3.png", "_4.png"
   → Wiederhole move_file mit neuem Namen
   → Aktualisiere safe_image_name Variable
   ```

5. **Falls kein Foto gefunden**:
   ```
   Wenn filesystem:list_directory keine *_foto.png findet:
   → Melde: "⚠️ Kein Bild gefunden für dieses Rezept"
   → Setze: image_available = false
   → HTML wird ohne Bild erstellt
   → Notiere in Log
   ```

---

### 5. HTML-Generierung
**Ziel**: Formatierte HTML-Seite aus Template erstellen

**Aktionen**:
1. **Template laden**:
   ```
   Verwende: filesystem:read_file von "Ausgang/Template.html"
   Speichere in Variable: template_content
   ```

2. **TAG-Ersetzung** (alle TAGs müssen befüllt werden):

   | TAG | Ersetzen mit | Beispiel |
   |-----|--------------|----------|
   | `<TITLE>` | recipe_name | "Schoko-Muffins" |
   | `<RECIPE_NAME>` | recipe_name | "Schoko-Muffins" |
   | `<SUBTITLE>` | Kurzbeschreibung (optional) | "Saftige Muffins mit Schokodrops" oder leer |
   | `<IMAGE_PATH>` | "Images/" + safe_image_name | "Images/schoko_muffins.png" |
   | `<PREP_TIME>` | Vorbereitungszeit | "10 Minuten" oder "N/A" |
   | `<PREP_TIME_ISO>` | ISO-Format der Vorbereitungszeit | "PT10M" oder leer |
   | `<COOK_TIME>` | Zubereitungs-/Backzeit | "45 Minuten" oder "N/A" |
   | `<COOK_TIME_ISO>` | ISO-Format der Zubereitungszeit | "PT45M" oder leer |
   | `<WAIT_TIME>` | Wartezeit (optional) | "5 Minuten" oder "N/A" |
   | `<WAIT_TIME_ISO>` | ISO-Format der Wartezeit | "PT5M" oder leer |
   | `<TOTAL_TIME>` | Gesamtzeit | "60 Minuten" oder "N/A" |
   | `<TOTAL_TIME_ISO>` | ISO-Format der Gesamtzeit | "PT60M" oder leer |
   | `<PORTIONS>` | Anzahl Portionen | "4" oder "12 Stück" |
   | `<INGREDIENTS>` | HTML Liste aus ingredients | siehe unten |
   | `<INSTRUCTIONS>` | HTML Liste aus instructions | siehe unten |
   | `<TIPS>` | Tipps/Hinweise | Text oder "Keine Tipps verfügbar" |
   | `<NUTRITION>` | Nährwerte (optional) | "630 kcal | 18 g Fett | 80 g KH | 31 g Eiweiß" oder leer |

3. **Zutaten-Liste formatieren**:
   ```html
   <ul>
     <li>250 g Mehl</li>
     <li>100 ml Milch</li>
     <li>2 EL Öl</li>
     <li>1 TL Salz</li>
     <li>2 Eier</li>
   </ul>
   ```

   **Wichtig**: Achte darauf, dass zwischen Menge und Einheit ein Leerzeichen steht!
   - Korrekt: `<li>250 g Mehl</li>` (mit Leerzeichen)
   - Falsch: `<li>250g Mehl</li>` (ohne Leerzeichen)

4. **Zubereitungs-Liste formatieren**:
   ```html
   <ol>
     <li>Ofen auf 180°C vorheizen.</li>
     <li>Mehl und Milch in einer Schüssel vermischen.</li>
     <li>Eier unterrühren bis ein glatter Teig entsteht.</li>
     <li>In Muffinförmchen füllen und 30 Minuten backen.</li>
   </ol>
   ```

5. **Sonderfälle**:
   - Falls `image_available = false`:
     - Entferne kompletten `<img>` Tag aus Template
     - Oder kommentiere aus: `<!-- <img src="..."> -->`
   - Falls keine Portionen/Zeit: Zeige "N/A" oder lasse Feld weg
   - Falls keine Zeile mit Zeit-Info vorhanden: Entferne die entsprechende Zeile aus recipe-info

   **ISO-Zeitformat Konvertierung** (für Schema.org Markup):
   ```
   Minuten → PTxM  (z.B. "10 Minuten" → "PT10M")
   Stunden → PTxH  (z.B. "2 Stunden" → "PT2H")
   Gemischt → PTxHyM (z.B. "1 Stunde 30 Minuten" → "PT1H30M")

   Beispiele:
   - "5 Minuten" → "PT5M"
   - "45 Minuten" → "PT45M"
   - "1 Stunde" → "PT1H"
   - "1 Stunde 30 Minuten" → "PT1H30M"
   - "2 Stunden 15 Minuten" → "PT2H15M"
   ```

6. **Qualitätssicherung**:
   - ✓ Keine `<PLACEHOLDER>`-TAGs mehr sichtbar
   - ✓ `<meta charset="UTF-8">` im `<head>` vorhanden
   - ✓ Alle Umlaute korrekt (ä, ö, ü, ß)
   - ✓ HTML-Struktur valide (alle Tags geschlossen)

7. **Speichern**:
   ```
   Verwende: filesystem:save_file
   Parameter:
   - file_path: "Ausgang/<safe_recipe_name>.html"
   - content: befülltes HTML (UTF-8 encoded)
   ```

   Für `safe_recipe_name`: Gleiche Konvertierungsregeln wie Bildname

---

### 6. Index aktualisieren
**Ziel**: Rezept-Link in index.html hinzufügen und sortieren

**Aktionen**:
1. **Index laden**:
   ```
   Verwende: filesystem:read_file von "Ausgang/index.html"
   ```

2. **Falls index.html nicht existiert**:
   - Erstelle Basis-Index (siehe Anhang B)
   - Speichere mit `filesystem:save_file`

3. **Duplikatsprüfung**:
   ```
   Suche in index.html nach: href="<safe_recipe_name>.html"

   Falls gefunden:
   → Frage: "Rezept existiert bereits. Überschreiben?"
   → Bei NEIN: Füge Suffix "_v2", "_v3" hinzu
   → Bei JA: Ersetze bestehenden Link (aktualisiere Datum)
   ```

4. **Neuen Link erstellen**:
   ```html
   <li>
     <a href="<safe_recipe_name>.html"><recipe_name></a>
     <span class="date">(08.01.2026)</span>
   </li>
   ```

5. **Sortierung**:
   - Extrahiere alle `<li>` Einträge
   - Sortiere alphabetisch nach Linktext (case-insensitive)
   - Optional: Ignoriere Artikel am Anfang ("Der", "Die", "Das")
   - Beispiel-Reihenfolge:
     ```
     Apfelkuchen
     Käsespätzle
     Schoko-Muffins
     Tiramisu
     ```

6. **Rezept-Zähler aktualisieren**:
   - Zähle alle `<li>` Einträge
   - Ersetze: `<span id="count">X</span>` mit neuer Anzahl

7. **Speichern**:
   ```
   Verwende: filesystem:save_file
   Parameter:
   - file_path: "Ausgang/index.html"
   - content: aktualisierter Index (UTF-8)
   ```

8. **Validierung**:
   - ✓ Neuer Link sichtbar?
   - ✓ Sortierung korrekt?
   - ✓ Counter stimmt mit Anzahl überein?

---

### 7. Qualitätsprüfung
**Ziel**: Visueller Vergleich zwischen PDF und HTML

**Aktionen**:
1. **Dateien öffnen**:
   ```
   Verwende: windows-launcher:open_in_edge
   Parameter:
   - file_paths: [
       "Eingang/<current_pdf_name>.pdf",
       "Ausgang/<safe_recipe_name>.html"
     ]
   - new_window: false (beide als Tabs)
   ```

2. **Checkliste für Nutzer präsentieren**:
   ```
   📋 Bitte vergleiche PDF und HTML:

   Inhalt:
   ✓ Rezeptname korrekt und vollständig?
   ✓ Alle Zutaten vorhanden (Menge + Einheit + Zutat)?
   ✓ Zubereitungsschritte vollständig?
   ✓ Reihenfolge der Schritte korrekt?
   ✓ Metadaten korrekt (Portionen, Zeit, Schwierigkeit)?

   Darstellung:
   ✓ Bild zeigt das richtige Gericht?
   ✓ Bild nicht verzerrt oder abgeschnitten?
   ✓ Umlaute korrekt dargestellt (ä, ö, ü, ß)?

   OCR-Fehler prüfen:
   ✓ Keine "0" statt "O" (z.B. "0fen" → "Ofen")
   ✓ Keine "rn" statt "m" (z.B. "Milcli" → "Milch")
   ✓ Keine "l" statt "I" (z.B. "El" → "EL")
   ✓ Keine fehlenden oder doppelten Buchstaben

   Format:
   ✓ Keine doppelten Leerzeichen
   ✓ Zeilenumbrüche sinnvoll gesetzt
   ✓ Listen korrekt formatiert
   ```

3. **Bei gefundenen Fehlern**:
   - Notiere die Fehler
   - Biete manuelle Korrektur an:
     ```
     Verwende: filesystem:edit_file
     - Korrigiere fehlerhafte Stellen im HTML
     ```

4. **Optional: Index-Kontrolle**:
   ```
   Verwende: windows-launcher:open_in_edge
   - file_paths: ["Ausgang/index.html"]

   Prüfe:
   ✓ Neuer Link vorhanden
   ✓ Sortierung korrekt
   ✓ Link funktioniert
   ```

---

### 8. Protokollierung
**Ziel**: Verarbeitungsstatus dokumentieren

**Aktionen**:
1. **Log-Eintrag erstellen**:
   ```
   Verwende: filesystem:append_file
   Parameter:
   - file_path: "Ausgang/processing_log.txt"
   - content: Log-Eintrag (siehe Templates unten)
   ```

2. **Log-Templates**:

   **Erfolg**:
   ```
   ═══════════════════════════════════════════════════════
   [2026-01-08 14:23:45] ✓ ERFOLG
   PDF: <current_pdf_name>.pdf
   Rezept: <recipe_name>
   HTML: <safe_recipe_name>.html
   Bild: <safe_image_name>.png → Images/
   Textregionen: X (region01, region02, ...)
   Fotoregionen: 1 (regionXX)
   OCR-Qualität: ✓ Gut
   Zutaten: X gefunden
   Zubereitungsschritte: X gefunden
   Index: Aktualisiert (jetzt X Rezepte)
   Dauer: ~X Minuten
   ═══════════════════════════════════════════════════════
   ```

   **Teilweise**:
   ```
   ═══════════════════════════════════════════════════════
   [2026-01-08 14:30:00] ⚠ TEILWEISE
   PDF: <current_pdf_name>.pdf
   Rezept: <recipe_name> (Name manuell eingegeben)
   HTML: <safe_recipe_name>.html
   Bild: ⚠ Kein Foto markiert - ohne Bild erstellt
   Textregionen: X
   OCR-Qualität: ⚠ Mittel (einige "?" Zeichen)
   Zutaten: X gefunden
   Zubereitungsschritte: X gefunden
   Hinweis: Manuelle Überprüfung empfohlen
   Index: Aktualisiert (jetzt X Rezepte)
   ═══════════════════════════════════════════════════════
   ```

   **Fehler**:
   ```
   ═══════════════════════════════════════════════════════
   [2026-01-08 14:35:00] ✗ FEHLER
   PDF: <current_pdf_name>.pdf
   Fehler: <Fehlerbeschreibung>
   Status: Abgebrochen - keine Dateien erstellt
   Ursache: <Ursache>
   Vorschlag: <Lösungsvorschlag>
   ═══════════════════════════════════════════════════════
   ```

---

### 9. Weitere Rezepte?
**Ziel**: Workflow für mehrere Rezepte aus einem PDF

**Aktionen**:
1. Nach erfolgreicher Verarbeitung fragen:
   ```
   ❓ Enthält das PDF "<current_pdf_name>" weitere Rezepte?
   ❓ Möchtest du ein weiteres Rezept aus diesem PDF extrahieren?
   ```

2. **Bei JA**:
   ```
   ℹ️ Hinweise:
   • Beim nächsten Start von image-selector werden die tmp/
     Dateien automatisch gelöscht
   • Das ist normal - die aktuellen Daten sind bereits gesichert
   • Du kannst jetzt andere Regionen im gleichen PDF markieren

   → Springe zurück zu Schritt 2 (PDF-Analyse)
   → Nutze das GLEICHE PDF erneut
   → Lasse Nutzer andere Regionen für anderes Rezept markieren
   ```

3. **Bei NEIN**:
   ```
   ❓ Möchtest du ein anderes PDF verarbeiten?

   Bei JA: → Zurück zu Schritt 1 (PDF-Auswahl)
   Bei NEIN: → Workflow beenden, zu Schritt 10 (Cleanup)
   ```

---

### 10. Aufräumen
**Ziel**: Temporäre Dateien bereinigen

**⚠️ WICHTIG: PDFs NICHT löschen!**

**Begründung**:
- Ein PDF kann mehrere Rezepte enthalten
- Nutzer könnte später weitere Rezepte extrahieren wollen
- PDFs sind Quellmaterial und sollten erhalten bleiben

**Aktionen**:
1. **Temporäre Dateien in tmp/**:
   ```
   ℹ️ Hinweis: Beim nächsten image-selector Aufruf werden
   tmp/ Dateien automatisch gelöscht.

   Optional - Manuelles Cleanup JETZT:

   Verwende: filesystem:list_directory in "tmp/"
   Filtere nach: *_region*.*

   Für jede gefundene Datei:
   Verwende: filesystem:delete_this_file

   Beispiele:
   - "tmp/Kochbuch_region01_text.txt"
   - "tmp/Kochbuch_region02_text.txt"
   - "tmp/Kochbuch_region05_foto.png"

   Bestätigung: "✓ X temporäre Dateien aus tmp/ gelöscht"
   ```

2. **Was NICHT gelöscht wird**:
   ```
   ✗ Keine PDFs aus Eingang/ löschen
   ✗ Keine HTML-Dateien aus Ausgang/
   ✗ Keine Bilder aus Ausgang/Images/
   ✓ Nur tmp/ Dateien (optional)
   ```

3. **Abschlussmeldung**:
   ```
   ✅ Verarbeitung abgeschlossen!

   Erstellt:
   • HTML: Ausgang/<safe_recipe_name>.html
   • Bild: Ausgang/Images/<safe_image_name>.png (falls vorhanden)
   • Index: Aktualisiert mit neuem Link
   • Log: Eintrag in processing_log.txt

   Das PDF bleibt im Eingang/ für zukünftige Verarbeitungen.
   ```

---

## Wichtige Prinzipien

1. **PDFs bleiben erhalten**: Ein PDF kann mehrere Rezepte enthalten
2. **tmp/ wird auto-geleert**: Bei jedem image-selector Start
3. **OCR ist automatisch**: image-selector erstellt *_text.txt Dateien
4. **UTF-8 überall**: Alle Dateien mit UTF-8 Encoding
5. **Sichere Dateinamen**: Umlaute und Sonderzeichen konvertieren
6. **Validierung ist wichtig**: Nach jedem Schritt prüfen
7. **Logging für Transparenz**: Jeden Durchlauf dokumentieren
8. **Fehler sind okay**: Robuste Fehlerbehandlung mit Fallbacks
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
