import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    # Since it's a redirect to /static/index.html, but mounted, it should serve the file
    # Actually, the redirect is to /static/index.html, but since mounted, it works.

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Club" in data
    assert "participants" in data["Basketball Club"]

def test_signup_success():
    # Sign up a new student
    response = client.post("/activities/Basketball%20Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]

    # Check if added
    response = client.get("/activities")
    data = response.json()
    assert "test@example.com" in data["Basketball Club"]["participants"]

def test_signup_already_signed_up():
    # Try to sign up again
    response = client.post("/activities/Basketball%20Club/signup?email=test@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]

def test_signup_invalid_activity():
    response = client.post("/activities/Invalid%20Activity/signup?email=test2@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_success():
    # First sign up
    client.post("/activities/Basketball%20Club/signup?email=test3@example.com")
    
    # Then unregister
    response = client.delete("/activities/Basketball%20Club/participants/test3@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]

    # Check if removed
    response = client.get("/activities")
    data = response.json()
    assert "test3@example.com" not in data["Basketball Club"]["participants"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Basketball%20Club/participants/notsigned@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]

def test_unregister_invalid_activity():
    response = client.delete("/activities/Invalid%20Activity/participants/test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]