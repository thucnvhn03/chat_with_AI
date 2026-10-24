"""Hàm tiện ích cho kiểm thử tích hợp qua API thật."""

from typing import Any

from fastapi.testclient import TestClient

from tests import pdf_factory
from tests.conftest import create_user, login


def upload(client: TestClient, *files: tuple[str, bytes]) -> list[dict[str, Any]]:
    response = client.post(
        "/api/v1/documents",
        files=[("files", (name, data, "application/pdf")) for name, data in files],
    )
    assert response.status_code == 200, response.text
    result: list[dict[str, Any]] = response.json()
    return result


def bd_client(make_client, runtime, login_name: str) -> TestClient:  # type: ignore[no-untyped-def]
    create_user(runtime, login_name, "bd")
    client: TestClient = make_client()
    login(client, login_name)
    return client


def ready_document(client: TestClient, worker, name: str, pages: list[str]) -> str:  # type: ignore[no-untyped-def]
    [result] = upload(client, (name, pdf_factory.make_pdf(pages)))
    assert result["status"] == "processing", result
    worker.drain()
    doc = client.get(f"/api/v1/documents/{result['id']}").json()
    assert doc["status"] == "ready", doc
    return str(result["id"])


def ask(client: TestClient, question: str, conversation_id: str | None = None) -> dict[str, Any]:
    if conversation_id is None:
        conversation_id = client.post("/api/v1/conversations").json()["id"]
    response = client.post(
        f"/api/v1/conversations/{conversation_id}/messages", json={"question": question}
    )
    assert response.status_code == 200, response.text
    body: dict[str, Any] = response.json()
    body["conversation_id"] = conversation_id
    return body
