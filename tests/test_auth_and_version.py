"""Bearer auth middleware (driven as raw ASGI) and version single-sourcing."""

import importlib.metadata

import pytest

import otx_mcp
from otx_mcp.server import BearerAuthMiddleware

TOKEN = "s3cret-token"


async def _call(scope, token=TOKEN):
    called = []
    sent = []

    async def app(scope, receive, send):
        called.append(scope["type"])

    async def receive():
        return {"type": "http.request"}

    async def send(message):
        sent.append(message)

    await BearerAuthMiddleware(app, token)(scope, receive, send)
    return called, sent


def _http(auth=None):
    headers = [] if auth is None else [(b"authorization", auth.encode())]
    return {"type": "http", "headers": headers}


async def test_correct_token_calls_app():
    called, sent = await _call(_http(f"Bearer {TOKEN}"))
    assert called == ["http"]
    assert sent == []


@pytest.mark.parametrize(
    "auth",
    [
        None,
        "Bearer wrong",
        f"Basic {TOKEN}",
        TOKEN,
        f"Bearer {TOKEN[:-1]}",
        f"Bearer {TOKEN}x",
        f"Bearer  {TOKEN}",
        "Bearer ",
        "",
    ],
)
async def test_bad_auth_rejected(auth):
    called, sent = await _call(_http(auth))
    assert called == []
    assert sent[0]["status"] == 401
    assert (b"content-type", b"application/json") in sent[0]["headers"]
    assert b"bearer" in sent[1]["body"]


async def test_non_ascii_header_rejected_not_crashing():
    scope = {"type": "http", "headers": [(b"authorization", "Bearer é".encode("latin-1"))]}
    called, sent = await _call(scope)
    assert called == []
    assert sent[0]["status"] == 401


async def test_lifespan_passes_through():
    called, sent = await _call({"type": "lifespan"})
    assert called == ["lifespan"]
    assert sent == []


def test_version_single_sourced():
    assert importlib.metadata.version("otx-mcp") == otx_mcp.__version__
