"""Bounded inert reference import. Never renders HTML, opens a URL or runs code."""

import base64
import hashlib
import re
import struct
import zlib
from collections import Counter
from html.parser import HTMLParser

from ai_adapter import ContractError, require

HASH = re.compile(r"[a-f0-9]{64}\Z")
MAX_PNG = 1048576
MAX_HTML = 262144
MAX_PIXELS = 4194304


def png_size(raw):
    require(
        isinstance(raw, bytes)
        and 33 <= len(raw) <= MAX_PNG
        and raw[:8] == b"\x89PNG\r\n\x1a\n",
        "designInvalidPreview",
    )
    offset, compressed, size, ended, chunks = 8, bytearray(), None, False, 0
    while offset + 12 <= len(raw):
        length = int.from_bytes(raw[offset : offset + 4], "big")
        kind = raw[offset + 4 : offset + 8]
        require(
            length <= MAX_PNG and offset + 12 + length <= len(raw),
            "designInvalidPreview",
        )
        data = raw[offset + 8 : offset + 8 + length]
        crc = int.from_bytes(raw[offset + 8 + length : offset + 12 + length], "big")
        require(zlib.crc32(kind + data) == crc, "designInvalidPreview")
        chunks += 1
        require(chunks <= 1024, "designInvalidPreview")
        if size is None:
            require(kind == b"IHDR" and length == 13, "designInvalidPreview")
            width, height, depth, color, compression, filtering, interlace = (
                struct.unpack(">IIBBBBB", data)
            )
            require(
                0 < width <= 4096
                and 0 < height <= 4096
                and width * height <= MAX_PIXELS
                and depth == 8
                and color in (2, 6)
                and compression == filtering == interlace == 0,
                "designInvalidPreview",
            )
            size = {"width": width, "height": height}
            expected = height * (1 + width * (3 if color == 2 else 4))
        elif kind == b"IHDR":
            raise ContractError("designInvalidPreview")
        elif kind == b"IDAT":
            compressed.extend(data)
        elif kind == b"IEND":
            require(length == 0 and offset + 12 == len(raw), "designInvalidPreview")
            ended = True
            break
        elif (
            kind in {b"acTL", b"fcTL", b"fdAT"}
            or kind[:1].isupper()
            and kind != b"PLTE"
        ):
            raise ContractError("designInvalidPreview")
        offset += length + 12
    require(ended and compressed, "designInvalidPreview")
    try:
        decoder = zlib.decompressobj()
        pixels = decoder.decompress(compressed, expected + 1)
        require(
            len(pixels) == expected
            and decoder.eof
            and not decoder.unused_data
            and not decoder.unconsumed_tail,
            "designInvalidPreview",
        )
    except zlib.error:
        raise ContractError("designInvalidPreview") from None
    return size


