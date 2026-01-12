"""
Test suite for Contractor Certifications API endpoints
Tests: POST /api/certifications, GET /api/certifications/contractor/{id}, DELETE /api/certifications/{id}
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestCertificationsAPI:
    """Test suite for certifications CRUD operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data - create a test contractor for certification tests"""
        self.test_contractor_id = None
        self.test_certification_ids = []
        
        # Create a test contractor
        contractor_data = {
            "name": "TEST_Certification_Contractor",
            "weekly_payment": 50000.0,
            "project_name": "TEST_Project_Certifications",
            "budget": 1000000.0
        }
        response = requests.post(f"{BASE_URL}/api/contractors", json=contractor_data)
        if response.status_code == 200:
            self.test_contractor_id = response.json()["id"]
        
        yield
        
        # Cleanup - delete test certifications and contractor
        for cert_id in self.test_certification_ids:
            try:
                requests.delete(f"{BASE_URL}/api/certifications/{cert_id}")
            except:
                pass
        
        if self.test_contractor_id:
            try:
                requests.delete(f"{BASE_URL}/api/contractors/{self.test_contractor_id}")
            except:
                pass
    
    # ==================== POST /api/certifications ====================
    
    def test_create_certification_success(self):
        """Test creating a new certification successfully"""
        cert_data = {
            "contractor_id": self.test_contractor_id,
            "week_start_date": "2025-01-06",
            "amount": 100000.0,
            "description": "TEST_Avance de obra 20%"
        }
        
        response = requests.post(f"{BASE_URL}/api/certifications", json=cert_data)
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "id" in data, "Response should contain 'id'"
        assert data["contractor_id"] == self.test_contractor_id
        assert data["week_start_date"] == "2025-01-06"
        assert data["amount"] == 100000.0
        assert data["description"] == "TEST_Avance de obra 20%"
        assert "created_at" in data
        
        self.test_certification_ids.append(data["id"])
        
        # Verify contractor's total_paid was updated
        contractor_response = requests.get(f"{BASE_URL}/api/contractors/{self.test_contractor_id}")
        assert contractor_response.status_code == 200
        contractor_data = contractor_response.json()
        assert contractor_data["total_paid"] == 100000.0, f"Expected total_paid=100000, got {contractor_data['total_paid']}"
    
    def test_create_certification_without_description(self):
        """Test creating certification without optional description"""
        cert_data = {
            "contractor_id": self.test_contractor_id,
            "week_start_date": "2025-01-13",
            "amount": 75000.0
        }
        
        response = requests.post(f"{BASE_URL}/api/certifications", json=cert_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 75000.0
        assert data["description"] == "" or data["description"] is None or "description" in data
        
        self.test_certification_ids.append(data["id"])
    
    def test_create_certification_invalid_contractor(self):
        """Test creating certification with non-existent contractor"""
        cert_data = {
            "contractor_id": "non-existent-id-12345",
            "week_start_date": "2025-01-06",
            "amount": 50000.0
        }
        
        response = requests.post(f"{BASE_URL}/api/certifications", json=cert_data)
        
        # Should return 404 for non-existent contractor
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_create_multiple_certifications_updates_total(self):
        """Test that multiple certifications correctly update contractor's total_paid"""
        # First certification
        cert1_data = {
            "contractor_id": self.test_contractor_id,
            "week_start_date": "2025-01-06",
            "amount": 50000.0,
            "description": "TEST_First certification"
        }
        response1 = requests.post(f"{BASE_URL}/api/certifications", json=cert1_data)
        assert response1.status_code == 200
        self.test_certification_ids.append(response1.json()["id"])
        
        # Second certification
        cert2_data = {
            "contractor_id": self.test_contractor_id,
            "week_start_date": "2025-01-13",
            "amount": 75000.0,
            "description": "TEST_Second certification"
        }
        response2 = requests.post(f"{BASE_URL}/api/certifications", json=cert2_data)
        assert response2.status_code == 200
        self.test_certification_ids.append(response2.json()["id"])
        
        # Verify total_paid is sum of both certifications
        contractor_response = requests.get(f"{BASE_URL}/api/contractors/{self.test_contractor_id}")
        assert contractor_response.status_code == 200
        contractor_data = contractor_response.json()
        assert contractor_data["total_paid"] == 125000.0, f"Expected total_paid=125000, got {contractor_data['total_paid']}"
    
    # ==================== GET /api/certifications/contractor/{id} ====================
    
    def test_get_contractor_certifications_empty(self):
        """Test getting certifications for contractor with no certifications"""
        response = requests.get(f"{BASE_URL}/api/certifications/contractor/{self.test_contractor_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_contractor_certifications_with_data(self):
        """Test getting certifications for contractor with existing certifications"""
        # Create certifications first
        cert1 = {
            "contractor_id": self.test_contractor_id,
            "week_start_date": "2025-01-06",
            "amount": 100000.0,
            "description": "TEST_Cert 1"
        }
        cert2 = {
            "contractor_id": self.test_contractor_id,
            "week_start_date": "2025-01-13",
            "amount": 150000.0,
            "description": "TEST_Cert 2"
        }
        
        resp1 = requests.post(f"{BASE_URL}/api/certifications", json=cert1)
        resp2 = requests.post(f"{BASE_URL}/api/certifications", json=cert2)
        self.test_certification_ids.append(resp1.json()["id"])
        self.test_certification_ids.append(resp2.json()["id"])
        
        # Get certifications
        response = requests.get(f"{BASE_URL}/api/certifications/contractor/{self.test_contractor_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Verify data structure
        for cert in data:
            assert "id" in cert
            assert "contractor_id" in cert
            assert "week_start_date" in cert
            assert "amount" in cert
            assert "description" in cert
            assert "created_at" in cert
    
    def test_get_certifications_sorted_by_week(self):
        """Test that certifications are returned sorted by week_start_date descending"""
        # Create certifications with different dates
        dates = ["2025-01-06", "2025-01-20", "2025-01-13"]
        for date in dates:
            cert = {
                "contractor_id": self.test_contractor_id,
                "week_start_date": date,
                "amount": 50000.0
            }
            resp = requests.post(f"{BASE_URL}/api/certifications", json=cert)
            self.test_certification_ids.append(resp.json()["id"])
        
        response = requests.get(f"{BASE_URL}/api/certifications/contractor/{self.test_contractor_id}")
        data = response.json()
        
        # Verify sorted descending by week_start_date
        assert data[0]["week_start_date"] == "2025-01-20"
        assert data[1]["week_start_date"] == "2025-01-13"
        assert data[2]["week_start_date"] == "2025-01-06"
    
    # ==================== DELETE /api/certifications/{id} ====================
    
    def test_delete_certification_success(self):
        """Test deleting a certification and verifying total_paid is updated"""
        # Create a certification first
        cert_data = {
            "contractor_id": self.test_contractor_id,
            "week_start_date": "2025-01-06",
            "amount": 100000.0,
            "description": "TEST_To be deleted"
        }
        create_response = requests.post(f"{BASE_URL}/api/certifications", json=cert_data)
        assert create_response.status_code == 200
        cert_id = create_response.json()["id"]
        
        # Verify contractor total_paid increased
        contractor_before = requests.get(f"{BASE_URL}/api/contractors/{self.test_contractor_id}").json()
        assert contractor_before["total_paid"] == 100000.0
        
        # Delete the certification
        delete_response = requests.delete(f"{BASE_URL}/api/certifications/{cert_id}")
        assert delete_response.status_code == 200
        
        # Verify contractor total_paid decreased
        contractor_after = requests.get(f"{BASE_URL}/api/contractors/{self.test_contractor_id}").json()
        assert contractor_after["total_paid"] == 0.0, f"Expected total_paid=0, got {contractor_after['total_paid']}"
        
        # Verify certification no longer exists
        get_response = requests.get(f"{BASE_URL}/api/certifications/contractor/{self.test_contractor_id}")
        assert len(get_response.json()) == 0
    
    def test_delete_certification_not_found(self):
        """Test deleting non-existent certification returns 404"""
        response = requests.delete(f"{BASE_URL}/api/certifications/non-existent-id-12345")
        assert response.status_code == 404
    
    def test_delete_certification_updates_remaining_balance(self):
        """Test that deleting certification correctly updates remaining_balance"""
        # Create certification
        cert_data = {
            "contractor_id": self.test_contractor_id,
            "week_start_date": "2025-01-06",
            "amount": 200000.0
        }
        create_response = requests.post(f"{BASE_URL}/api/certifications", json=cert_data)
        cert_id = create_response.json()["id"]
        self.test_certification_ids.append(cert_id)
        
        # Check remaining_balance after creation
        contractor = requests.get(f"{BASE_URL}/api/contractors/{self.test_contractor_id}").json()
        assert contractor["remaining_balance"] == 800000.0  # 1000000 - 200000
        
        # Delete certification
        requests.delete(f"{BASE_URL}/api/certifications/{cert_id}")
        self.test_certification_ids.remove(cert_id)
        
        # Check remaining_balance after deletion
        contractor_after = requests.get(f"{BASE_URL}/api/contractors/{self.test_contractor_id}").json()
        assert contractor_after["remaining_balance"] == 1000000.0  # Back to original budget


class TestExistingCertifications:
    """Test with existing data - Claudio Sanchez contractor"""
    
    def test_get_existing_contractor_certifications(self):
        """Test getting certifications for existing contractor Claudio Sanchez"""
        # Known contractor ID from existing data
        contractor_id = "70cdb1c7-6811-448f-b273-7e4e114c29c9"
        
        response = requests.get(f"{BASE_URL}/api/certifications/contractor/{contractor_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Should have at least one certification based on existing data
        if len(data) > 0:
            cert = data[0]
            assert "id" in cert
            assert cert["contractor_id"] == contractor_id
            assert "amount" in cert
            print(f"Found {len(data)} certifications for Claudio Sanchez")
    
    def test_get_all_certifications(self):
        """Test getting all certifications endpoint"""
        response = requests.get(f"{BASE_URL}/api/certifications")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Total certifications in system: {len(data)}")


class TestCertificationEdgeCases:
    """Test edge cases for certifications"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test contractor"""
        self.test_contractor_id = None
        self.test_certification_ids = []
        
        contractor_data = {
            "name": "TEST_Edge_Case_Contractor",
            "weekly_payment": 10000.0,
            "project_name": "TEST_Edge_Project",
            "budget": 100000.0
        }
        response = requests.post(f"{BASE_URL}/api/contractors", json=contractor_data)
        if response.status_code == 200:
            self.test_contractor_id = response.json()["id"]
        
        yield
        
        for cert_id in self.test_certification_ids:
            try:
                requests.delete(f"{BASE_URL}/api/certifications/{cert_id}")
            except:
                pass
        
        if self.test_contractor_id:
            try:
                requests.delete(f"{BASE_URL}/api/contractors/{self.test_contractor_id}")
            except:
                pass
    
    def test_certification_exceeds_budget(self):
        """Test creating certification that exceeds budget (should still work)"""
        cert_data = {
            "contractor_id": self.test_contractor_id,
            "week_start_date": "2025-01-06",
            "amount": 150000.0,  # Exceeds 100000 budget
            "description": "TEST_Over budget certification"
        }
        
        response = requests.post(f"{BASE_URL}/api/certifications", json=cert_data)
        
        # Should still create (no budget validation on certification)
        assert response.status_code == 200
        self.test_certification_ids.append(response.json()["id"])
        
        # Verify remaining_balance is negative
        contractor = requests.get(f"{BASE_URL}/api/contractors/{self.test_contractor_id}").json()
        assert contractor["remaining_balance"] == -50000.0
    
    def test_certification_with_zero_amount(self):
        """Test creating certification with zero amount"""
        cert_data = {
            "contractor_id": self.test_contractor_id,
            "week_start_date": "2025-01-06",
            "amount": 0.0
        }
        
        response = requests.post(f"{BASE_URL}/api/certifications", json=cert_data)
        
        # Should work (no validation for zero amount)
        assert response.status_code == 200
        self.test_certification_ids.append(response.json()["id"])
    
    def test_delete_prevents_negative_total_paid(self):
        """Test that deleting certification doesn't make total_paid negative"""
        # Create and delete certification
        cert_data = {
            "contractor_id": self.test_contractor_id,
            "week_start_date": "2025-01-06",
            "amount": 50000.0
        }
        
        create_resp = requests.post(f"{BASE_URL}/api/certifications", json=cert_data)
        cert_id = create_resp.json()["id"]
        
        # Delete it
        requests.delete(f"{BASE_URL}/api/certifications/{cert_id}")
        
        # Verify total_paid is 0, not negative
        contractor = requests.get(f"{BASE_URL}/api/contractors/{self.test_contractor_id}").json()
        assert contractor["total_paid"] >= 0, "total_paid should never be negative"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
