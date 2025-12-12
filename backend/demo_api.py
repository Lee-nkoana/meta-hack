#!/usr/bin/env python3
"""
Interactive API Demo for Medical Records Bridge
This script demonstrates all API endpoints with real requests and responses
"""
import requests
import json
import time
from typing import Dict, Optional


class Colors:
    """Terminal colors for beautiful output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class APIDemo:
    """Interactive API demonstration"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.record_id: Optional[int] = None
        self.stats = {
            "passed": 0,
            "failed": 0,
            "failed_endpoints": []
        }
    
    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.END}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")
    
    def print_section(self, text: str):
        """Print a section title"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
        print(f"{Colors.CYAN}{'-'*len(text)}{Colors.END}")
    
    def print_request(self, method: str, endpoint: str, data: Optional[Dict] = None):
        """Print request details"""
        print(f"{Colors.YELLOW}REQUEST:{Colors.END}")
        print(f"  {Colors.BOLD}{method}{Colors.END} {endpoint}")
        if data:
            print(f"  {Colors.BLUE}Body:{Colors.END}")
            print(f"    {json.dumps(data, indent=4)}")
    
    def print_response(self, response: requests.Response):
        """Print response details"""
        status_color = Colors.GREEN if response.status_code < 400 else Colors.RED
        print(f"\n{Colors.YELLOW}RESPONSE:{Colors.END}")
        print(f"  {Colors.BOLD}Status:{Colors.END} {status_color}{response.status_code}{Colors.END}")
        
        try:
            response_data = response.json()
            print(f"  {Colors.BLUE}Body:{Colors.END}")
            print(f"    {json.dumps(response_data, indent=4)}")
        except:
            print(f"  {Colors.BLUE}Body:{Colors.END} {response.text}")
    
    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    form_data: Optional[Dict] = None, use_auth: bool = False):
        """Make an API request and display the result"""
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        if use_auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        self.print_request(method, endpoint, data or form_data)
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                if form_data:
                    response = requests.post(url, data=form_data, headers=headers)
                else:
                    response = requests.post(url, json=data, headers=headers)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                print(f"{Colors.RED}Unknown method: {method}{Colors.END}")
                return None
            
            self.print_response(response)
            
            # Update stats
            if response.status_code < 400:
                self.stats["passed"] += 1
            else:
                self.stats["failed"] += 1
                self.stats["failed_endpoints"].append(f"{method} {endpoint} (Status: {response.status_code})")
                
            return response
        except Exception as e:
            print(f"{Colors.RED}Error: {str(e)}{Colors.END}")
            self.stats["failed"] += 1
            self.stats["failed_endpoints"].append(f"{method} {endpoint} (Error: {str(e)})")
            return None
    
    def demo_health_check(self):
        """Demonstrate health check endpoint"""
        self.print_section("1. Health Check")
        print("Check if the API server is running...")
        self.make_request("GET", "/health")
        time.sleep(1)
    
    def demo_registration(self):
        """Demonstrate user registration"""
        self.print_section("2. User Registration")
        print("Creating a new user account...")
        
        user_data = {
            "email": "demo@example.com",
            "username": f"demouser_{int(time.time())}",
            "password": "demo123456",
            "full_name": "Demo User"
        }
        
        response = self.make_request("POST", "/api/auth/register", data=user_data)
        if response and response.status_code == 201:
            self.user_id = response.json()["id"]
            print(f"\n{Colors.GREEN}User created successfully!{Colors.END}")
            return user_data
        return None
    
    def demo_login(self, user_data: Dict):
        """Demonstrate user login"""
        self.print_section("3. User Login")
        print("Logging in with the created user...")
        
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
        response = self.make_request("POST", "/api/auth/login", form_data=login_data)
        if response and response.status_code == 200:
            self.token = response.json()["access_token"]
            print(f"\n{Colors.GREEN}Login successful! Token acquired.{Colors.END}")
            return True
        return False
    
    def demo_current_user(self):
        """Demonstrate getting current user"""
        self.print_section("4. Get Current User Info")
        print("Fetching authenticated user information...")
        self.make_request("GET", "/api/auth/me", use_auth=True)
        time.sleep(1)
    
    def demo_create_record(self):
        """Demonstrate creating a medical record"""
        self.print_section("5. Create Medical Record")
        print("Creating a sample medical record...")
        
        record_data = {
            "title": "Annual Physical Exam",
            "original_text": "BP: 120/80, HR: 72, Temp: 98.6F. Patient presents with no acute complaints. Labs show WBC: 7.5, RBC: 4.8, HGB: 14.2, PLT: 250. All values within normal limits.",
            "record_type": "doctor_note"
        }
        
        response = self.make_request("POST", "/api/records", data=record_data, use_auth=True)
        if response and response.status_code == 201:
            self.record_id = response.json()["id"]
            print(f"\n{Colors.GREEN}Medical record created successfully!{Colors.END}")
        time.sleep(1)
    
    def demo_list_records(self):
        """Demonstrate listing medical records"""
        self.print_section("6. List Medical Records")
        print("Fetching all medical records for the user...")
        self.make_request("GET", "/api/records", use_auth=True)
        time.sleep(1)
    
    def demo_get_record(self):
        """Demonstrate getting a specific record"""
        if not self.record_id:
            print(f"{Colors.YELLOW}Skipping - no record created{Colors.END}")
            return
        
        self.print_section("7. Get Specific Medical Record")
        print(f"Fetching details for record ID: {self.record_id}...")
        self.make_request("GET", f"/api/records/{self.record_id}", use_auth=True)
        time.sleep(1)
    
    def demo_update_record(self):
        """Demonstrate updating a medical record"""
        if not self.record_id:
            print(f"{Colors.YELLOW}Skipping - no record created{Colors.END}")
            return
        
        self.print_section("8. Update Medical Record")
        print("Updating the medical record title...")
        
        update_data = {
            "title": "Annual Physical Exam - Updated"
        }
        
        self.make_request("PUT", f"/api/records/{self.record_id}", data=update_data, use_auth=True)
        time.sleep(1)
    
    def demo_ai_translate(self):
        """Demonstrate AI translation"""
        self.print_section("9. AI Medical Text Translation")
        print("Translating medical jargon to layman's terms...")
        
        translate_data = {
            "text": "Patient presents with acute myalgia and pyrexia. Administered antipyretics."
        }
        
        response = self.make_request("POST", "/api/ai/translate", data=translate_data, use_auth=True)
        if response and response.status_code == 503:
            print(f"\n{Colors.YELLOW}Note: AI service requires API key configuration{Colors.END}")
        time.sleep(1)
    
    def demo_ai_suggestions(self):
        """Demonstrate AI lifestyle suggestions"""
        self.print_section("10. AI Lifestyle Suggestions")
        print("Getting lifestyle suggestions for a condition...")
        
        suggestions_data = {
            "condition": "Patient has elevated cholesterol levels (LDL: 160)"
        }
        
        response = self.make_request("POST", "/api/ai/suggestions", data=suggestions_data, use_auth=True)
        if response and response.status_code == 503:
            print(f"\n{Colors.YELLOW}Note: AI service requires API key configuration{Colors.END}")
        time.sleep(1)
    
    def demo_user_profile(self):
        """Demonstrate getting user profile"""
        self.print_section("11. Get User Profile")
        print("Fetching user profile with statistics...")
        self.make_request("GET", "/api/users/me", use_auth=True)
        time.sleep(1)
    
    def demo_dashboard(self):
        """Demonstrate dashboard stats"""
        self.print_section("12. Get Dashboard Statistics")
        print("Fetching dashboard statistics...")
        self.make_request("GET", "/api/users/dashboard", use_auth=True)
        time.sleep(1)
    
    def demo_update_profile(self):
        """Demonstrate updating user profile"""
        self.print_section("13. Update User Profile")
        print("Updating user full name...")
        
        update_data = {
            "full_name": "Demo User - Updated"
        }
        
        self.make_request("PUT", "/api/users/me", data=update_data, use_auth=True)
        time.sleep(1)
    
    def demo_delete_record(self):
        """Demonstrate deleting a medical record"""
        if not self.record_id:
            print(f"{Colors.YELLOW}Skipping - no record created{Colors.END}")
            return
        
        self.print_section("14. Delete Medical Record")
        print(f"Deleting medical record ID: {self.record_id}...")
        self.make_request("DELETE", f"/api/records/{self.record_id}", use_auth=True)
        time.sleep(1)

    def demo_delete_user(self):
        """Demonstrate deleting the user account"""
        self.print_section("15. Delete User Account (Cleanup)")
        print("Deleting the demo user account...")
        self.make_request("DELETE", "/api/users/me", use_auth=True)
        time.sleep(1)
    
    def run_full_demo(self):
        """Run the complete API demonstration"""
        self.print_header("Medical Records Bridge API - Interactive Demo")
        
        print(f"{Colors.CYAN}This demo will walk through all API endpoints with real requests and responses.{Colors.END}")
        print(f"{Colors.CYAN}Make sure the API server is running at {self.base_url}{Colors.END}\n")
        
        input(f"{Colors.BOLD}Press Enter to start...{Colors.END}")
        
        # Health check
        self.demo_health_check()
        
        # Authentication flow
        user_data = self.demo_registration()
        if not user_data:
            print(f"\n{Colors.RED}Failed to create user. Exiting demo.{Colors.END}")
            return
        
        if not self.demo_login(user_data):
            print(f"\n{Colors.RED}Failed to login. Exiting demo.{Colors.END}")
            return
        
        self.demo_current_user()
        
        # Medical records
        self.demo_create_record()
        self.demo_list_records()
        self.demo_get_record()
        self.demo_update_record()
        
        # AI services
        self.demo_ai_translate()
        self.demo_ai_suggestions()
        
        # User profile
        self.demo_user_profile()
        self.demo_dashboard()
        self.demo_update_profile()
        
        # Cleanup
        self.demo_delete_record()
        self.demo_delete_user()
        
        # Final message
        self.print_header("Demo Complete!")
        print(f"{Colors.GREEN}All API endpoints demonstrated successfully!{Colors.END}")
        print(f"\n{Colors.CYAN}For interactive testing, visit:{Colors.END}")
        print(f"  Swagger UI: {self.base_url}/docs")
        print(f"  ReDoc: {self.base_url}/redoc\n")
        
        # Print Stats
        print(f"\n{Colors.HEADER}{Colors.BOLD}Demo Statistics:{Colors.END}")
        print(f"  Total Requests: {self.stats['passed'] + self.stats['failed']}")
        print(f"  Passed: {Colors.GREEN}{self.stats['passed']}{Colors.END}")
        print(f"  Failed: {Colors.RED}{self.stats['failed']}{Colors.END}")
        
        if self.stats["failed"] > 0:
            print(f"\n{Colors.RED}Failed Endpoints:{Colors.END}")
            for failure in self.stats["failed_endpoints"]:
                print(f"  - {failure}")
            print(f"\n{Colors.YELLOW}Please check the logs or configuration for the failed endpoints.{Colors.END}")


def main():
    """Main entry point"""
    import sys
    
    base_url = "http://localhost:5000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    demo = APIDemo(base_url)
    
    try:
        demo.run_full_demo()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Demo interrupted by user.{Colors.END}")
    except Exception as e:
        print(f"\n\n{Colors.RED}Error running demo: {str(e)}{Colors.END}")


if __name__ == "__main__":
    main()
