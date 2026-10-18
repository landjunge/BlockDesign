"""Synthetic reference/file acceptance; no browser, model or personal store."""

import base64
import hashlib
import json
import struct
import sys
import unittest
import zlib
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from design_source import catalog, imported, png_size
from project_store import ContractError, ProjectStore, encoded
from project_store_test import body


def png(width=16, height=16):
    def chunk(kind, data):
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data))
        )

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress((b"\0" + b"\x44\x99\xaa" * width) * height))
        + chunk(b"IEND", b"")
    )


class Reference(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = ProjectStore(Path(self.temp.name))
        self.project = str(uuid4())
        self.image = png()
        self.html = b'<button id="left">Same</button><button id="right">Same</button><button id="dup"></button><button id="dup"></button><script>fetch("https://invalid.invalid/")</script>'

    def upload(self):
        return self.store.import_design(
            {
                "preview_base64": base64.b64encode(self.image).decode(),
                "html_base64": base64.b64encode(self.html).decode(),
            }
        )

    def test_static_ids_exact_hashes_and_preserved_original(self):
        value = self.upload()
        self.assertEqual(
            value["source"]["artifact_sha256"], hashlib.sha256(self.html).hexdigest()
        )
        self.assertEqual(value["source"]["source_commit"], None)
        self.assertEqual(
            self.store.raw(value["source"]["artifact_sha256"], 262144), self.html
        )
        self.assertEqual(
            self.store.preview(value["preview"]["artifact_sha256"]), self.image
        )
        self.assertEqual(
            [x["resolution"] for x in value["catalog"]],
            ["unique", "unique", "unresolved"],
        )
        self.assertEqual(
            catalog(b'<template><button id="inactive"></button></template>')[0][
                "resolution"
            ],
            "unresolved",
        )

    def test_save_reload_history_and_raw_artifact_dedup(self):
        value = self.upload()
        document = body()
        document["state"]["design"] = value
        first = self.store.save(self.project, document, {}, None)
        count = len(list(self.store.cas.root.iterdir()))
        document["state"]["revision"] = 1
        document["history"]["undo"] = [
            {
                "state": {
                    k: v
                    for k, v in body()["state"].items()
                    if k not in {"tasks", "ui", "revision"}
                },
                "label": "old inline",
            }
        ]
        second = self.store.save(self.project, document, {}, first["head"])
        loaded = ProjectStore(self.store.root).read(self.project)
        self.assertEqual(loaded["head"], second["head"])
        self.assertEqual(loaded["body"]["state"]["design"], value)
        self.assertEqual(
            len(list(self.store.cas.root.glob(value["preview"]["artifact_sha256"]))), 1
        )
        self.assertGreaterEqual(len(list(self.store.cas.root.iterdir())), count)

    def test_tampered_catalog_viewport_history_and_missing_image_fail_closed(self):
        value = self.upload()
        for key in ["catalog", "viewport", "missing", "historical"]:
            document = body()
            document["state"]["design"] = deepcopy(value)
            if key == "catalog":
                document["state"]["design"]["catalog"][2]["resolution"] = "unique"
            elif key == "viewport":
                document["state"]["design"]["source"]["reference_viewport"]["width"] = (
                    50
                )
            elif key == "missing":
                document["state"]["design"]["preview"]["artifact_sha256"] = "0" * 64
            else:
                prior = deepcopy(document["state"])
                prior["design"]["catalog"][2]["resolution"] = "unique"
                document["history"]["undo"] = [{"state": prior, "label": "forged"}]
            with self.subTest(key=key), self.assertRaises(ContractError):
                self.store.save(self.project, document, {}, None)

    def test_png_bounds_crc_trailing_html_path_and_symlink_refused(self):
        for raw in [
            b'<svg onload="alert(1)"></svg>',
            self.image + b"<script/>",
            self.image[:-4] + b"bad!",
            png(4096, 1025),
        ]:
            with self.subTest(size=len(raw)), self.assertRaises(ContractError):
                png_size(raw)
        value = self.upload()
        self.assertRaises(
            ContractError, self.store.preview, value["source"]["artifact_sha256"]
        )
        self.assertRaises(ContractError, self.store.preview, "../secret")
        target = Path(self.temp.name) / "outside.png"
        target.write_bytes(self.image)
        link = self.store.cas.root / ("f" * 64)
        link.symlink_to(target)
        self.assertRaises(ContractError, self.store.preview, "f" * 64)

    def test_size_ids_and_future_format_limits(self):
        self.assertRaises(
            ContractError, self.store.import_design, {"preview_base64": "a" * 1500000}
        )
        self.assertRaises(ContractError, catalog, ('<div id="x"></div>' * 257).encode())
        document = body()
        document["state"]["design"] = imported(self.image)
        document["state"]["design"]["version"] = 2
        self.assertRaises(
            ContractError, self.store.save, self.project, document, {}, None
        )

    def test_declared_hidpi_viewport_must_keep_aspect_ratio(self):
        value = imported(self.image, self.html, {"width": 8, "height": 8})
        self.assertEqual(
            value["source"]["reference_viewport"], {"width": 8, "height": 8}
        )
        self.assertRaises(
            ContractError, imported, self.image, self.html, {"width": 8, "height": 7}
        )
        self.assertRaises(
            ContractError, imported, self.image, self.html, {"width": True, "height": 1}
        )

    def test_future_reference_format_never_falls_back_to_an_older_writable_head(self):
        first = self.store.save(self.project, body(), {}, None)
        document = body()
        document["state"]["design"] = self.upload()
        self.store.save(self.project, document, {}, first["head"])
        commit_path = max((self.store.folder(self.project) / "commits").glob("*.json"))
        record = json.loads(commit_path.read_bytes())
        stored = self.store.read_blob(record["commit"]["chunks"]["document"])
        stored["design"]["version"] = 2
        record["commit"]["chunks"]["document"] = self.store.blob(stored)
        record["sha256"] = hashlib.sha256(encoded(record["commit"])).hexdigest()
        future_bytes = encoded(record)
        commit_path.write_bytes(future_bytes)
        with self.assertRaisesRegex(ContractError, "storageFormat"):
            ProjectStore(self.store.root).read(self.project)
        self.assertEqual(commit_path.read_bytes(), future_bytes)
        self.assertEqual(len(list(commit_path.parent.glob("*.json"))), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
