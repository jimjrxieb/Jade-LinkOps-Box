#!/usr/bin/env python3
"""
ZRS Property Management Workflow Test
=====================================

End-to-end testing of the complete property management AI system.
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List


class PropertyManagementTester:
    """
    Test suite for ZRS Property Management AI workflows.
    """
    
    def __init__(self, base_url: str = "http://localhost:9000"):
        """Initialize tester with API base URL."""
        self.base_url = base_url
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
    
    def log_test(self, test_name: str, success: bool, response: Dict = None, error: str = None):
        """Log test result."""
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "response": response,
            "error": error
        }
        self.test_results.append(result)
        
        if success:
            self.passed_tests += 1
            print(f"✅ {test_name}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: {error}")
    
    def test_api_health(self):
        """Test API health endpoint."""
        try:
            response = requests.get(f"{self.base_url}/property/health")
            if response.status_code == 200:
                self.log_test("API Health Check", True, response.json())
                return True
            else:
                self.log_test("API Health Check", False, error=f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Health Check", False, error=str(e))
            return False
    
    def test_late_notice_workflow(self):
        """Test sending late rent notice workflow."""
        try:
            payload = {
                "tenant_name": "Peter Parker",
                "unit_number": "205",
                "amount_due": 1200.00,
                "days_late": 7,
                "template": "standard_late_notice",
                "include_late_fee": True
            }
            
            response = requests.post(f"{self.base_url}/property/send-late-notice", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                expected_fields = ["email_sent", "email_id", "timestamp", "command_executed"]
                
                if all(field in result for field in expected_fields):
                    self.log_test("Late Notice Workflow", True, result)
                    return True
                else:
                    self.log_test("Late Notice Workflow", False, error="Missing required fields")
                    return False
            else:
                self.log_test("Late Notice Workflow", False, error=f"Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Late Notice Workflow", False, error=str(e))
            return False
    
    def test_maintenance_notification(self):
        """Test maintenance notification workflow."""
        try:
            payload = {
                "unit_number": "303",
                "issue_type": "plumbing",
                "description": "Water leak in kitchen ceiling",
                "urgency": "emergency",
                "tenant_contact": "555-0123",
                "estimated_cost": 350.00
            }
            
            response = requests.post(f"{self.base_url}/property/notify-maintenance", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                expected_fields = ["work_order_id", "assigned_tech", "estimated_arrival", "command_executed"]
                
                if all(field in result for field in expected_fields):
                    self.log_test("Maintenance Notification", True, result)
                    return True
                else:
                    self.log_test("Maintenance Notification", False, error="Missing required fields")
                    return False
            else:
                self.log_test("Maintenance Notification", False, error=f"Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Maintenance Notification", False, error=str(e))
            return False
    
    def test_vendor_suggestion(self):
        """Test vendor suggestion workflow."""
        try:
            payload = {
                "work_type": "hvac",
                "building": "Building A",
                "urgency": "urgent",
                "budget_max": 2000.00,
                "availability_required": "within_24_hours"
            }
            
            response = requests.post(f"{self.base_url}/property/vendor-suggest", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                if "recommended_vendors" in result and len(result["recommended_vendors"]) > 0:
                    vendor = result["recommended_vendors"][0]
                    required_vendor_fields = ["vendor_name", "contact_info", "estimated_cost", "rating"]
                    
                    if all(field in vendor for field in required_vendor_fields):
                        self.log_test("Vendor Suggestion", True, result)
                        return True
                    else:
                        self.log_test("Vendor Suggestion", False, error="Missing vendor fields")
                        return False
                else:
                    self.log_test("Vendor Suggestion", False, error="No vendors returned")
                    return False
            else:
                self.log_test("Vendor Suggestion", False, error=f"Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Vendor Suggestion", False, error=str(e))
            return False
    
    def test_turnover_scheduling(self):
        """Test unit turnover scheduling workflow."""
        try:
            payload = {
                "unit_number": "506",
                "move_out_date": "2025-02-15",
                "new_lease_start": "2025-02-20",
                "cleaning_level": "deep_clean",
                "repairs_needed": ["carpet_cleaning", "paint_touch_up"],
                "inspection_required": True
            }
            
            response = requests.post(f"{self.base_url}/property/schedule-turnover", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                expected_fields = ["turnover_id", "scheduled_tasks", "estimated_completion", "command_executed"]
                
                if all(field in result for field in expected_fields):
                    if len(result["scheduled_tasks"]) > 0:
                        self.log_test("Turnover Scheduling", True, result)
                        return True
                    else:
                        self.log_test("Turnover Scheduling", False, error="No tasks scheduled")
                        return False
                else:
                    self.log_test("Turnover Scheduling", False, error="Missing required fields")
                    return False
            else:
                self.log_test("Turnover Scheduling", False, error=f"Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Turnover Scheduling", False, error=str(e))
            return False
    
    def test_broadcast_notice(self):
        """Test broadcast notice workflow."""
        try:
            payload = {
                "message": "Pool maintenance scheduled for February 10-12. Pool will be closed during this time.",
                "subject": "Pool Closure Notice - February 10-12",
                "recipient_group": "all_tenants",
                "delivery_method": ["email", "posted_notice"],
                "send_time": "immediate",
                "priority": "normal"
            }
            
            response = requests.post(f"{self.base_url}/property/broadcast-notice", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                expected_fields = ["notification_id", "total_recipients", "delivery_status", "command_executed"]
                
                if all(field in result for field in expected_fields):
                    if result["total_recipients"] > 0:
                        self.log_test("Broadcast Notice", True, result)
                        return True
                    else:
                        self.log_test("Broadcast Notice", False, error="No recipients")
                        return False
                else:
                    self.log_test("Broadcast Notice", False, error="Missing required fields")
                    return False
            else:
                self.log_test("Broadcast Notice", False, error=f"Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Broadcast Notice", False, error=str(e))
            return False
    
    def test_delinquency_query(self):
        """Test delinquency query workflow."""
        try:
            payload = {
                "days_late_min": 15,
                "days_late_max": 60,
                "amount_min": 1000.00,
                "sort_by": "amount_owed",
                "sort_order": "desc"
            }
            
            response = requests.post(f"{self.base_url}/property/query-delinquency", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                expected_fields = ["total_delinquent_tenants", "total_amount_owed", "tenants", "summary_stats", "command_executed"]
                
                if all(field in result for field in expected_fields):
                    self.log_test("Delinquency Query", True, result)
                    return True
                else:
                    self.log_test("Delinquency Query", False, error="Missing required fields")
                    return False
            else:
                self.log_test("Delinquency Query", False, error=f"Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Delinquency Query", False, error=str(e))
            return False
    
    def test_jade_integration(self):
        """Test Jade AI assistant integration with property management."""
        try:
            # Test Jade's ability to route property management queries
            payload = {
                "query": "Send late rent notice to Tony Stark in unit 401",
                "context": [],
                "user_role": "property_manager"
            }
            
            response = requests.post(f"{self.base_url}/jade", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if Jade response contains property management command
                if "answer" in result:
                    answer = result["answer"].lower()
                    if any(keyword in answer for keyword in ["late_notice", "send_email", "tenant"]):
                        self.log_test("Jade Integration", True, result)
                        return True
                    else:
                        self.log_test("Jade Integration", False, error="No property management command in response")
                        return False
                else:
                    self.log_test("Jade Integration", False, error="No answer field in response")
                    return False
            else:
                self.log_test("Jade Integration", False, error=f"Status {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Jade Integration", False, error=str(e))
            return False
    
    def run_all_tests(self):
        """Run complete test suite."""
        print("🏠 Starting ZRS Property Management AI Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            self.test_api_health,
            self.test_late_notice_workflow,
            self.test_maintenance_notification,
            self.test_vendor_suggestion,
            self.test_turnover_scheduling,
            self.test_broadcast_notice,
            self.test_delinquency_query,
            self.test_jade_integration
        ]
        
        for test in tests:
            test()
            time.sleep(0.5)  # Brief pause between tests
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏠 ZRS Property Management AI Test Results")
        print("=" * 60)
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📊 Success Rate: {(self.passed_tests / (self.passed_tests + self.failed_tests) * 100):.1f}%")
        
        # Save detailed results
        with open("property_management_test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "passed": self.passed_tests,
                    "failed": self.failed_tests,
                    "total": self.passed_tests + self.failed_tests,
                    "success_rate": self.passed_tests / (self.passed_tests + self.failed_tests) * 100,
                    "duration": duration,
                    "timestamp": datetime.now().isoformat()
                },
                "detailed_results": self.test_results
            }, f, indent=2)
        
        print("\n📁 Detailed results saved to: property_management_test_results.json")
        
        if self.failed_tests == 0:
            print("\n🎉 All tests passed! ZRS Property Management AI is ready for deployment.")
        else:
            print(f"\n⚠️  {self.failed_tests} test(s) failed. Review results for issues.")
        
        return self.failed_tests == 0


def main():
    """Main test runner."""
    tester = PropertyManagementTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Ready for production deployment!")
        exit(0)
    else:
        print("\n🔧 Issues found - review and fix before deployment.")
        exit(1)


if __name__ == "__main__":
    main()