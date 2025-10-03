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

    # Die Prompt-Funktion sollte die erwartete Zeichenkette liefern
    assert (
        server.generate_recipe() == "Lösche die Dateien im Unterordner 'tmp'."
    )
