#!/usr/bin/env python3
"""
Test script for the Printing Domain microservices.
This script tests the basic functionality of all services.
"""
import sys
import json
import time
import requests
from typing import Dict, Any, Optional

# Service URLs (update these if running in different ports)
SERVICES = {
    'printers': 'http://localhost:8000',
    'monitoring': 'http://localhost:8001',
    'calibration': 'http://localhost:8002'
}

def print_status(service: str, status: str, message: str = ""):
    """Print test status with consistent formatting"""
    status_pad = ' ' * (15 - len(service))
    print(f"{service}:{status_pad}[{status.upper()}] {message}")

def test_service_health() -> bool:
    """Test health check endpoints for all services"""
    all_healthy = True
    for service, base_url in SERVICES.items():
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print_status(service, "OK", f"Health check passed")
            else:
                print_status(service, "ERROR", f"Status code: {response.status_code}")
                all_healthy = False
        except requests.exceptions.RequestException as e:
            print_status(service, "ERROR", f"Connection failed: {str(e)}")
            all_healthy = False
    return all_healthy

def test_printers_service() -> bool:
    """Test Printers Service functionality"""
    base_url = SERVICES['printers']
    print("\nTesting Printers Service:")
    
    # Test creating a printer
    printer_data = {
        "name": "Test Printer",
        "model": "Test Model",
        "ip_address": "192.168.1.100",
        "location": "Test Location",
        "status": "offline"
    }
    
    try:
        # Create printer
        response = requests.post(f"{base_url}/printers", json=printer_data)
        if response.status_code != 201:
            print_status("CREATE", "ERROR", f"Failed to create printer: {response.text}")
            return False
        
        printer = response.json()
        printer_id = printer['id']
        print_status("CREATE", "OK", f"Created printer with ID: {printer_id}")
        
        # Get printer
        response = requests.get(f"{base_url}/printers/{printer_id}")
        if response.status_code != 200:
            print_status("GET", "ERROR", f"Failed to get printer: {response.text}")
            return False
        
        print_status("GET", "OK", "Successfully retrieved printer")
        
        # List printers
        response = requests.get(f"{base_url}/printers")
        if response.status_code != 200:
            print_status("LIST", "ERROR", f"Failed to list printers: {response.text}")
            return False
            
        printers = response.json()
        print_status("LIST", "OK", f"Found {len(printers)} printers")
        
        return True
        
    except Exception as e:
        print_status("ERROR", str(e))
        return False

def test_monitoring_service() -> bool:
    """Test Monitoring Service functionality"""
    base_url = SERVICES['monitoring']
    print("\nTesting Monitoring Service:")
    
    try:
        # Get system status
        response = requests.get(f"{base_url}/monitoring/status")
        if response.status_code != 200:
            print_status("STATUS", "ERROR", f"Failed to get system status: {response.text}")
            return False
            
        status = response.json()
        print_status("STATUS", "OK", f"System status: {status['status']}")
        
        # Create test alert
        alert_data = {
            "printer_id": "test-printer-1",
            "level": "warning",
            "message": "Low toner level",
            "details": {"toner_level": 10}
        }
        
        response = requests.post(
            f"{base_url}/monitoring/alerts",
            json=alert_data
        )
        
        if response.status_code != 201:
            print_status("ALERT", "ERROR", f"Failed to create alert: {response.text}")
            return False
            
        alert = response.json()
        print_status("ALERT", "OK", f"Created alert: {alert['id']}")
        
        # List alerts
        response = requests.get(f"{base_url}/monitoring/alerts")
        if response.status_code != 200:
            print_status("LIST ALERTS", "ERROR", f"Failed to list alerts: {response.text}")
            return False
            
        alerts = response.json()
        print_status("LIST ALERTS", "OK", f"Found {len(alerts)} alerts")
        
        return True
        
    except Exception as e:
        print_status("ERROR", str(e))
        return False

def test_calibration_service() -> bool:
    """Test Calibration Service functionality"""
    base_url = SERVICES['calibration']
    print("\nTesting Calibration Service:")
    
    try:
        # Create a calibration profile
        profile_data = {
            "name": "Test Profile",
            "description": "Test calibration profile",
            "printer_model": "Test Model",
            "parameters": {"test_param": 1.0},
            "is_default": True
        }
        
        response = requests.post(
            f"{base_url}/calibration/profiles",
            json=profile_data
        )
        
        if response.status_code != 201:
            print_status("PROFILE", "ERROR", f"Failed to create profile: {response.text}")
            return False
            
        profile = response.json()
        print_status("PROFILE", "OK", f"Created profile: {profile['id']}")
        
        # Start a calibration
        calibration_data = {
            "printer_id": "test-printer-1",
            "profile_id": profile['id'],
            "calibration_type": "automatic",
            "notes": "Test calibration"
        }
        
        response = requests.post(
            f"{base_url}/calibration/start",
            json=calibration_data
        )
        
        if response.status_code != 201:
            print_status("CALIBRATION", "ERROR", f"Failed to start calibration: {response.text}")
            return False
            
        calibration = response.json()
        print_status("CALIBRATION", "OK", f"Started calibration: {calibration['id']}")
        
        # Get calibration status
        response = requests.get(f"{base_url}/calibration/{calibration['id']}")
        if response.status_code != 200:
            print_status("STATUS", "ERROR", f"Failed to get calibration status: {response.text}")
            return False
            
        status = response.json()
        print_status("STATUS", "OK", f"Calibration status: {status['status']}")
        
        return True
        
    except Exception as e:
        print_status("ERROR", str(e))
        return False

def main():
    print("=== Printing Domain Microservices Test ===\n")
    
    # Wait for services to be ready
    print("Waiting for services to be ready...")
    time.sleep(5)
    
    # Test service health
    if not test_service_health():
        print("\nSome services are not healthy. Please check the services and try again.")
        sys.exit(1)
    
    # Test each service
    success = True
    success &= test_printers_service()
    success &= test_monitoring_service()
    success &= test_calibration_service()
    
    # Print final result
    print("\n=== Test Results ===")
    if success:
        print("✅ All tests passed successfully!")
    else:
        print("❌ Some tests failed. Please check the logs above for details.")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
