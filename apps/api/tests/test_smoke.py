from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "NEXUS AI"


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_creates_conversation() -> None:
    response = client.post("/api/v1/chat", json={"message": "Remember that I am learning FastAPI."})
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "mock"
    conversation_response = client.get(f"/api/v1/conversations/{body['conversation_id']}")
    assert conversation_response.status_code == 200
    assert len(conversation_response.json()["messages"]) == 2


def test_memory_crud() -> None:
    response = client.post(
        "/api/v1/memories",
        json={"category": "goal", "content": "Ship NEXUS", "importance": 0.9},
    )
    assert response.status_code == 201
    memory_id = response.json()["id"]
    list_response = client.get("/api/v1/memories")
    assert any(item["id"] == memory_id for item in list_response.json())
    delete_response = client.delete(f"/api/v1/memories/{memory_id}")
    assert delete_response.status_code == 204


def test_document_ingestion_and_retrieval(tmp_path: Path) -> None:
    file_path = tmp_path / "notes.txt"
    file_path.write_text("NEXUS stores knowledge chunks and can cite document snippets.", encoding="utf-8")
    with file_path.open("rb") as handle:
        upload_response = client.post(
            "/api/v1/documents",
            files={"file": ("notes.txt", handle, "text/plain")},
        )
    assert upload_response.status_code == 201
    ask_response = client.post("/api/v1/documents/ask", json={"question": "What does NEXUS store?"})
    assert ask_response.status_code == 200
    assert ask_response.json()["sources"]


def test_career_analysis() -> None:
    response = client.post(
        "/api/v1/career/analyze",
        json={
            "resume_text": "Python FastAPI SQL engineering",
            "job_description": "We need Python FastAPI AI engineering and testing skills",
        },
    )
    assert response.status_code == 201
    assert response.json()["heuristic"]
