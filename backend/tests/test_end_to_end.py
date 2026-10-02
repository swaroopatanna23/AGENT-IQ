import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "AgentIQ backend is running"
    assert "agents" in data

def test_auth_workflow():
    user_payload = {
        "email": "test_engineer@agentiq.edu",
        "password": "Password123!",
        "full_name": "Test Engineer"
    }
    res = client.post("/api/v1/auth/register", json=user_payload)
    if res.status_code == 400:
        res = client.post("/api/v1/auth/login", json={"email": user_payload["email"], "password": user_payload["password"]})
    
    assert res.status_code == 200
    token = res.json()["access_token"]
    assert token

    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == user_payload["email"]

def test_sample_dataset_load_and_query():
    res = client.post("/api/v1/datasets/load-sample/students")
    assert res.status_code == 200
    dataset = res.json()
    dataset_id = dataset["id"]
    assert dataset_id > 0
    assert dataset["row_count"] == 60
    assert dataset["quality_score"] == 100.0

    q_payload = {
        "dataset_id": dataset_id,
        "question": "What is average marks by age?"
    }
    q_res = client.post("/api/v1/analysis/query", json=q_payload)
    assert q_res.status_code == 200
    q_data = q_res.json()
    assert q_data["schema"]["detected_intent"] == "group_comparison"
    assert "marks" in q_data["schema"]["target_columns"]
    assert "age" in q_data["schema"]["group_by"]
    assert len(q_data["result_data"]) > 0
    assert len(q_data["agent_trace"]) == 8
    assert "short_answer" in q_data["explanation"]

def test_data_sources_list():
    res = client.get("/api/v1/data-sources")
    assert res.status_code == 200
    sources = res.json()
    assert len(sources) >= 7
