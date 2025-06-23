import pytest
from fastapi.testclient import TestClient
from app.main import app, PrinterStatus

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_printer():
    printer_data = {
        "name": "Test Printer",
        "model": "Test Model",
        "ip_address": "192.168.1.100",
        "location": "Test Location",
        "status": "offline"
    }
    response = client.post("/printers", json=printer_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Printer"
    assert "id" in data

    # Cleanup
    printer_id = data["id"]
    response = client.get(f"/printers/{printer_id}")
    assert response.status_code == 200
    assert response.json()["id"] == printer_id

def test_get_nonexistent_printer():
    response = client.get("/printers/9999")
    assert response.status_code == 404

def test_list_printers():
    response = client.get("/printers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
