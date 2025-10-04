"""
Smart Stadium API Test Suite
Comprehensive testing of all API endpoints
"""

import asyncio
import requests
import json
import time
from typing import Dict, Any

class SmartStadiumAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
    
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = f"Status: {response.status_code}"
            if data:
                details += f", Uptime: {data.get('data', {}).get('uptime_seconds', 'N/A')}s"
            
            self.log_test("Health Check", success, details)
            return success
        except Exception as e:
            self.log_test("Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_system_status(self):
        """Test the system status endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/status")
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = f"Status: {response.status_code}"
            if data:
                details += f", Devices: {data.get('online_devices', 0)}/{data.get('total_devices', 0)} online"
                details += f", Team: {data.get('current_team', {}).get('full_name', 'Unknown')}"
            
            self.log_test("System Status", success, details)
            return success
        except Exception as e:
            self.log_test("System Status", False, f"Error: {str(e)}")
            return False
    
    def test_get_devices(self):
        """Test getting all devices"""
        try:
            response = self.session.get(f"{self.base_url}/api/devices/")
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = f"Status: {response.status_code}"
            if data and data.get('success'):
                device_count = len(data.get('data', {}).get('devices', []))
                details += f", Found {device_count} devices"
            
            self.log_test("Get Devices", success, details)
            return success
        except Exception as e:
            self.log_test("Get Devices", False, f"Error: {str(e)}")
            return False
    
    def test_get_teams(self):
        """Test getting all teams"""
        try:
            response = self.session.get(f"{self.base_url}/api/teams/")
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = f"Status: {response.status_code}"
            if data and data.get('success'):
                team_count = len(data.get('data', {}).get('teams', []))
                details += f", Found {team_count} teams"
            
            self.log_test("Get Teams", success, details)
            return success
        except Exception as e:
            self.log_test("Get Teams", False, f"Error: {str(e)}")
            return False
    
    def test_get_current_team(self):
        """Test getting current team"""
        try:
            response = self.session.get(f"{self.base_url}/api/teams/current")
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = f"Status: {response.status_code}"
            if data and data.get('success'):
                team_data = data.get('data', {})
                details += f", Current: {team_data.get('full_name', 'Unknown')}"
                details += f", Colors: {team_data.get('primary_color')} / {team_data.get('secondary_color')}"
            
            self.log_test("Get Current Team", success, details)
            return success
        except Exception as e:
            self.log_test("Get Current Team", False, f"Error: {str(e)}")
            return False
    
    def test_celebration_types(self):
        """Test getting celebration types"""
        try:
            response = self.session.get(f"{self.base_url}/api/celebrations/types")
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = f"Status: {response.status_code}"
            if data and data.get('success'):
                celebration_count = len(data.get('data', {}))
                details += f", Found {celebration_count} celebration types"
            
            self.log_test("Get Celebration Types", success, details)
            return success
        except Exception as e:
            self.log_test("Get Celebration Types", False, f"Error: {str(e)}")
            return False
    
    def test_team_search(self):
        """Test team search functionality"""
        try:
            response = self.session.get(f"{self.base_url}/api/teams/search/bills")
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = f"Status: {response.status_code}"
            if data and data.get('success'):
                result_count = data.get('data', {}).get('result_count', 0)
                details += f", Found {result_count} teams matching 'bills'"
            
            self.log_test("Team Search", success, details)
            return success
        except Exception as e:
            self.log_test("Team Search", False, f"Error: {str(e)}")
            return False
    
    def test_change_team(self):
        """Test changing teams"""
        try:
            # Test changing to Miami Dolphins
            payload = {"team_id": "NFL-MIAMI-DOLPHINS"}
            response = self.session.put(
                f"{self.base_url}/api/teams/current",
                json=payload
            )
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = f"Status: {response.status_code}"
            if data and data.get('success'):
                new_team = data.get('data', {}).get('new_team', {})
                details += f", Changed to: {new_team.get('full_name', 'Unknown')}"
            
            self.log_test("Change Team", success, details)
            
            # Change back to Bills
            if success:
                payload = {"team_id": "NFL-BUFFALO-BILLS"}
                self.session.put(f"{self.base_url}/api/teams/current", json=payload)
            
            return success
        except Exception as e:
            self.log_test("Change Team", False, f"Error: {str(e)}")
            return False
    
    def test_sack_celebration(self):
        """Test triggering a sack celebration (quick test)"""
        try:
            response = self.session.post(f"{self.base_url}/api/celebrations/sack")
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = f"Status: {response.status_code}"
            if data and data.get('success'):
                details += f", Message: {data.get('message', 'No message')}"
            
            self.log_test("Sack Celebration", success, details)
            return success
        except Exception as e:
            self.log_test("Sack Celebration", False, f"Error: {str(e)}")
            return False
    
    def test_device_refresh(self):
        """Test device status refresh"""
        try:
            response = self.session.post(f"{self.base_url}/api/devices/refresh")
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = f"Status: {response.status_code}"
            if data and data.get('success'):
                summary = data.get('data', {}).get('device_summary', {})
                details += f", Online: {summary.get('online', 0)}/{summary.get('total', 0)}"
            
            self.log_test("Device Refresh", success, details)
            return success
        except Exception as e:
            self.log_test("Device Refresh", False, f"Error: {str(e)}")
            return False
    
    def test_set_default_lighting(self):
        """Test setting default lighting"""
        try:
            response = self.session.post(f"{self.base_url}/api/devices/lighting/default")
            success = response.status_code == 200
            data = response.json() if success else None
            
            details = f"Status: {response.status_code}"
            if data and data.get('success'):
                details += f", Message: {data.get('message', 'No message')}"
            
            self.log_test("Set Default Lighting", success, details)
            return success
        except Exception as e:
            self.log_test("Set Default Lighting", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🧪 SMART STADIUM API TEST SUITE")
        print("=" * 50)
        print(f"🎯 Testing API at: {self.base_url}")
        print()
        
        tests = [
            self.test_health_endpoint,
            self.test_system_status,
            self.test_get_devices,
            self.test_get_teams,
            self.test_get_current_team,
            self.test_celebration_types,
            self.test_team_search,
            self.test_change_team,
            self.test_device_refresh,
            self.test_set_default_lighting,
            self.test_sack_celebration,  # Last since it triggers lights
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                time.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        print()
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 30)
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! Your Smart Stadium API is working perfectly!")
        else:
            print(f"\n⚠️ Some tests failed. Check the details above.")
        
        return passed == total

def main():
    """Main test runner"""
    print("🏈 Smart Stadium API Testing")
    print("Waiting 2 seconds for server to be ready...")
    time.sleep(2)
    
    tester = SmartStadiumAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Your API is ready for:")
        print("   📱 Mobile app integration")
        print("   🖥️ Web dashboard control")
        print("   🎮 Game day automation")
        print("   📡 Real-time celebrations")
    
    return success

if __name__ == "__main__":
    main()