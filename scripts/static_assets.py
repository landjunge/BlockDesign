"""Bounded descriptor snapshots of the editor's public HTML/JS/CSS only."""

import os
import stat
from pathlib import Path

MAX_ASSET_BYTES = 4194304


class AssetUnavailable(ValueError):
    pass


def read_asset(project, path):
    """Never retranslate a checked URL or follow an asset-tree symlink.

    Owner-only files are private, including a mistakenly placed .js/.css file.
    Configuration/database/download/directory serving is not an asset feature.
    """
    if path == "/":
        parts = ["index.html"]
    else:
        if not isinstance(path, str) or not path.startswith("/") or "\x00" in path:
            raise AssetUnavailable
        parts = path[1:].split("/")
    if not parts or any(part in {"", ".", ".."} for part in parts):
        raise AssetUnavailable
    if parts != ["index.html"] and not (
        len(parts) >= 2
        and (
            parts[0] == "src"
            and parts[-1].endswith(".js")
            or parts[0] == "styles"
            and parts[-1].endswith(".css")
        )
    ):
        raise AssetUnavailable
    directory = None
    leaf = None
    try:
        directory = os.open(Path(project), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        for part in parts[:-1]:
            next_fd = os.open(
                part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory
            )
            os.close(directory)
            directory = next_fd
        leaf = os.open(
            parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
        )
        before = os.fstat(leaf)
        if (
            not stat.S_ISREG(before.st_mode)
            or not before.st_mode & 0o044
            or before.st_size > MAX_ASSET_BYTES
        ):
            raise AssetUnavailable
        with os.fdopen(leaf, "rb", closefd=False) as source:
            raw = source.read(MAX_ASSET_BYTES + 1)
        after = os.fstat(leaf)

        def identity(info):
            return (
                info.st_dev,
                info.st_ino,
                info.st_size,
                info.st_mtime_ns,
                info.st_ctime_ns,
            )

        if (
            len(raw) != before.st_size
            or len(raw) > MAX_ASSET_BYTES
            or identity(before) != identity(after)
        ):
            raise AssetUnavailable
        return raw, before.st_mtime
    except (OSError, ValueError):
        raise AssetUnavailable from None
    finally:
        if leaf is not None:
            os.close(leaf)
        if directory is not None:
            os.close(directory)
