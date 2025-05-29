import pytest
from fastapi.testclient import TestClient
from app import app
import time

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_add_review():
    review_data = {
        "text": "This movie was absolutely amazing! Great acting and storyline.",
        "sentiment": 1
    }
    response = client.post("/add_review", json=review_data)
    assert response.status_code == 200
    assert "task_id" in response.json()

def test_find_similar():
    similarity_data = {
        "text": "This movie was fantastic and entertaining!"
    }
    response = client.post("/find_similar", json=similarity_data)
    assert response.status_code == 200
    assert "task_id" in response.json()

def test_task_status():
    review_data = {
        "text": "Great movie with excellent cinematography.",
        "sentiment": 1
    }
    response = client.post("/add_review", json=review_data)
    task_id = response.json()["task_id"]
    
    time.sleep(2)
    
    status_response = client.get(f"/status/{task_id}")
    assert status_response.status_code == 200
    assert "task_id" in status_response.json()
    assert "status" in status_response.json()

if __name__ == "__main__":
    pytest.main([__file__]) 