"""T1-03: adapter OIDC với IdP giả lập (httpx.MockTransport)."""

import base64
import json
import time
from typing import Any
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest

from app.adapters.oidc_identity import OidcError, OidcIdentityClient

ISSUER = "https://idp.example.test"


def _jwt(claims: dict[str, Any]) -> str:
    def part(obj: dict[str, Any]) -> str:
        return base64.urlsafe_b64encode(json.dumps(obj).encode()).rstrip(b"=").decode()

    return f"{part({'alg': 'RS256'})}.{part(claims)}.chu-ky"


class FakeIdp:
    def __init__(self) -> None:
        self.claims: dict[str, Any] = {}
        self.token_requests: list[dict[str, list[str]]] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/.well-known/openid-configuration":
            return httpx.Response(
                200,
                json={
                    "issuer": ISSUER,
                    "authorization_endpoint": f"{ISSUER}/authorize",
                    "token_endpoint": f"{ISSUER}/token",
                },
            )
        if request.url.path == "/token":
            self.token_requests.append(parse_qs(request.content.decode()))
            return httpx.Response(200, json={"id_token": _jwt(self.claims), "access_token": "a"})
        return httpx.Response(404)


@pytest.fixture
def idp() -> FakeIdp:
    return FakeIdp()


@pytest.fixture
def client(idp: FakeIdp) -> OidcIdentityClient:
    http = httpx.Client(transport=httpx.MockTransport(idp.handler))
    return OidcIdentityClient(ISSUER, "cwd-app", None, "http://app/cb", "openid email", http)


def _claims(**override: Any) -> dict[str, Any]:
    base = {
        "iss": ISSUER,
        "aud": "cwd-app",
        "exp": time.time() + 300,
        "nonce": "n1",
        "sub": "user-123",
        "email": "an.nguyen@example.test",
        "name": "Nguyễn An",
    }
    base.update(override)
    return base


def test_authorization_url_uses_pkce(client: OidcIdentityClient) -> None:
    url = client.authorization_url("s1", "n1", "challenge")
    query = parse_qs(urlsplit(url).query)
    assert url.startswith(f"{ISSUER}/authorize?")
    assert query["code_challenge"] == ["challenge"]
    assert query["code_challenge_method"] == ["S256"]
    assert query["state"] == ["s1"] and query["nonce"] == ["n1"]


def test_exchange_returns_identity_and_sends_verifier(
    client: OidcIdentityClient, idp: FakeIdp
) -> None:
    idp.claims = _claims()
    identity = client.exchange_code("code-1", "verifier-1", "n1")
    assert identity.subject == "user-123"
    assert identity.email == "an.nguyen@example.test"
    assert idp.token_requests[0]["code_verifier"] == ["verifier-1"]


@pytest.mark.parametrize(
    "override",
    [{"nonce": "khac"}, {"aud": "app-khac"}, {"iss": "https://gia-mao"}, {"exp": time.time() - 10}],
)
def test_exchange_rejects_invalid_token(
    client: OidcIdentityClient, idp: FakeIdp, override: dict[str, Any]
) -> None:
    idp.claims = _claims(**override)
    with pytest.raises(OidcError):
        client.exchange_code("code-1", "verifier-1", "n1")
