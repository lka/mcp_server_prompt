import importlib
import os
import sys
import types


def make_fake_fastmcp_module():
    mod = types.ModuleType("fastmcp")

    class FastMCP:
        def __init__(self, name=None, on_duplicate_prompts=None):
            self.name = name
            self.on_duplicate_prompts = on_duplicate_prompts
            self._prompts = []
            self.run_called = False

        def prompt(self, func=None):
            # behave as decorator
            if func is None:

                def decorator(f):
                    self._prompts.append(f)
                    return f

                return decorator
            else:
                self._prompts.append(func)
                return func

        def run(self):
            self.run_called = True

        def serve(self):
            self.serve_called = True

        def start(self):
            self.start_called = True

    mod.FastMCP = FastMCP
    return mod


def import_server_with_fake():
    # Ensure src/ is on sys.path so the package can be imported
    # from the workspace
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    src_dir = os.path.join(repo_root, "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    # inject fake fastmcp before importing the server module
    sys.modules["fastmcp"] = make_fake_fastmcp_module()

    # make sure any cached imports are cleared so tests get a fresh import
    sys.modules.pop("mcp_server_prompt.server", None)
    sys.modules.pop("mcp_server_prompt", None)

    return importlib.import_module("mcp_server_prompt.server")


def test_generate_recipe_and_prompt_registered():
    server = import_server_with_fake()
    assert hasattr(server, "generate_recipe")
    # expected prefix from example server
    assert server.generate_recipe().startswith(
        "Lösche die Dateien im Unterordner 'tmp'."
    )
    # prompt decorator should have registered the function on the mcp instance
    assert server.generate_recipe in getattr(server.mcp, "_prompts", [])


def test_main_calls_run_if_available():
    server = import_server_with_fake()
    assert hasattr(server, "main")
    # initially run_called should be False
    assert not getattr(server.mcp, "run_called", False)
    server.main()
    assert getattr(server.mcp, "run_called", False) is True


def test_main_is_callable():
    server = import_server_with_fake()
    assert callable(server.main)
