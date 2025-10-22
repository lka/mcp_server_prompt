from fastmcp import FastMCP

# from fastmcp.prompts.prompt import Message, PromptMessage, TextContent

mcp = FastMCP(name="PromptServer", on_duplicate_prompts="error")


# Basic prompt returning a string (converted to user message automatically)
@mcp.prompt
def generate_recipe() -> str:
    """Erstellt eine HTML-Datei mit einem gescannten Rezept."""
    return """Benutze für alle neu erzeugten Dateien das Verzeichnis 'tmp'.
Die zu verwendende Sprache ist deutsch.
Lasse mich aus der PDF im Verzeichnis 'Eingang' die Regionen\
 auswählen, die den Text und das Bild des Rezepts enthalten.
Führe OCR auf den ausgewählten Textregionen durch.
Erstelle eine HTML-Datei, die das Rezept mit dem extrahierten Text und Bild\
 darstellt.
Speichere die HTML-Datei im Verzeichnis 'Ausgang' ab.
Für die HTML-Datei verwende die Struktur von Template.html im Verzeichnis\
 'Ausgang' als Vorlage und verwende die darin enthaltenen TAGs.
Stelle sicher, dass das Bild des Rezeptes im Unterverzeichnis\
 'Ausgang\\Images' gespeichert wird und in der HTML-Datei korrekt referenziert\
 wird. Achte dabei auf Umlaute und Sonderzeichen.
Ergänze die Datei 'index.html' im Verzeichnis 'Ausgang', um auf die neue\
 Rezeptdatei zu verlinken."""


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
