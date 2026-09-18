import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_get_benchmarks():
    response = client.get("/api/benchmarks")
    assert response.status_code == 200
    data = response.json()
    assert "model1_map50" in data
    assert "model2_auc" in data
    assert "model3_spearman" in data
    assert "model4_regression_detection_rate" in data

def test_get_targets():
    response = client.get("/api/targets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    assert "v1_good" in data[0]["url"] or "v1_good" in data[0]["id"]

def test_get_memory_stats():
    response = client.get("/api/memory/stats")
    assert response.status_code == 200
    data = response.json()
    assert "runs_seen" in data
    assert len(data["detection_speed_curve"]) > 0
