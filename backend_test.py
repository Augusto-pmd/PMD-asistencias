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
        """Test Attendance management with late hours discount feature"""
        print("\n" + "="*50)
        print("TESTING ATTENDANCE MANAGEMENT WITH LATE HOURS")
        print("="*50)

        if not self.employee_ids:
            print("❌ No employees available for attendance testing")
            return False

        employee_id = self.employee_ids[0]
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        # Test Create Attendance - Present
        attendance_data = {
            "employee_id": employee_id,
            "date": today,
            "status": "present",
            "week_start_date": self.current_week_start
        }
        success, response = self.run_test("Mark Attendance Present", "POST", "attendance", 200, attendance_data)

        # Test Create Attendance - Late with hours
        late_attendance_data = {
            "employee_id": employee_id,
            "date": yesterday,
            "status": "late",
            "late_hours": 2.0,
            "week_start_date": self.current_week_start
        }
        success, response = self.run_test("Mark Attendance Late with 2 hours", "POST", "attendance", 200, late_attendance_data)
        if success:
            if response.get('late_hours') == 2.0:
                print("   ✅ Late hours recorded correctly")
            else:
                print(f"   ❌ Late hours incorrect: {response.get('late_hours')}")

        # Test Update Attendance - Change late hours
        late_attendance_data["late_hours"] = 1.5
        success, response = self.run_test("Update Late Hours to 1.5", "POST", "attendance", 200, late_attendance_data)
        if success:
            if response.get('late_hours') == 1.5:
                print("   ✅ Late hours updated correctly")
            else:
                print(f"   ❌ Late hours update failed: {response.get('late_hours')}")

        # Test Edge Case - Late with 0 hours
        zero_late_data = {
            "employee_id": employee_id,
            "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "status": "late",
            "late_hours": 0.0,
            "week_start_date": self.current_week_start
        }
        success, response = self.run_test("Mark Late with 0 hours", "POST", "attendance", 200, zero_late_data)
        if success:
            if response.get('late_hours') == 0.0:
                print("   ✅ Zero late hours handled correctly")
            else:
                print(f"   ❌ Zero late hours handling failed: {response.get('late_hours')}")

        # Test Edge Case - Late with decimal hours
        decimal_late_data = {
            "employee_id": employee_id,
            "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "status": "late",
            "late_hours": 0.5,
            "week_start_date": self.current_week_start
        }
        success, response = self.run_test("Mark Late with 0.5 hours", "POST", "attendance", 200, decimal_late_data)
        if success:
            if response.get('late_hours') == 0.5:
                print("   ✅ Decimal late hours handled correctly")
            else:
                print(f"   ❌ Decimal late hours handling failed: {response.get('late_hours')}")

        # Test Get All Attendance
        success, response = self.run_test("Get All Attendance", "GET", "attendance", 200)
        if success:
            print(f"   Found {len(response)} attendance records")
            # Verify late_hours field is present
            late_records = [r for r in response if r.get('status') == 'late']
            for record in late_records:
                if 'late_hours' in record:
                    print(f"   ✅ Late record has late_hours: {record['late_hours']}")
                else:
                    print("   ❌ Late record missing late_hours field")

        # Test Get Week Attendance
        success, response = self.run_test("Get Week Attendance", "GET", f"attendance/week/{self.current_week_start}", 200)
        if success:
            print(f"   Found {len(response)} attendance records for current week")
            # Verify late_hours field is present in week data
            late_records = [r for r in response if r.get('status') == 'late']
            total_late_hours = sum(r.get('late_hours', 0) for r in late_records)
            print(f"   Total late hours for week: {total_late_hours}")

        return True

    def test_late_hours_discount_calculation(self):
        """Test late hours discount calculation in payment system"""
        print("\n" + "="*50)
        print("TESTING LATE HOURS DISCOUNT CALCULATION")
        print("="*50)

        if not self.employee_ids:
            print("❌ No employees available for late hours testing")
            return False

        # Create a test employee with known daily salary for calculation
        employee_data = {
            "name": "Test Employee Late Hours",
            "daily_salary": 8000.0  # 8000 / 8 = 1000 per hour
        }
        success, response = self.run_test("Create Employee for Late Hours Test", "POST", "employees", 200, employee_data)
        if not success or 'id' not in response:
            print("❌ Failed to create test employee")
            return False
        
        test_employee_id = response['id']
        self.employee_ids.append(test_employee_id)
        print(f"   Created test employee ID: {test_employee_id}")
        print(f"   Daily salary: {employee_data['daily_salary']}")
        print(f"   Hourly rate: {employee_data['daily_salary'] / 8}")

        # Create attendance records for the week
        week_dates = []
        for i in range(5):  # Monday to Friday
            date = datetime.strptime(self.current_week_start, "%Y-%m-%d") + timedelta(days=i)
            week_dates.append(date.strftime("%Y-%m-%d"))

        # Monday: Present
        attendance_data = {
            "employee_id": test_employee_id,
            "date": week_dates[0],
            "status": "present",
            "week_start_date": self.current_week_start
        }
        success, response = self.run_test("Monday - Present", "POST", "attendance", 200, attendance_data)

        # Tuesday: Late 2 hours
        attendance_data = {
            "employee_id": test_employee_id,
            "date": week_dates[1],
            "status": "late",
            "late_hours": 2.0,
            "week_start_date": self.current_week_start
        }
        success, response = self.run_test("Tuesday - Late 2 hours", "POST", "attendance", 200, attendance_data)

        # Wednesday: Present
        attendance_data = {
            "employee_id": test_employee_id,
            "date": week_dates[2],
            "status": "present",
            "week_start_date": self.current_week_start
        }
        success, response = self.run_test("Wednesday - Present", "POST", "attendance", 200, attendance_data)

        # Thursday: Late 1 hour
        attendance_data = {
            "employee_id": test_employee_id,
            "date": week_dates[3],
            "status": "late",
            "late_hours": 1.0,
            "week_start_date": self.current_week_start
        }
        success, response = self.run_test("Thursday - Late 1 hour", "POST", "attendance", 200, attendance_data)

        # Friday: Present
        attendance_data = {
            "employee_id": test_employee_id,
            "date": week_dates[4],
            "status": "present",
            "week_start_date": self.current_week_start
        }
        success, response = self.run_test("Friday - Present", "POST", "attendance", 200, attendance_data)

        # Add an advance for complete calculation test
        advance_data = {
            "employee_id": test_employee_id,
            "amount": 1000.0,
            "date": week_dates[0],
            "description": "Test advance for late hours calculation",
            "week_start_date": self.current_week_start
        }
        success, response = self.run_test("Add Advance for Test Employee", "POST", "advances", 200, advance_data)
        if success and 'id' in response:
            self.advance_ids.append(response['id'])

        # Test payment calculation with late hours
        calculation_data = {
            "week_start_date": self.current_week_start
        }
        success, response = self.run_test("Calculate Payments with Late Hours", "POST", "payments/calculate", 200, calculation_data)
        if success:
            print(f"   Payment calculation completed: {response}")

        # Verify the calculation by checking payment history
        success, response = self.run_test("Get Payment History for Verification", "GET", "payments/history", 200)
        if success:
            # Find our test employee's payment record
            test_payment = None
            for payment in response:
                if payment.get('employee_id') == test_employee_id:
                    test_payment = payment
                    break
            
            if test_payment:
                print(f"   Found payment record for test employee")
                print(f"   Days worked: {test_payment.get('days_worked')}")
                print(f"   Total salary (after late discount): {test_payment.get('total_salary')}")
                print(f"   Total advances: {test_payment.get('total_advances')}")
                print(f"   Net payment: {test_payment.get('net_payment')}")
                
                # Expected calculation:
                # Days worked: 5 (all days marked as present or late)
                # Gross salary: 5 * 8000 = 40000
                # Late hours: 2 + 1 = 3 hours
                # Hourly rate: 8000 / 8 = 1000
                # Late discount: 3 * 1000 = 3000
                # Total salary after discount: 40000 - 3000 = 37000
                # Net payment: 37000 - 1000 (advance) = 36000
                
                expected_days = 5
                expected_gross = 5 * 8000
                expected_late_discount = 3 * 1000
                expected_total_salary = expected_gross - expected_late_discount
                expected_net = expected_total_salary - 1000
                
                print(f"\n   CALCULATION VERIFICATION:")
                print(f"   Expected days worked: {expected_days}")
                print(f"   Expected gross salary: {expected_gross}")
                print(f"   Expected late discount: {expected_late_discount}")
                print(f"   Expected total salary: {expected_total_salary}")
                print(f"   Expected net payment: {expected_net}")
                
                if test_payment.get('days_worked') == expected_days:
                    print("   ✅ Days worked calculated correctly")
                else:
                    print(f"   ❌ Days worked incorrect: {test_payment.get('days_worked')} vs {expected_days}")
                
                if test_payment.get('total_salary') == expected_total_salary:
                    print("   ✅ Total salary (with late discount) calculated correctly")
                else:
                    print(f"   ❌ Total salary incorrect: {test_payment.get('total_salary')} vs {expected_total_salary}")
                
                if test_payment.get('net_payment') == expected_net:
                    print("   ✅ Net payment calculated correctly")
                else:
                    print(f"   ❌ Net payment incorrect: {test_payment.get('net_payment')} vs {expected_net}")
            else:
                print("   ❌ Payment record not found for test employee")

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

        return True

    def test_backward_compatibility(self):
        """Test backward compatibility with old contractors without budget fields"""
        print("\n" + "="*50)
        print("TESTING BACKWARD COMPATIBILITY")
        print("="*50)
        
        # Test that API now requires budget fields (expected behavior)
        contractor_data = {
            "name": "Old Contractor Test",
            "weekly_payment": 10000.0
        }
        success, response = self.run_test("Create Old-Style Contractor (should fail)", "POST", "contractors", 422, contractor_data)
        if not success:
            print("   ✅ API correctly requires project_name and budget fields")
        else:
            print("   ❌ API should require budget fields but didn't")
        
        # Test that existing contractors without budget fields are handled properly
        success, response = self.run_test("Get All Contractors (check existing data)", "GET", "contractors", 200)
        if success:
            print(f"   Found {len(response)} contractors")
            # Check if any contractors have missing budget fields and how they're handled
            for contractor in response:
                name = contractor.get('name', 'Unknown')
                project_name = contractor.get('project_name', 'N/A')
                budget = contractor.get('budget', 0)
                total_paid = contractor.get('total_paid', 0)
                remaining_balance = contractor.get('remaining_balance', 0)
                
                if project_name == 'Sin asignar' or project_name is None:
                    print(f"   ✅ Contractor '{name}' has default project name handling")
                
                # All contractors should have budget fields now
                if 'budget' in contractor and 'total_paid' in contractor and 'remaining_balance' in contractor:
                    print(f"   ✅ Contractor '{name}' has all budget fields")
                else:
                    print(f"   ❌ Contractor '{name}' missing budget fields")
        
        return True

    def test_dashboard_stats(self):
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
            self.test_backward_compatibility()
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