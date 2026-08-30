from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": f"smoke-{uuid4()}@example.com",
            "password": "smoke-test-password",
            "display_name": "Smoke Test",
        },
    )
    assert response.status_code == 201
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_root(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "NEXUS AI"


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_creates_conversation(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post("/api/v1/chat", headers=auth_headers, json={"message": "Remember that I am learning FastAPI."})
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "mock"
    conversation_response = client.get(f"/api/v1/conversations/{body['conversation_id']}", headers=auth_headers)
    assert conversation_response.status_code == 200
    assert len(conversation_response.json()["messages"]) == 2


def test_memory_crud(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/memories",
        headers=auth_headers,
        json={"category": "goal", "content": "Ship NEXUS", "importance": 0.9},
    )
    assert response.status_code == 201
    memory_id = response.json()["id"]
    list_response = client.get("/api/v1/memories", headers=auth_headers)
    assert any(item["id"] == memory_id for item in list_response.json())
    delete_response = client.delete(f"/api/v1/memories/{memory_id}", headers=auth_headers)
    assert delete_response.status_code == 204


def test_document_ingestion_and_retrieval(client: TestClient, tmp_path: Path, auth_headers: dict[str, str]) -> None:
    file_path = tmp_path / "notes.txt"
    file_path.write_text("NEXUS stores knowledge chunks and can cite document snippets.", encoding="utf-8")
    with file_path.open("rb") as handle:
        upload_response = client.post(
            "/api/v1/documents",
            headers=auth_headers,
            files={"file": ("notes.txt", handle, "text/plain")},
        )
    assert upload_response.status_code == 201
    ask_response = client.post("/api/v1/documents/ask", headers=auth_headers, json={"question": "What does NEXUS store?"})
    assert ask_response.status_code == 200
    assert ask_response.json()["sources"]


def test_career_analysis(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/career/analyze",
        headers=auth_headers,
        json={
            "resume_text": "Python FastAPI SQL engineering",
            "job_description": "We need Python FastAPI AI engineering and testing skills",
        },
    )
    assert response.status_code == 201
    assert response.json()["heuristic"]


def test_career_analysis_accepts_uploaded_sources(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.post(
        "/api/v1/career/analyze-upload",
        headers=auth_headers,
        data={"job_description": "Looking for Python and FastAPI experience"},
        files={"resume_file": ("resume.txt", b"Python FastAPI engineer", "text/plain")},
    )
    assert response.status_code == 201
    assert "python" in response.json()["matched_skills"]
