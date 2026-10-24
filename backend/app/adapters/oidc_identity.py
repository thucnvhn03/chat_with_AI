"""Adapter OIDC: Authorization Code + PKCE với IdP của tổ chức (DQ-003 = OIDC, T1-03).

ID token được nhận trực tiếp từ token endpoint qua TLS, nên theo OpenID Connect Core 3.1.3.7 việc xác
thực TLS của máy chủ thay cho kiểm tra chữ ký. Adapter vẫn kiểm `iss`, `aud`, `exp` và `nonce`.
Vai trò KHÔNG lấy từ IdP.
"""

import base64
import json
import time
from typing import Any
from urllib.parse import urlencode

import httpx

from app.ports.identity import OidcIdentity


class OidcError(Exception):
    pass


def _decode_jwt_payload(token: str) -> dict[str, Any]:
    try:
        payload = token.split(".")[1]
        padded = payload + "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(padded))
    except (IndexError, ValueError) as exc:
        raise OidcError("id_token_malformed") from exc
    if not isinstance(data, dict):
        raise OidcError("id_token_malformed")
    return data


class OidcIdentityClient:
    def __init__(
        self,
        issuer: str,
        client_id: str,
        client_secret: str | None,
        redirect_uri: str,
        scopes: str,
        http: httpx.Client | None = None,
    ) -> None:
        self._issuer = issuer.rstrip("/")
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri
        self._scopes = scopes
        self._http = http or httpx.Client(timeout=10)
        self._metadata: dict[str, Any] | None = None

    def _discovery(self) -> dict[str, Any]:
        if self._metadata is None:
            response = self._http.get(f"{self._issuer}/.well-known/openid-configuration")
            response.raise_for_status()
            self._metadata = response.json()
        return self._metadata

    def authorization_url(self, state: str, nonce: str, code_challenge: str) -> str:
        params = {
            "response_type": "code",
            "client_id": self._client_id,
            "redirect_uri": self._redirect_uri,
            "scope": self._scopes,
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        return f"{self._discovery()['authorization_endpoint']}?{urlencode(params)}"

    def exchange_code(self, code: str, code_verifier: str, nonce: str) -> OidcIdentity:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._redirect_uri,
            "client_id": self._client_id,
            "code_verifier": code_verifier,
        }
        if self._client_secret:
            data["client_secret"] = self._client_secret
        response = self._http.post(self._discovery()["token_endpoint"], data=data)
        if response.status_code != 200:
            raise OidcError(f"token_endpoint_{response.status_code}")
        id_token = response.json().get("id_token")
        if not isinstance(id_token, str):
            raise OidcError("id_token_missing")

        claims = _decode_jwt_payload(id_token)
        audience = claims.get("aud")
        audiences = audience if isinstance(audience, list) else [audience]
        if str(claims.get("iss", "")).rstrip("/") != self._issuer:
            raise OidcError("issuer_mismatch")
        if self._client_id not in audiences:
            raise OidcError("audience_mismatch")
        if float(claims.get("exp", 0)) < time.time():
            raise OidcError("id_token_expired")
        if claims.get("nonce") != nonce:
            raise OidcError("nonce_mismatch")
        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject:
            raise OidcError("subject_missing")
        email = claims.get("email")
        name = claims.get("name")
        return OidcIdentity(
            subject=subject,
            email=email if isinstance(email, str) else None,
            name=name if isinstance(name, str) else None,
        )
