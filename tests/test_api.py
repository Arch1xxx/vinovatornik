import json
import threading
import urllib.error
import urllib.request
from http.server import HTTPServer

import pytest

from vinovatornik.api import Handler, handle_blame
from vinovatornik.engine import blame


def test_ok_matches_engine():
    status, body = handle_blame({"text": "упал прод", "level": 2})
    assert status == 200
    assert body == blame("упал прод", 2).to_dict()


def test_default_level():
    status, body = handle_blame({"text": "упал прод"})
    assert status == 200
    assert body["level"] == 3


@pytest.mark.parametrize(
    "payload",
    [None, [], "text", {}, {"text": 5}, {"text": ""}, {"text": "x", "level": 9}, {"text": "x", "level": "3"}],
)
def test_bad_requests(payload):
    status, body = handle_blame(payload)
    assert status == 400
    assert "error" in body


@pytest.fixture
def server():
    srv = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()
    srv.server_close()


def _post(url, data: bytes):
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def test_http_roundtrip(server):
    status, body = _post(server + "/blame", json.dumps({"text": "в меня врезался грузовик"}).encode())
    assert status == 200
    assert body["culprit"]


def test_http_bad_json(server):
    status, _ = _post(server + "/blame", b"{oops")
    assert status == 400


def test_http_unknown_path(server):
    status, _ = _post(server + "/nope", b"{}")
    assert status == 404


def test_health(server):
    with urllib.request.urlopen(server + "/health") as resp:
        assert json.loads(resp.read()) == {"status": "ok"}
