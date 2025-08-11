#!/usr/bin/env python3
"""
Smoke Tests for AgroTech 1.0
Performs basic functional tests after deployment
"""

import argparse
import requests
import sys
import time
import json
from typing import Dict, List, Optional
from urllib.parse import urljoin

class SmokeTests:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.results: List[Dict] = []
        
        # Set common headers
        self.session.headers.update({
            'User-Agent': 'AgroTech-SmokeTest/1.0',
            'Accept': 'application/json'
        })
    
    def log_result(self, test_name: str, passed: bool, message: str = "", 
                   response_time: float = 0, status_code: int = 0):
        """Log test result"""
        result = {
            'test': test_name,
            'passed': passed,
            'message': message,
            'response_time_ms': round(response_time * 1000, 2),
            'status_code': status_code,
            'timestamp': time.time()
        }
        self.results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"    {message}")
        if response_time > 0:
            print(f"    Response time: {result['response_time_ms']}ms")
    
    def test_health_endpoint(self) -> bool:
        """Test basic health endpoint"""
        try:
            start_time = time.time()
            response = self.session.get(
                urljoin(self.base_url, '/health'),
                timeout=self.timeout
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_result(
                        "Health Check", True, 
                        f"Application healthy: {data.get('version', 'unknown')}",
                        response_time, response.status_code
                    )
                    return True
                else:
                    self.log_result(
                        "Health Check", False,
                        f"Unhealthy status: {data.get('status')}",
                        response_time, response.status_code
                    )
                    return False
            else:
                self.log_result(
                    "Health Check", False,
                    f"HTTP {response.status_code}: {response.text[:100]}",
                    response_time, response.status_code
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Health Check", False, f"Request failed: {str(e)}")
            return False
    
    def test_api_status(self) -> bool:
        """Test API status endpoint"""
        try:
            start_time = time.time()
            response = self.session.get(
                urljoin(self.base_url, '/api/v1/status'),
                timeout=self.timeout
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "API Status", True,
                    f"API version: {data.get('api_version', 'unknown')}",
                    response_time, response.status_code
                )
                return True
            else:
                self.log_result(
                    "API Status", False,
                    f"HTTP {response.status_code}",
                    response_time, response.status_code
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("API Status", False, f"Request failed: {str(e)}")
            return False
    
    def test_database_connectivity(self) -> bool:
        """Test database connectivity through API"""
        try:
            start_time = time.time()
            response = self.session.get(
                urljoin(self.base_url, '/api/v1/health/database'),
                timeout=self.timeout
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('database_status') == 'connected':
                    self.log_result(
                        "Database Connectivity", True,
                        f"DB connected: {data.get('database_type', 'unknown')}",
                        response_time, response.status_code
                    )
                    return True
                else:
                    self.log_result(
                        "Database Connectivity", False,
                        f"DB not connected: {data.get('database_status')}",
                        response_time, response.status_code
                    )
                    return False
            else:
                self.log_result(
                    "Database Connectivity", False,
                    f"HTTP {response.status_code}",
                    response_time, response.status_code
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Database Connectivity", False, f"Request failed: {str(e)}")
            return False
    
    def test_authentication_endpoints(self) -> bool:
        """Test authentication endpoints are accessible"""
        try:
            start_time = time.time()
            response = self.session.post(
                urljoin(self.base_url, '/api/v1/auth/login'),
                json={'email': 'test@example.com', 'password': 'wrongpassword'},
                timeout=self.timeout
            )
            response_time = time.time() - start_time
            
            # We expect a 401 or 400 for invalid credentials, not a 500
            if response.status_code in [400, 401, 422]:
                self.log_result(
                    "Authentication Endpoint", True,
                    f"Auth endpoint responding correctly",
                    response_time, response.status_code
                )
                return True
            else:
                self.log_result(
                    "Authentication Endpoint", False,
                    f"Unexpected status: HTTP {response.status_code}",
                    response_time, response.status_code
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Authentication Endpoint", False, f"Request failed: {str(e)}")
            return False
    
    def test_static_assets(self) -> bool:
        """Test static assets are being served"""
        try:
            start_time = time.time()
            response = self.session.get(
                urljoin(self.base_url, '/static/app.js'),
                timeout=self.timeout
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.log_result(
                    "Static Assets", True,
                    f"Static files served correctly",
                    response_time, response.status_code
                )
                return True
            else:
                self.log_result(
                    "Static Assets", False,
                    f"HTTP {response.status_code}",
                    response_time, response.status_code
                )
                return False
                
        except requests.exceptions.RequestException as e:
            # Static assets might not be critical for basic functionality
            self.log_result("Static Assets", False, f"Request failed: {str(e)}")
            return False
    
    def test_response_times(self) -> bool:
        """Test that response times are acceptable"""
        endpoints = [
            '/health',
            '/api/v1/status',
            '/'  # Main page
        ]
        
        all_fast = True
        max_acceptable_time = 2.0  # 2 seconds
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = self.session.get(
                    urljoin(self.base_url, endpoint),
                    timeout=self.timeout
                )
                response_time = time.time() - start_time
                
                if response_time <= max_acceptable_time:
                    self.log_result(
                        f"Response Time - {endpoint}", True,
                        f"Fast response: {round(response_time * 1000)}ms",
                        response_time, response.status_code
                    )
                else:
                    self.log_result(
                        f"Response Time - {endpoint}", False,
                        f"Slow response: {round(response_time * 1000)}ms > {max_acceptable_time}s",
                        response_time, response.status_code
                    )
                    all_fast = False
                    
            except requests.exceptions.RequestException as e:
                self.log_result(f"Response Time - {endpoint}", False, f"Request failed: {str(e)}")
                all_fast = False
        
        return all_fast
    
    def test_security_headers(self) -> bool:
        """Test that security headers are present"""
        try:
            start_time = time.time()
            response = self.session.get(
                urljoin(self.base_url, '/'),
                timeout=self.timeout
            )
            response_time = time.time() - start_time
            
            security_headers = [
                'X-Content-Type-Options',
                'X-Frame-Options',
                'X-XSS-Protection'
            ]
            
            present_headers = []
            missing_headers = []
            
            for header in security_headers:
                if header in response.headers:
                    present_headers.append(header)
                else:
                    missing_headers.append(header)
            
            if len(present_headers) >= len(security_headers) * 0.7:  # At least 70%
                self.log_result(
                    "Security Headers", True,
                    f"Security headers present: {', '.join(present_headers)}",
                    response_time, response.status_code
                )
                return True
            else:
                self.log_result(
                    "Security Headers", False,
                    f"Missing headers: {', '.join(missing_headers)}",
                    response_time, response.status_code
                )
                return False
                
        except requests.exceptions.RequestException as e:
            self.log_result("Security Headers", False, f"Request failed: {str(e)}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all smoke tests"""
        print(f"🔥 Running smoke tests against: {self.base_url}")
        print("=" * 60)
        
        test_methods = [
            self.test_health_endpoint,
            self.test_api_status,
            self.test_database_connectivity,
            self.test_authentication_endpoints,
            self.test_static_assets,
            self.test_response_times,
            self.test_security_headers
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ FAIL: {test_method.__name__} - Unexpected error: {str(e)}")
        
        print("\n" + "=" * 60)
        print(f"📊 SMOKE TEST RESULTS")
        print(f"Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Summary
        if passed_tests == total_tests:
            print("🎉 All smoke tests passed!")
            return True
        elif passed_tests >= total_tests * 0.8:  # 80% pass rate
            print("⚠️  Most smoke tests passed, minor issues detected")
            return True
        else:
            print("❌ Smoke tests failed, deployment may have issues")
            return False
    
    def save_results(self, filename: str):
        """Save test results to JSON file"""
        summary = {
            'base_url': self.base_url,
            'timestamp': time.time(),
            'total_tests': len(self.results),
            'passed_tests': len([r for r in self.results if r['passed']]),
            'failed_tests': len([r for r in self.results if not r['passed']]),
            'average_response_time_ms': sum(r['response_time_ms'] for r in self.results) / len(self.results) if self.results else 0,
            'results': self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📋 Results saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(description="AgroTech Smoke Tests")
    parser.add_argument('--environment', choices=['staging', 'production'], 
                       default='staging', help='Environment to test')
    parser.add_argument('--url', help='Custom base URL to test')
    parser.add_argument('--timeout', type=int, default=30, help='Request timeout in seconds')
    parser.add_argument('--output', help='Output file for results (JSON)')
    
    args = parser.parse_args()
    
    # Determine base URL
    if args.url:
        base_url = args.url
    elif args.environment == 'staging':
        base_url = 'https://staging.agrotech.convey4you.com'
    elif args.environment == 'production':
        base_url = 'https://agrotech.convey4you.com'
    else:
        print("Error: Must specify --url or --environment")
        return 1
    
    # Run smoke tests
    smoke_tests = SmokeTests(base_url, args.timeout)
    success = smoke_tests.run_all_tests()
    
    # Save results if requested
    if args.output:
        smoke_tests.save_results(args.output)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
