import pytest
from fastapi import status
from app.main import PrinterStatus

# Test data
TEST_PRINTER = {
    "name": "Test Printer",
    "model": "Test Model",
    "ip_address": "192.168.1.100",
    "location": "Test Location",
    "status": "offline"
}

UPDATED_PRINTER = {
    "name": "Updated Printer",
    "model": "Updated Model",
    "ip_address": "192.168.1.200",
    "location": "Updated Location",
    "status": "online"
}

class TestHealthCheck:
    def test_health_check(self, test_app):
        response = test_app.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ok"}

class TestPrintersCRUD:
    def test_create_printer(self, test_app):
        # Test creating a new printer
        response = test_app.post("/printers", json=TEST_PRINTER)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == TEST_PRINTER["name"]
        assert "id" in data
        
        # Store the printer ID for subsequent tests
        self.printer_id = data["id"]
    
    def test_get_printer(self, test_app):
        # Test getting the created printer
        response = test_app.get(f"/printers/{self.printer_id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == self.printer_id
        assert data["name"] == TEST_PRINTER["name"]
    
    def test_update_printer(self, test_app):
        # Test updating the printer
        response = test_app.put(
            f"/printers/{self.printer_id}", 
            json=UPDATED_PRINTER
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == UPDATED_PRINTER["name"]
        assert data["status"] == UPDATED_PRINTER["status"]
    
    def test_list_printers(self, test_app):
        # Test listing all printers
        response = test_app.get("/printers")
        assert response.status_code == status.HTTP_200_OK
        printers = response.json()
        assert isinstance(printers, list)
        assert len(printers) > 0
        assert any(p["id"] == self.printer_id for p in printers)
    
    def test_delete_printer(self, test_app):
        # Test deleting the printer
        response = test_app.delete(f"/printers/{self.printer_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify the printer was deleted
        response = test_app.get(f"/printers/{self.printer_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestErrorHandling:
    def test_get_nonexistent_printer(self, test_app):
        response = test_app.get("/printers/9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_invalid_printer(self, test_app):
        # Test with missing required fields
        invalid_printer = {"name": "Invalid Printer"}
        response = test_app.post("/printers", json=invalid_printer)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_nonexistent_printer(self, test_app):
        response = test_app.put("/printers/9999", json=UPDATED_PRINTER)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_nonexistent_printer(self, test_app):
        response = test_app.delete("/printers/9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
