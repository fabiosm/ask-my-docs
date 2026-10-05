from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_docs_loads():
    response = client.get("/docs")
    assert response.status_code == 200

def test_ask_without_question_returns_422():
    response = client.get("/ask")
    assert response.status_code == 422