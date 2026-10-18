"""Optional trusted startup profile, never browser configuration or a task queue."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path
from uuid import UUID

PROJECT = Path(__file__).resolve().parents[1]
MAX_PROFILE_BYTES = 65536
MAX_PROJECTS = 32
MESSAGES = {
    "workflow_profile_file": "Private absolute regular file outside the entire editor project required (owner-only, no symlinks) / private absolute Datei außerhalb des gesamten Editorprojekts erforderlich (nur Eigentümer, keine Symlinks).",
    "workflow_profile_schema": "Invalid bounded workflow profile / ungültiges begrenztes Workflowprofil.",
    "workflow_profile_sdk": "Existing compatible KiraBridge SDK is missing; select an existing BD_PYTHON environment, no automatic installation / kompatibles vorhandenes KiraBridge-SDK fehlt; vorhandene BD_PYTHON-Umgebung wählen.",
    "workflow_profile_bridge": "Existing Bridge config/principal/credentials unavailable or incompatible; inspect locally without exposing secrets / bestehende Bridge-Konfiguration, Principal oder Zugang nicht nutzbar; lokal ohne Geheimnisausgabe prüfen.",
    "workflow_profile_project": "Project CWD or fixed filenames invalid/outside principal roots / Projekt-CWD oder feste Dateinamen ungültig bzw. außerhalb der Principal-Roots.",
}


class WorkflowProfileError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(MESSAGES[code])


def selected_profile(option=None):
    return (
        option if option is not None else os.environ.get("BD_WORKFLOW_PROFILE") or None
    )


def external_private_file(value, *, private=True):
    """Check configured private files before their SDK reader can use them."""
    try:
        path = Path(value)
        if (
            not path.is_absolute()
            or path != path.resolve(strict=True)
            or path.is_relative_to(PROJECT.resolve())
        ):
            raise ValueError
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if (
                not stat.S_ISREG(info.st_mode)
                or private
                and (info.st_uid != os.getuid() or info.st_mode & 0o077)
            ):
                raise ValueError
        return path
    except (OSError, ValueError, TypeError, RuntimeError):
        raise WorkflowProfileError("workflow_profile_file") from None


def private_bytes(value):
    """Read once, bounded and descriptor-checked; never chmod/create a user file."""
    try:
        path = external_private_file(value)
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as source:
            before = os.fstat(source.fileno())
            if (
                not stat.S_ISREG(before.st_mode)
                or before.st_uid != os.getuid()
                or before.st_mode & 0o077
                or before.st_size > MAX_PROFILE_BYTES
            ):
                raise ValueError
            raw = source.read(MAX_PROFILE_BYTES + 1)
            after = os.fstat(source.fileno())
            if (
                len(raw) != before.st_size
                or len(raw) > MAX_PROFILE_BYTES
                or (
                    before.st_dev,
                    before.st_ino,
                    before.st_size,
                    before.st_mtime_ns,
                    before.st_ctime_ns,
                )
                != (
                    after.st_dev,
                    after.st_ino,
                    after.st_size,
                    after.st_mtime_ns,
                    after.st_ctime_ns,
                )
            ):
                raise ValueError
            return raw
    except (OSError, ValueError, TypeError, RuntimeError):
        raise WorkflowProfileError("workflow_profile_file") from None


def unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def load_workflow_profile(option=None):
    """Construct the existing fixed client without network, database or dispatch.

    None keeps the editor's previous unconfigured behavior. No browser input can
    invoke this function or choose a principal/configuration/source path.
    """
    path = selected_profile(option)
    if path is None:
        return None
    raw = private_bytes(path)
    try:
        value = json.loads(raw, object_pairs_hook=unique_fields)
        if (
            not isinstance(value, dict)
            or set(value) != {"format", "bridge_config", "principal", "projects"}
            or value["format"] != "blockdesigner.workflow-profile.v1"
            or not isinstance(value["bridge_config"], str)
            or not isinstance(value["principal"], str)
            or re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value["principal"]) is None
            or not isinstance(value["projects"], dict)
            or not 1 <= len(value["projects"]) <= MAX_PROJECTS
        ):
            raise ValueError
        profiles = value["projects"]
        for project, profile in profiles.items():
            if (
                str(UUID(project)) != project
                or not isinstance(profile, dict)
                or set(profile) != {"cwd", "source_file", "preview_file"}
            ):
                raise ValueError
            if (
                not isinstance(profile["cwd"], str)
                or not 0 < len(profile["cwd"]) <= 4096
            ):
                raise ValueError
            for key in ("source_file", "preview_file"):
                name = profile[key]
                if (
                    not isinstance(name, str)
                    or not 0 < len(name) <= 255
                    or Path(name).name != name
                    or name in {".", ".."}
                    or any(ord(c) < 32 for c in name)
                ):
                    raise ValueError
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise WorkflowProfileError("workflow_profile_schema") from None

    config_raw = private_bytes(value["bridge_config"])
    try:
        from design_workflow import DesignWorkflow, FixedBridgeClient
        from kirabridge.bridge_core.config import load_config
        from kirabridge.filesystem_manager import PathScope
    except ImportError:
        raise WorkflowProfileError("workflow_profile_sdk") from None
    try:
        config = load_config(value["bridge_config"])
        if (
            config._source_sha256 != hashlib.sha256(config_raw).hexdigest()
            or private_bytes(value["bridge_config"]) != config_raw
            or value["principal"] not in config.principals
        ):
            raise ValueError
        for field in ("credentials_file", "tls_key", "tls_cert"):
            configured = getattr(config, field, None)
            if configured is not None:
                external_private_file(configured, private=field != "tls_cert")
        client = FixedBridgeClient(config, value["principal"])
    except WorkflowProfileError:
        raise
    except ImportError:
        raise WorkflowProfileError("workflow_profile_sdk") from None
    except Exception:
        # Never expose validation exceptions, environment values or credentials.
        raise WorkflowProfileError("workflow_profile_bridge") from None
    workflow = DesignWorkflow(None, client, profiles)
    try:
        scope = PathScope(
            config.principals[value["principal"]].roots,
            excluded=[str(config.state_path)],
        )
        for project in profiles:
            pinned = workflow.operator_profile(project)
            with scope.directory(pinned["cwd"]) as directory:
                info = os.fstat(directory)
                if (info.st_dev, info.st_ino) != (
                    pinned["cwd_device"],
                    pinned["cwd_inode"],
                ):
                    raise ValueError
    except Exception:
        raise WorkflowProfileError("workflow_profile_project") from None
    return client, profiles
