import importlib
import os
import sys

import pytest


@pytest.mark.integration
def test_integration_with_real_fastmcp():
    """Integrationstest: nutzt echte `fastmcp`-Installation.

    Der Test wird übersprungen, wenn die Umgebungsvariable
    `RUN_INTEGRATION` nicht auf `1` gesetzt ist oder wenn
    `fastmcp` nicht installiert ist.
    """
    if os.environ.get("RUN_INTEGRATION") != "1":
        pytest.skip("Set RUN_INTEGRATION=1 to run integration tests")

    # Wenn fastmcp nicht installiert ist, skippen
    pytest.importorskip("fastmcp")

    # Stelle sicher, dass wir das echte Paket importieren (keine vorher
    # injizierten Mocks aus den Unit-Tests in sys.modules)
    sys.modules.pop("fastmcp", None)
    sys.modules.pop("mcp_server_prompt.server", None)
    sys.modules.pop("mcp_server_prompt", None)

    # src/ zum sys.path hinzufügen, falls nicht vorhanden
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    src_dir = os.path.join(repo_root, "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    fastmcp = importlib.import_module("fastmcp")
    server = importlib.import_module("mcp_server_prompt.server")

    # mcp sollte eine Instanz von fastmcp.FastMCP sein
    assert isinstance(server.mcp, fastmcp.FastMCP)

    # RECIPE_PROMPT Konstante sollte existieren und den erwarteten Inhalt haben
    assert hasattr(server, "RECIPE_PROMPT")
    assert server.RECIPE_PROMPT.startswith("\n# Rezept-Extraktion aus PDF")

    # Die Prompt-Funktion sollte die erwartete Zeichenkette liefern
    # Manche Implementationen von fastmcp ersetzen die Python-Funktion
    # durch ein Wrapper-Objekt (z. B. FunctionPrompt). Versuche mehrere
    # Strategien, um den resultierenden String zu erhalten.
    for func_name in ("generate_recipe", "get_recipe_prompt"):
        result = None
        gen = getattr(server, func_name, None)
        if callable(gen):
            try:
                result = gen()
            except TypeError:
                result = None

        if result is None and gen is not None:
            # häufige Attribute, die die originale Funktion enthalten
            for attr in ("fn", "func", "function", "wrapped", "__wrapped__"):
                candidate = getattr(gen, attr, None)
                if callable(candidate):
                    try:
                        result = candidate()
                        break
                    except TypeError:
                        result = None

        assert (
            result is not None
        ), f"Konnte den Rückgabewert von {func_name}() nicht ermitteln"
        assert (
            result == server.RECIPE_PROMPT
        ), f"{func_name}() liefert nicht RECIPE_PROMPT"
