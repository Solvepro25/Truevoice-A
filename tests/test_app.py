import pytest
from fastapi.testclient import TestClient
from app.main import app, create_access_token

client = TestClient(app)

@pytest.fixture
def token():
    return create_access_token({"sub": "user123"})

def test_token_generation():
    res = client.post("/token", data={"user_id": "user123"})
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_enroll_missing_file(token):
    res = client.post(
        "/enroll",
        headers={"Authorization": f"Bearer {token}"},
        data={"user_id": "user123", "challenge_text": "hello"},
    )
    assert res.status_code == 422
