"""Only startup paths changed by BD-C01; never use the user's workspace."""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from host import PROJECT, JsonStore, ModuleManifest, ModuleRegistry, setup
from launch import readiness


class Startup(unittest.TestCase):
    def test_missing_source_reports_without_creating_workspace(self):
        with TemporaryDirectory() as temporary:
            home = Path(temporary)
            absent = home / "never-created"
            with patch.dict(
                os.environ,
                {
                    "BD_THREADDESK_SOURCE": str(absent),
                    "BD_WHITEBOARD_ROOT": str(home / "board"),
                },
            ):
                report = readiness()
            self.assertFalse(report["prerequisites_ready"])
            self.assertFalse((home / "board").exists())

    def test_explicit_setup_preserves_disabled_module_and_thread(self):
        with TemporaryDirectory() as temporary:
            home = Path(temporary)
            store = JsonStore(home)
            registry = ModuleRegistry(store)
            manifest = ModuleManifest.from_dict(
                json.loads((PROJECT / "module.json").read_text())
            )
            registry.install(manifest)
            before = (home / "modules.json").read_bytes()
            with (
                patch.dict(os.environ, {"BD_WHITEBOARD_ROOT": str(home)}),
                self.assertRaisesRegex(RuntimeError, "disabled"),
            ):
                setup()
            self.assertEqual((home / "modules.json").read_bytes(), before)
            self.assertEqual(store.list_threads(), [])

    def test_shell_reports_explicit_missing_python_without_setup(self):
        with TemporaryDirectory() as temporary:
            env = {
                **os.environ,
                "BD_PYTHON": str(Path(temporary) / "missing"),
                "BD_WHITEBOARD_ROOT": str(Path(temporary) / "board"),
            }
            result = subprocess.run(
                [str(ROOT / "start.command"), "--check"],
                env=env,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("BD_PYTHON", result.stderr)
            self.assertFalse((Path(temporary) / "board").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
