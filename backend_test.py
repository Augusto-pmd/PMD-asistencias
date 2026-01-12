import requests
import sys
from datetime import datetime, timedelta
import json

class PayrollProAPITester:
    def __init__(self, base_url="https://payroll-manager-60.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.employee_ids = []
        self.contractor_ids = []
        self.advance_ids = []
        self.current_week_start = self.get_current_week_start()

    def get_current_week_start(self):
        """Get current week start (Monday)"""
        today = datetime.now()
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        return monday.strftime("%Y-%m-%d")

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {method} {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
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

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test("Root API", "GET", "", 200)
        return success

    def test_employee_crud(self):
        """Test Employee CRUD operations"""
        print("\n" + "="*50)
        print("TESTING EMPLOYEE MANAGEMENT")
        print("="*50)
        
        # Test Create Employee
        employee_data = {
            "name": "Juan Pérez Test",
            "daily_salary": 5000.0
        }
        success, response = self.run_test("Create Employee", "POST", "employees", 200, employee_data)
        if success and 'id' in response:
            employee_id = response['id']
            self.employee_ids.append(employee_id)
            print(f"   Created employee ID: {employee_id}")
        else:
            return False

        # Test Get All Employees
        success, response = self.run_test("Get All Employees", "GET", "employees", 200)
        if success:
            print(f"   Found {len(response)} employees")

        # Test Get Single Employee
        success, response = self.run_test("Get Single Employee", "GET", f"employees/{employee_id}", 200)
        if success:
            print(f"   Employee name: {response.get('name', 'N/A')}")

        # Test Update Employee
        update_data = {
            "name": "Juan Pérez Updated",
            "daily_salary": 5500.0
        }
        success, response = self.run_test("Update Employee", "PUT", f"employees/{employee_id}", 200, update_data)

        # Test Get Updated Employee
        success, response = self.run_test("Verify Employee Update", "GET", f"employees/{employee_id}", 200)
        if success and response.get('name') == "Juan Pérez Updated":
            print("   ✅ Employee update verified")
        else:
            print("   ❌ Employee update verification failed")

        return True

    def test_contractor_crud(self):
        """Test Contractor CRUD operations with budget tracking"""
        print("\n" + "="*50)
        print("TESTING CONTRACTOR MANAGEMENT WITH BUDGET TRACKING")
        print("="*50)
        
        # Test Create Contractor with Budget
        contractor_data = {
            "name": "María González Test",
            "weekly_payment": 15000.0,
            "project_name": "Casa Barrio Centro",
            "budget": 500000.0
        }
        success, response = self.run_test("Create Contractor with Budget", "POST", "contractors", 200, contractor_data)
        if success and 'id' in response:
            contractor_id = response['id']
            self.contractor_ids.append(contractor_id)
            print(f"   Created contractor ID: {contractor_id}")
            
            # Verify budget fields
            if response.get('budget') == 500000.0:
                print("   ✅ Budget field set correctly")
            else:
                print(f"   ❌ Budget field incorrect: {response.get('budget')}")
                
            if response.get('total_paid') == 0.0:
                print("   ✅ Initial total_paid is 0")
            else:
                print(f"   ❌ Initial total_paid incorrect: {response.get('total_paid')}")
                
            if response.get('remaining_balance') == 500000.0:
                print("   ✅ Initial remaining_balance equals budget")
            else:
                print(f"   ❌ Initial remaining_balance incorrect: {response.get('remaining_balance')}")
                
            if response.get('project_name') == "Casa Barrio Centro":
                print("   ✅ Project name set correctly")
            else:
                print(f"   ❌ Project name incorrect: {response.get('project_name')}")
        else:
            return False

        # Test Create Second Contractor with Different Budget
        contractor_data2 = {
            "name": "Carlos López Test",
            "weekly_payment": 20000.0,
            "project_name": "Casa Norte",
            "budget": 300000.0
        }
        success, response = self.run_test("Create Second Contractor with Budget", "POST", "contractors", 200, contractor_data2)
        if success and 'id' in response:
            contractor_id2 = response['id']
            self.contractor_ids.append(contractor_id2)
            print(f"   Created second contractor ID: {contractor_id2}")

        # Test Get All Contractors
        success, response = self.run_test("Get All Contractors", "GET", "contractors", 200)
        if success:
            print(f"   Found {len(response)} contractors")
            # Verify budget fields are included
            for contractor in response:
                if 'budget' in contractor and 'total_paid' in contractor and 'remaining_balance' in contractor:
                    print(f"   ✅ Budget fields present for {contractor.get('name', 'Unknown')}")
                else:
                    print(f"   ❌ Budget fields missing for {contractor.get('name', 'Unknown')}")

        # Test Get Single Contractor
        success, response = self.run_test("Get Single Contractor", "GET", f"contractors/{contractor_id}", 200)
        if success:
            print(f"   Contractor name: {response.get('name', 'N/A')}")
            print(f"   Weekly payment: {response.get('weekly_payment', 'N/A')}")
            print(f"   Project: {response.get('project_name', 'N/A')}")
            print(f"   Budget: {response.get('budget', 'N/A')}")
            print(f"   Total paid: {response.get('total_paid', 'N/A')}")
            print(f"   Remaining balance: {response.get('remaining_balance', 'N/A')}")

        # Test Update Contractor Budget
        update_data = {
            "name": "María González Updated",
            "weekly_payment": 16000.0,
            "project_name": "Casa Barrio Centro Updated",
            "budget": 600000.0
        }
        success, response = self.run_test("Update Contractor Budget", "PUT", f"contractors/{contractor_id}", 200, update_data)

        # Test Get Updated Contractor
        success, response = self.run_test("Verify Contractor Budget Update", "GET", f"contractors/{contractor_id}", 200)
        if success:
            if response.get('name') == "María González Updated":
                print("   ✅ Contractor name update verified")
            else:
                print("   ❌ Contractor name update verification failed")
                
            if response.get('budget') == 600000.0:
                print("   ✅ Budget update verified")
            else:
                print(f"   ❌ Budget update failed: {response.get('budget')}")
                
            # Verify remaining_balance recalculated
            expected_balance = 600000.0 - response.get('total_paid', 0)
            if response.get('remaining_balance') == expected_balance:
                print("   ✅ Remaining balance recalculated correctly")
            else:
                print(f"   ❌ Remaining balance calculation error: {response.get('remaining_balance')} vs {expected_balance}")

        return True

    def test_attendance_management(self):
        """Test Attendance management"""
        print("\n" + "="*50)
        print("TESTING ATTENDANCE MANAGEMENT")
        print("="*50)

        if not self.employee_ids:
            print("❌ No employees available for attendance testing")
            return False

        employee_id = self.employee_ids[0]
        today = datetime.now().strftime("%Y-%m-%d")

        # Test Create Attendance - Present
        attendance_data = {
            "employee_id": employee_id,
            "date": today,
            "status": "present",
            "week_start_date": self.current_week_start
        }
        success, response = self.run_test("Mark Attendance Present", "POST", "attendance", 200, attendance_data)

        # Test Update Attendance - Late
        attendance_data["status"] = "late"
        success, response = self.run_test("Update Attendance to Late", "POST", "attendance", 200, attendance_data)

        # Test Get All Attendance
        success, response = self.run_test("Get All Attendance", "GET", "attendance", 200)
        if success:
            print(f"   Found {len(response)} attendance records")

        # Test Get Week Attendance
        success, response = self.run_test("Get Week Attendance", "GET", f"attendance/week/{self.current_week_start}", 200)
        if success:
            print(f"   Found {len(response)} attendance records for current week")

        return True

    def test_advance_management(self):
        """Test Advance management"""
        print("\n" + "="*50)
        print("TESTING ADVANCE MANAGEMENT")
        print("="*50)

        if not self.employee_ids:
            print("❌ No employees available for advance testing")
            return False

        employee_id = self.employee_ids[0]
        today = datetime.now().strftime("%Y-%m-%d")

        # Test Create Advance
        advance_data = {
            "employee_id": employee_id,
            "amount": 1000.0,
            "date": today,
            "description": "Test advance payment",
            "week_start_date": self.current_week_start
        }
        success, response = self.run_test("Create Advance", "POST", "advances", 200, advance_data)
        if success and 'id' in response:
            advance_id = response['id']
            self.advance_ids.append(advance_id)
            print(f"   Created advance ID: {advance_id}")

        # Test Get All Advances
        success, response = self.run_test("Get All Advances", "GET", "advances", 200)
        if success:
            print(f"   Found {len(response)} advances")

        # Test Get Employee Advances
        success, response = self.run_test("Get Employee Advances", "GET", f"advances/employee/{employee_id}", 200)
        if success:
            print(f"   Found {len(response)} advances for employee")

        return True

    def test_payment_calculation(self):
        """Test Payment calculation and history with budget tracking"""
        print("\n" + "="*50)
        print("TESTING PAYMENT CALCULATION WITH BUDGET TRACKING")
        print("="*50)

        # Test Calculate Payments
        calculation_data = {
            "week_start_date": self.current_week_start
        }
        success, response = self.run_test("Calculate Payments", "POST", "payments/calculate", 200, calculation_data)
        if success:
            print(f"   Payment calculation result: {response}")
            contractors_updated = response.get('contractors_updated', 0)
            print(f"   Contractors updated: {contractors_updated}")

        # Verify contractor total_paid was updated
        if self.contractor_ids:
            contractor_id = self.contractor_ids[0]
            success, response = self.run_test("Check Contractor After Payment", "GET", f"contractors/{contractor_id}", 200)
            if success:
                total_paid = response.get('total_paid', 0)
                weekly_payment = response.get('weekly_payment', 0)
                budget = response.get('budget', 0)
                remaining_balance = response.get('remaining_balance', 0)
                
                print(f"   Total paid after 1st payment: {total_paid}")
                print(f"   Weekly payment: {weekly_payment}")
                print(f"   Budget: {budget}")
                print(f"   Remaining balance: {remaining_balance}")
                
                if total_paid == weekly_payment:
                    print("   ✅ Total paid equals weekly payment after first calculation")
                else:
                    print(f"   ❌ Total paid mismatch: {total_paid} vs {weekly_payment}")
                    
                expected_balance = budget - total_paid
                if remaining_balance == expected_balance:
                    print("   ✅ Remaining balance calculated correctly")
                else:
                    print(f"   ❌ Remaining balance error: {remaining_balance} vs {expected_balance}")

        # Test second payment calculation
        success, response = self.run_test("Calculate Payments Again", "POST", "payments/calculate", 200, calculation_data)
        if success and self.contractor_ids:
            contractor_id = self.contractor_ids[0]
            success, response = self.run_test("Check Contractor After 2nd Payment", "GET", f"contractors/{contractor_id}", 200)
            if success:
                total_paid = response.get('total_paid', 0)
                weekly_payment = response.get('weekly_payment', 0)
                budget = response.get('budget', 0)
                remaining_balance = response.get('remaining_balance', 0)
                
                print(f"   Total paid after 2nd payment: {total_paid}")
                print(f"   Remaining balance: {remaining_balance}")
                
                if total_paid == weekly_payment * 2:
                    print("   ✅ Total paid accumulated correctly (2x weekly payment)")
                else:
                    print(f"   ❌ Total paid accumulation error: {total_paid} vs {weekly_payment * 2}")
                    
                expected_balance = budget - total_paid
                if remaining_balance == expected_balance:
                    print("   ✅ Remaining balance updated correctly after 2nd payment")
                else:
                    print(f"   ❌ Remaining balance error after 2nd payment: {remaining_balance} vs {expected_balance}")

        # Test Get Payment History
        success, response = self.run_test("Get Payment History", "GET", "payments/history", 200)
        if success:
            print(f"   Found {len(response)} payment history records")

    def test_backward_compatibility(self):
        """Test backward compatibility with old contractors without budget fields"""
        print("\n" + "="*50)
        print("TESTING BACKWARD COMPATIBILITY")
        print("="*50)
        
        # Create contractor without budget fields (simulating old data)
        contractor_data = {
            "name": "Old Contractor Test",
            "weekly_payment": 10000.0
        }
        success, response = self.run_test("Create Old-Style Contractor", "POST", "contractors", 200, contractor_data)
        if success and 'id' in response:
            contractor_id = response['id']
            self.contractor_ids.append(contractor_id)
            print(f"   Created old-style contractor ID: {contractor_id}")
            
            # Check if default values are applied
            if response.get('project_name') == 'Sin asignar' or response.get('project_name') is None:
                print("   ✅ Default project_name handled correctly")
            else:
                print(f"   ❌ Project name should be 'Sin asignar', got: {response.get('project_name')}")
                
            if response.get('budget', 0) == 0:
                print("   ✅ Default budget is 0")
            else:
                print(f"   ❌ Default budget should be 0, got: {response.get('budget')}")
                
            if response.get('total_paid', 0) == 0:
                print("   ✅ Default total_paid is 0")
            else:
                print(f"   ❌ Default total_paid should be 0, got: {response.get('total_paid')}")
                
            if response.get('remaining_balance', 0) == 0:
                print("   ✅ Default remaining_balance is 0")
            else:
                print(f"   ❌ Default remaining_balance should be 0, got: {response.get('remaining_balance')}")
        
        # Test that old contractors appear in list without errors
        success, response = self.run_test("Get All Contractors (with old data)", "GET", "contractors", 200)
        if success:
            old_contractor = next((c for c in response if c.get('name') == 'Old Contractor Test'), None)
            if old_contractor:
                print("   ✅ Old contractor appears in list")
                if old_contractor.get('project_name') == 'Sin asignar':
                    print("   ✅ Old contractor shows 'Sin asignar' for project")
                else:
                    print(f"   ❌ Old contractor project name: {old_contractor.get('project_name')}")
            else:
                print("   ❌ Old contractor not found in list")
        
        return True
        """Test Dashboard statistics"""
        print("\n" + "="*50)
        print("TESTING DASHBOARD STATISTICS")
        print("="*50)

        success, response = self.run_test("Get Dashboard Stats", "GET", "dashboard/stats", 200)
        if success:
            print(f"   Total employees: {response.get('total_employees', 'N/A')}")
            print(f"   Active employees: {response.get('active_employees', 'N/A')}")
            print(f"   Total contractors: {response.get('total_contractors', 'N/A')}")
            print(f"   Active contractors: {response.get('active_contractors', 'N/A')}")
            print(f"   Total payment this week: {response.get('total_payment_this_week', 'N/A')}")
            print(f"   Contractors payment this week: {response.get('contractors_payment_this_week', 'N/A')}")
            print(f"   Total advances this week: {response.get('total_advances_this_week', 'N/A')}")
            print(f"   Net payment this week: {response.get('net_payment_this_week', 'N/A')}")
            print(f"   Total to pay Friday: {response.get('total_to_pay_friday', 'N/A')}")
            
            # Verify contractor stats are included
            if 'total_contractors' in response and 'active_contractors' in response:
                print("   ✅ Contractor stats included in dashboard")
            else:
                print("   ❌ Contractor stats missing from dashboard")
                
            if 'contractors_payment_this_week' in response:
                print("   ✅ Contractor payment calculation included")
            else:
                print("   ❌ Contractor payment calculation missing")

        return True

    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n" + "="*50)
        print("CLEANING UP TEST DATA")
        print("="*50)

        # Delete test advances
        for advance_id in self.advance_ids:
            success, _ = self.run_test(f"Delete Advance {advance_id}", "DELETE", f"advances/{advance_id}", 200)

        # Delete test contractors
        for contractor_id in self.contractor_ids:
            success, _ = self.run_test(f"Delete Contractor {contractor_id}", "DELETE", f"contractors/{contractor_id}", 200)

        # Delete test employees
        for employee_id in self.employee_ids:
            success, _ = self.run_test(f"Delete Employee {employee_id}", "DELETE", f"employees/{employee_id}", 200)

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting PayrollPro API Tests")
        print(f"Base URL: {self.base_url}")
        print("="*60)

        try:
            # Test basic connectivity
            if not self.test_root_endpoint():
                print("❌ Root endpoint failed, stopping tests")
                return False

            # Test all modules
            self.test_employee_crud()
            self.test_contractor_crud()
            self.test_attendance_management()
            self.test_advance_management()
            self.test_payment_calculation()
            self.test_dashboard_stats()

            # Cleanup
            self.cleanup_test_data()

        except Exception as e:
            print(f"❌ Test suite failed with error: {str(e)}")
            return False

        # Print final results
        print("\n" + "="*60)
        print("📊 FINAL TEST RESULTS")
        print("="*60)
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")

        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed")
            return False

def main():
    tester = PayrollProAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())