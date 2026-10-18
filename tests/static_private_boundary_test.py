"""Synthetic local HTTP/loader regression only: no user host, model or secrets."""

import json
import sys
from functools import partial
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import server
import workflow_profile as profiles
from workflow_profile_test import own as own
from workflow_profile_test import private, save

MARKER = b"synthetic-private-fixture-not-a-real-secret"


@pytest.fixture
def assets(tmp_path, monkeypatch):
    project = tmp_path.resolve() / "editor"
    (project / "src").mkdir(parents=True)
    (project / "styles").mkdir()
    for relative, raw in [
        ("index.html", b"<!doctype html><title>Own fixture</title>"),
        ("src/app.js", b"export const own = true;"),
        ("styles/editor.css", b"body { color: teal; }"),
    ]:
        path = project / relative
        path.write_bytes(raw)
        path.chmod(0o644)
    for relative in ["src/private.js", "styles/private.css", "src/profile.json"]:
        path = project / relative
        path.write_bytes(MARKER)
        path.chmod(0o600)
    (project / "root-only.js").write_bytes(MARKER)
    (project / "root-only.js").chmod(0o644)
    outside = tmp_path.resolve() / "outside"
    outside.mkdir()
    (outside / "outside.css").write_bytes(MARKER)
    (outside / "outside.css").chmod(0o644)
    (project / "styles" / "linked.css").symlink_to(outside / "outside.css")
    (project / "styles" / "linked-dir").symlink_to(outside, target_is_directory=True)
    monkeypatch.setattr(server, "PROJECT", project)
    http = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(server.Handler, directory=str(project))
    )
    thread = Thread(target=http.serve_forever, daemon=True)
    thread.start()
    try:
        yield http
    finally:
        http.shutdown()
        http.server_close()
        thread.join(timeout=3)
        assert not thread.is_alive()


def fetch(http, path, method="GET", host=None):
    connection = HTTPConnection("127.0.0.1", http.server_port, timeout=3)
    try:
        headers = {} if host is None else {"Host": host}
        connection.request(method, path, headers=headers)
        response = connection.getresponse()
        status, headers, body = (
            response.status,
            dict(response.getheaders()),
            response.read(),
        )
        assert MARKER not in body
        return status, headers, body
    finally:
        connection.close()


@pytest.mark.parametrize(
    "path,content_type",
    [
        ("/", "text/html"),
        ("/index.html", "text/html"),
        ("/src/app.js", "javascript"),
        ("/styles/editor.css", "text/css"),
    ],
)
def test_real_http_normal_public_assets_keep_mime_and_security_headers(
    assets, path, content_type
):
    status, headers, body = fetch(assets, path)
    assert status == 200 and body
    assert content_type in headers["Content-Type"]
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in headers["Content-Security-Policy"]


@pytest.mark.parametrize(
    "path",
    [
        "/src/private.js",
        "/styles/private.css",
        "/src/profile.json",
        "/src/../root-only.js",
        "/src/%2e%2e/root-only.js",
        "/src/..%2froot-only.js",
        "/styles/.%2e/root-only.js",
        "/src/%2e%2e/%73rc/private.js",
        "/styles/linked.css",
        "/styles/linked-dir/outside.css",
        "/src/",
    ],
)
def test_real_http_private_traversal_and_symlink_paths_are_denied(assets, path):
    assert fetch(assets, path)[0] == 404


def test_head_uses_same_boundary_and_host_check_remains(assets):
    status, headers, body = fetch(assets, "/src/app.js", "HEAD")
    assert status == 200 and not body and int(headers["Content-Length"]) > 0
    assert fetch(assets, "/src/private.js", "HEAD")[0] == 404
    assert fetch(assets, "/src/app.js", host="foreign.invalid")[0] == 403


@pytest.mark.parametrize(
    "case",
    [
        "profile_src",
        "profile_styles",
        "config_src",
        "credentials_file",
        "tls_key",
        "tls_cert",
    ],
)
def test_loader_refuses_all_configured_private_files_inside_entire_project(
    own, monkeypatch, case
):
    project = own[0] / "editor"
    (project / "src").mkdir(parents=True)
    (project / "styles").mkdir()
    monkeypatch.setattr(profiles, "PROJECT", project)
    if case.startswith("profile_"):
        folder = "src" if case == "profile_src" else "styles"
        path = private(project / folder / "profile.json", json.dumps(own[3]))
    else:
        path = own[2]
        config = Path(own[3]["bridge_config"])
        if case == "config_src":
            relocated = private(project / "src" / "config.toml", config.read_text())
            own[3]["bridge_config"] = str(relocated)
        else:
            secret = private(
                project / "styles" / "configured-private-file", MARKER.decode()
            )
            # These are top-level Bridge settings, not principal settings.
            config.write_text(
                f"{case} = {json.dumps(str(secret))}\n" + config.read_text()
            )
        save(own)
    with pytest.raises(profiles.WorkflowProfileError) as error:
        profiles.load_workflow_profile(str(path))
    assert error.value.code == "workflow_profile_file"
    assert "outside the entire editor project" in str(error.value)
    assert MARKER.decode() not in str(error.value)
    assert str(project) not in str(error.value)