class ElementCatalog(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items, self.inert = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in {"template", "noscript"}:
            self.inert += 1
        values = [value for key, value in attrs if key == "id"]
        if values:
            require(
                len(self.items) < 256
                and len(tag) <= 256
                and len(values) == 1
                and isinstance(values[0], str)
                and 0 < len(values[0]) <= 256
                and not any(ord(c) < 32 for c in values[0]),
                "designElementLimit",
            )
            self.items.append((values[0], tag, not self.inert))

    def handle_endtag(self, tag):
        if tag in {"template", "noscript"}:
            self.inert = max(0, self.inert - 1)


def catalog(raw):
    require(isinstance(raw, bytes) and 0 < len(raw) <= MAX_HTML, "designSourceLimit")
    try:
        text = raw.decode("utf-8", errors="strict")
        require("\x00" not in text, "designInvalidSource")
        parser = ElementCatalog()
        parser.feed(text)
        parser.close()
    except ContractError:
        raise
    except (UnicodeError, ValueError):
        raise ContractError("designInvalidSource") from None
    counts = Counter(item[0] for item in parser.items)
    return [
        {
            "element_id": "id:" + identity,
            "tag": next(tag for key, tag, _ in parser.items if key == identity),
            "count": count,
            "resolution": "unique"
            if count == 1
            and all(eligible for key, _, eligible in parser.items if key == identity)
            else "unresolved",
        }
        for identity, count in counts.items()
    ]


def decode_upload(value, limit):
    require(
        isinstance(value, str) and len(value) <= (limit + 2) // 3 * 4,
        "designSourceLimit",
    )
    try:
        raw = base64.b64decode(value, validate=True)
    except ValueError:
        raise ContractError("designInvalidSource") from None
    require(0 < len(raw) <= limit, "designSourceLimit")
    return raw


def validate_design(value, box_ids):
    if value is None:
        return
    require(
        isinstance(value, dict)
        and set(value) == {"version", "source", "preview", "catalog", "bindings"}
        and type(value["version"]) is int
        and value["version"] == 1,
        "designInvalidSource",
    )
    source, preview = value["source"], value["preview"]
    require(
        isinstance(source, dict)
        and set(source)
        == {"artifact_sha256", "media_type", "source_commit", "reference_viewport"}
        and HASH.fullmatch(str(source["artifact_sha256"]))
        and source["media_type"] in {"text/html", "image/png"}
        and source["source_commit"] is None,
        "designInvalidSource",
    )
    require(
        isinstance(preview, dict)
        and set(preview) == {"artifact_sha256", "media_type", "rendering_mode"}
        and HASH.fullmatch(str(preview["artifact_sha256"]))
        and preview["media_type"] == "image/png"
        and preview["rendering_mode"] == "inert-image",
        "designInvalidPreview",
    )
    viewport = source["reference_viewport"]
    require(
        isinstance(viewport, dict)
        and set(viewport) == {"width", "height"}
        and all(type(v) is int and 0 < v <= 32768 for v in viewport.values()),
        "designInvalidPreview",
    )
    entries, bindings = value["catalog"], value["bindings"]
    require(
        isinstance(entries, list)
        and len(entries) <= 256
        and isinstance(bindings, dict)
        and len(bindings) <= 256
        and set(bindings) <= set(box_ids),
        "designElementLimit",
    )
    seen = set()
    for entry in entries:
        require(
            isinstance(entry, dict)
            and set(entry) == {"element_id", "tag", "count", "resolution"}
            and isinstance(entry["element_id"], str)
            and 0 < len(entry["element_id"]) <= 259
            and isinstance(entry["tag"], str)
            and len(entry["tag"]) <= 256
            and type(entry["count"]) is int
            and 1 <= entry["count"] <= 256
            and entry["resolution"] in {"unique", "unresolved"},
            "designInvalidSource",
        )
        require(entry["element_id"] not in seen, "designInvalidSource")
        seen.add(entry["element_id"])
    for binding in bindings.values():
        require(
            isinstance(binding, dict)
            and set(binding) == {"action", "source_element"}
            and binding["action"] in {"move", "replace", "new"},
            "designInvalidSource",
        )
        ref = binding["source_element"]
        if binding["action"] == "new":
            require(ref is None, "designInvalidSource")
        else:
            require(
                isinstance(ref, dict)
                and set(ref) == {"artifact_sha256", "element_id", "resolution"}
                and HASH.fullmatch(str(ref["artifact_sha256"]))
                and (
                    ref["element_id"] is None
                    or isinstance(ref["element_id"], str)
                    and len(ref["element_id"]) <= 512
                )
                and ref["resolution"] in {"unique", "unresolved"},
                "designInvalidSource",
            )
            if ref["resolution"] == "unique":
                require(
                    isinstance(ref["element_id"], str) and bool(ref["element_id"]),
                    "designInvalidSource",
                )
                if ref["artifact_sha256"] == source["artifact_sha256"]:
                    require(
                        any(
                            item["element_id"] == ref["element_id"]
                            and item["count"] == 1
                            and item["resolution"] == "unique"
                            for item in entries
                        ),
                        "designForeignElement",
                    )


def imported(preview, original=None, reference_viewport=None):
    size = png_size(preview)
    viewport = size if reference_viewport is None else reference_viewport
    require(
        isinstance(viewport, dict)
        and set(viewport) == {"width", "height"}
        and all(type(v) is int and 0 < v <= 32768 for v in viewport.values())
        and viewport["width"] * size["height"] == viewport["height"] * size["width"],
        "designViewportMismatch",
    )
    source = preview if original is None else original
    entries = [] if original is None else catalog(original)
    sha = lambda raw: hashlib.sha256(raw).hexdigest()
    return {
        "version": 1,
        "source": {
            "artifact_sha256": sha(source),
            "media_type": "image/png" if original is None else "text/html",
            "source_commit": None,
            "reference_viewport": viewport,
        },
        "preview": {
            "artifact_sha256": sha(preview),
            "media_type": "image/png",
            "rendering_mode": "inert-image",
        },
        "catalog": entries,
        "bindings": {},
    }
