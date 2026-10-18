"""Read-only startup preflight, then the existing local host/server path."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path.home() / "threaddesk-worktrees/ordinal-lock/src"


def readiness():
    source = Path(
        os.environ.get("BD_THREADDESK_SOURCE", str(DEFAULT_SOURCE))
    ).expanduser()
    whiteboard = Path(
        os.environ.get("BD_WHITEBOARD_ROOT", str(Path.home() / ".threaddesk"))
    ).expanduser()
    binding = PROJECT / ".runtime/binding.json"
    checks = [
        {
            "name": "python",
            "ok": sys.version_info >= (3, 12),
            "detail": "Python >=3.12 required; set BD_PYTHON to an existing interpreter.",
        }
    ]
    checks.append(
        {
            "name": "threaddesk_source",
            "ok": (source / "threaddesk/services/modules.py").is_file(),
            "detail": "Set BD_THREADDESK_SOURCE to a compatible ThreadDesk src directory.",
        }
    )
    if checks[-1]["ok"] and checks[0]["ok"]:
        sys.path.insert(0, str(source))
        sys.dont_write_bytecode = True
        try:
            modules = importlib.import_module("threaddesk.services.modules")
            supported = Path(modules.__file__).resolve() == (
                source / "threaddesk/services/modules.py"
            ).resolve() and all(
                hasattr(modules, key)
                for key in ("ModuleManifest", "ModuleRegistry", "ModuleRuntime")
            )
        except ImportError:
            supported = False
        checks.append(
            {
                "name": "module_contract",
                "ok": supported,
                "detail": "Existing module API must import; no dependency installation is performed.",
            }
        )
    enabled = None
    registry = whiteboard / "modules.json"
    try:
        saved = json.loads(registry.read_text()) if registry.exists() else {}
        item = saved.get("modules", {}).get("block-designer")
        if item is not None:
            enabled = item.get("enabled") is True
    except (OSError, ValueError, TypeError, AttributeError):
        checks.append(
            {
                "name": "module_registry",
                "ok": False,
                "detail": "Existing registry is unreadable; preserve it and repair before setup.",
            }
        )
    if binding.exists() and enabled is None:
        checks.append(
            {
                "name": "module_registry",
                "ok": False,
                "detail": "Existing binding has no installed module. Preserve binding and review the selected Whiteboard root before setup.",
            }
        )
    if enabled is False:
        checks.append(
            {
                "name": "module_enabled",
                "ok": False,
                "detail": "BlockDesigner is disabled. Setup will preserve that decision; enable it explicitly in the existing module administration.",
            }
        )
    binding_ready = False
    if binding.exists():
        try:
            value = json.loads(binding.read_text())
            identity = value.get("thread_id")
            binding_ready = (
                isinstance(identity, str)
                and re.fullmatch(r"[A-Za-z0-9_-]{1,128}", identity) is not None
                and (whiteboard / "threads" / (identity + ".json")).is_file()
            )
            if value.get("root") is not None:
                binding_ready = (
                    binding_ready
                    and Path(value["root"]).resolve() == whiteboard.resolve()
                )
        except (OSError, ValueError, TypeError, AttributeError):
            pass
        checks.append(
            {
                "name": "existing_binding",
                "ok": binding_ready,
                "detail": "Existing binding must refer to a thread in BD_WHITEBOARD_ROOT; it will not be overwritten.",
            }
        )
    prerequisites = all(check["ok"] for check in checks)
    return {
        "product": "BlockDesigner",
        "version": json.loads((PROJECT / "package.json").read_text())["version"],
        "prerequisites_ready": prerequisites,
        "binding_ready": binding_ready,
        "setup_required": not binding.exists(),
        "checks": checks,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="BlockDesigner: existing local editor, no dependency installation. Configure BD_PYTHON and BD_THREADDESK_SOURCE if needed."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check",
        action="store_true",
        help="Read-only readiness report; does not create bindings or project data",
    )
    mode.add_argument(
        "--setup",
        action="store_true",
        help="Create/reuse the existing own module binding; never reactivate a disabled module",
    )
    parser.add_argument("--port", type=int, default=5190)
    args = parser.parse_args(argv)
    if not 0 <= args.port <= 65535:
        parser.error("port must be 0–65535")
    report = readiness()
    if args.check:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["prerequisites_ready"] and report["binding_ready"] else 2
    if not report["prerequisites_ready"]:
        for check in report["checks"]:
            if not check["ok"]:
                print(
                    f"Start nicht bereit / not ready [{check['name']}]: {check['detail']}",
                    file=sys.stderr,
                )
        return 2
    # No default user's data is touched during --check. Normal start reuses the
    # existing host/setup; disabled/mismatched records are never reset here.
    from host import setup

    if args.setup:
        setup()
        return 0
    if report["setup_required"]:
        setup()
    from server import main as serve

    sys.argv = [sys.argv[0], "--port", str(args.port)]
    serve()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
