"""
Test cases for the monitoring service API endpoints.

This module contains test cases for the monitoring service API endpoints,
including printer status, print jobs, alerts, and metrics.
"""
import pytest
from fastapi import status
from unittest.mock import patch
from datetime import datetime, timedelta

# Import test fixtures
from .conftest import (
    client,
    mock_http_client,
    test_printer,
    test_job,
    test_alert,
    test_metric
)

# Test print job endpoints

def test_create_print_job(client, test_job):
    """Test creating a new print job."""
    response = client.post("/print-jobs/", json={
        "printer_id": test_job["printer_id"],
        "file_name": test_job["file_name"],
        "file_size": test_job["file_size"],
        "estimated_duration": test_job["estimated_duration"]
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["printer_id"] == test_job["printer_id"]
    assert data["file_name"] == test_job["file_name"]
    assert data["status"] == "queued"
    assert "id" in data

def test_get_print_job(client, test_job):
    """Test retrieving a print job by ID."""
    # First create a job
    create_response = client.post("/print-jobs/", json={
        "printer_id": test_job["printer_id"],
        "file_name": test_job["file_name"],
        "file_size": test_job["file_size"],
        "estimated_duration": test_job["estimated_duration"]
    })
    job_id = create_response.json()["id"]
    
    # Then retrieve it
    response = client.get(f"/print-jobs/{job_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == job_id
    assert data["status"] == "queued"

def test_start_print_job(client, test_job):
    """Test starting a print job."""
    # Create a job
    create_response = client.post("/print-jobs/", json={
        "printer_id": test_job["printer_id"],
        "file_name": test_job["file_name"],
        "file_size": test_job["file_size"],
        "estimated_duration": test_job["estimated_duration"]
    })
    job_id = create_response.json()["id"]
    
    # Start the job
    response = client.post(f"/print-jobs/{job_id}/start")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "printing"
    assert data["start_time"] is not None

# Test printer status endpoints

def test_update_printer_status(client, test_printer):
    """Test updating a printer's status."""
    printer_id = test_printer["id"]
    status_data = {"status": "printing", "message": "Starting print job"}
    
    response = client.post(f"/printers/{printer_id}/status", json=status_data)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["printer_id"] == printer_id
    assert data["status"] == "printing"
    assert data["message"] == "Starting print job"

def test_get_printer_status(client, test_printer):
    """Test getting a printer's status."""
    printer_id = test_printer["id"]
    
    # First update the status to ensure it exists
    client.post(f"/printers/{printer_id}/status", 
               json={"status": "idle", "message": "Printer is idle"})
    
    # Then retrieve it
    response = client.get(f"/printers/{printer_id}/status")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "status" in data
    assert "message" in data
    assert "last_updated" in data

# Test alert endpoints

def test_create_alert(client, test_alert):
    """Test creating a new alert."""
    response = client.post("/alerts/", json={
        "printer_id": test_alert["printer_id"],
        "level": test_alert["level"],
        "message": test_alert["message"],
        "details": test_alert["details"]
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == test_alert["message"]
    assert data["status"] == "open"
    assert "id" in data

def test_list_alerts(client, test_alert):
    """Test listing all alerts."""
    # Create a test alert
    client.post("/alerts/", json={
        "printer_id": test_alert["printer_id"],
        "level": test_alert["level"],
        "message": test_alert["message"],
        "details": test_alert["details"]
    })
    
    # List all alerts
    response = client.get("/alerts/")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(alert["message"] == test_alert["message"] for alert in data)

# Test metrics endpoints

def test_record_metric(client, test_metric):
    """Test recording a new metric."""
    response = client.post("/metrics/", json={
        "printer_id": test_metric["printer_id"],
        "metric_type": test_metric["metric_type"],
        "value": test_metric["value"]
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["printer_id"] == test_metric["printer_id"]
    assert data["metric_type"] == test_metric["metric_type"]
    assert data["value"] == test_metric["value"]
    assert "id" in data

def test_get_metrics(client, test_metric):
    """Test querying metrics with filters."""
    # Record a test metric
    client.post("/metrics/", json={
        "printer_id": test_metric["printer_id"],
        "metric_type": test_metric["metric_type"],
        "value": test_metric["value"]
    })
    
    # Query metrics with filters
    response = client.get("/metrics/", params={
        "printer_id": test_metric["printer_id"],
        "metric_type": test_metric["metric_type"]
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(m["printer_id"] == test_metric["printer_id"] for m in data)
