import requests
import sys
from datetime import datetime, timedelta
import json

class DeleteOperationsTest:
    def __init__(self, base_url="https://site-salary.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.current_week_start = self.get_current_week_start()

    def get_current_week_start(self):
        """Get current week start (Monday)"""
        today = datetime.now()
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        return monday.strftime("%Y-%m-%d")

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"   Response: {response.text}")
                except:
                    pass
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_employee_delete_operation(self):
        """Test Employee Delete Operation - Create, Delete, Verify"""
        print("\n" + "="*60)
        print("TESTING EMPLOYEE DELETE OPERATION")
        print("="*60)
        
        # Step 1: Create a test employee
        employee_data = {
            "name": "Test Employee for Delete",
            "daily_salary": 3000.0
        }
        success, response = self.run_test("Create Test Employee", "POST", "employees", 200, employee_data)
        if not success or 'id' not in response:
            print("❌ Failed to create test employee")
            return False
        
        employee_id = response['id']
        print(f"   Created employee ID: {employee_id}")
        
        # Step 2: Verify employee exists in list
        success, response = self.run_test("Verify Employee Exists", "GET", "employees", 200)
        if not success:
            return False
        
        employee_found = any(emp['id'] == employee_id for emp in response)
        if not employee_found:
            print("❌ Employee not found in list after creation")
            return False
        print(f"   ✅ Employee found in list ({len(response)} total employees)")
        
        # Step 3: Delete the employee
        success, response = self.run_test("Delete Test Employee", "DELETE", f"employees/{employee_id}", 200)
        if not success:
            return False
        
        # Step 4: Verify employee is removed from list
        success, response = self.run_test("Verify Employee Deleted", "GET", "employees", 200)
        if not success:
            return False
        
        employee_still_exists = any(emp['id'] == employee_id for emp in response)
        if employee_still_exists:
            print("❌ Employee still exists in list after deletion")
            return False
        print(f"   ✅ Employee successfully removed from list ({len(response)} total employees)")
        
        # Step 5: Verify 404 when trying to get deleted employee
        success, response = self.run_test("Verify Employee 404", "GET", f"employees/{employee_id}", 404)
        if success:
            print("   ✅ Deleted employee returns 404 as expected")
        
        return True

    def test_advance_delete_operation(self):
        """Test Advance Delete Operation - Create, Delete, Verify"""
        print("\n" + "="*60)
        print("TESTING ADVANCE DELETE OPERATION")
        print("="*60)
        
        # Step 1: First create an employee for the advance
        employee_data = {
            "name": "Employee for Advance Test",
            "daily_salary": 4000.0
        }
        success, response = self.run_test("Create Employee for Advance", "POST", "employees", 200, employee_data)
        if not success or 'id' not in response:
            print("❌ Failed to create employee for advance test")
            return False
        
        employee_id = response['id']
        print(f"   Created employee ID: {employee_id}")
        
        # Step 2: Create a test advance
        advance_data = {
            "employee_id": employee_id,
            "amount": 1500.0,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "description": "Test advance for delete operation",
            "week_start_date": self.current_week_start
        }
        success, response = self.run_test("Create Test Advance", "POST", "advances", 200, advance_data)
        if not success or 'id' not in response:
            print("❌ Failed to create test advance")
            return False
        
        advance_id = response['id']
        print(f"   Created advance ID: {advance_id}")
        
        # Step 3: Verify advance exists in list
        success, response = self.run_test("Verify Advance Exists", "GET", "advances", 200)
        if not success:
            return False
        
        advance_found = any(adv['id'] == advance_id for adv in response)
        if not advance_found:
            print("❌ Advance not found in list after creation")
            return False
        print(f"   ✅ Advance found in list ({len(response)} total advances)")
        
        # Step 4: Delete the advance
        success, response = self.run_test("Delete Test Advance", "DELETE", f"advances/{advance_id}", 200)
        if not success:
            return False
        
        # Step 5: Verify advance is removed from list
        success, response = self.run_test("Verify Advance Deleted", "GET", "advances", 200)
        if not success:
            return False
        
        advance_still_exists = any(adv['id'] == advance_id for adv in response)
        if advance_still_exists:
            print("❌ Advance still exists in list after deletion")
            return False
        print(f"   ✅ Advance successfully removed from list ({len(response)} total advances)")
        
        # Step 6: Clean up - delete the test employee
        success, response = self.run_test("Cleanup Test Employee", "DELETE", f"employees/{employee_id}", 200)
        if success:
            print("   ✅ Test employee cleaned up")
        
        return True

    def run_delete_tests(self):
        """Run focused delete operation tests"""
        print("🚀 Starting Delete Operations Tests")
        print(f"Base URL: {self.base_url}")
        print("="*70)

        try:
            # Test employee delete operation
            employee_test_passed = self.test_employee_delete_operation()
            
            # Test advance delete operation  
            advance_test_passed = self.test_advance_delete_operation()

        except Exception as e:
            print(f"❌ Test suite failed with error: {str(e)}")
            return False

        # Print final results
        print("\n" + "="*70)
        print("📊 DELETE OPERATIONS TEST RESULTS")
        print("="*70)
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")

        if employee_test_passed and advance_test_passed:
            print("🎉 All delete operations working correctly!")
            print("✅ Employee delete: PASSED")
            print("✅ Advance delete: PASSED")
            return True
        else:
            print("⚠️  Some delete operations failed")
            print(f"❌ Employee delete: {'PASSED' if employee_test_passed else 'FAILED'}")
            print(f"❌ Advance delete: {'PASSED' if advance_test_passed else 'FAILED'}")
            return False

def main():
    tester = DeleteOperationsTest()
    success = tester.run_delete_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())