#!/usr/bin/env python3
"""
Health Check Script for AgroTech 1.0
Comprehensive health monitoring for deployments
"""

import argparse
import requests
import sys
import time
import json
from typing import Dict, List, Optional
from urllib.parse import urljoin

class HealthChecker:
    def __init__(self, base_url: str, timeout: int = 60):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.health_status = {
            'overall': 'unknown',
            'components': {},
            'metrics': {},
            'start_time': time.time()
        }
        
        # Set headers
        self.session.headers.update({
            'User-Agent': 'AgroTech-HealthCheck/1.0',
            'Accept': 'application/json'
        })
    
    def check_basic_connectivity(self) -> bool:
        """Check basic HTTP connectivity"""
        try:
            print("🔗 Checking basic connectivity...")
            response = self.session.get(
                urljoin(self.base_url, '/health'),
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Basic connectivity: OK")
                self.health_status['components']['connectivity'] = 'healthy'
                return True
            else:
                print(f"❌ Basic connectivity: HTTP {response.status_code}")
                self.health_status['components']['connectivity'] = 'unhealthy'
                return False
                
        except Exception as e:
            print(f"❌ Basic connectivity: {str(e)}")
            self.health_status['components']['connectivity'] = 'unhealthy'
            return False
    
    def check_application_health(self) -> bool:
        """Check detailed application health"""
        try:
            print("🏥 Checking application health...")
            response = self.session.get(
                urljoin(self.base_url, '/health'),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check overall status
                if data.get('status') == 'healthy':
                    print("✅ Application health: OK")
                    self.health_status['components']['application'] = 'healthy'
                    
                    # Store metrics
                    if 'metrics' in data:
                        self.health_status['metrics'].update(data['metrics'])
                    
                    return True
                else:
                    print(f"❌ Application health: {data.get('status', 'unknown')}")
                    self.health_status['components']['application'] = 'unhealthy'
                    return False
            else:
                print(f"❌ Application health: HTTP {response.status_code}")
                self.health_status['components']['application'] = 'unhealthy'
                return False
                
        except Exception as e:
            print(f"❌ Application health: {str(e)}")
            self.health_status['components']['application'] = 'unhealthy'
            return False
    
    def check_database_health(self) -> bool:
        """Check database connectivity and health"""
        try:
            print("🗄️  Checking database health...")
            response = self.session.get(
                urljoin(self.base_url, '/api/v1/health/database'),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('database_status') == 'connected':
                    print("✅ Database health: OK")
                    self.health_status['components']['database'] = 'healthy'
                    
                    # Store database metrics
                    if 'connection_pool' in data:
                        self.health_status['metrics']['database'] = data['connection_pool']
                    
                    return True
                else:
                    print(f"❌ Database health: {data.get('database_status', 'unknown')}")
                    self.health_status['components']['database'] = 'unhealthy'
                    return False
            else:
                print(f"❌ Database health: HTTP {response.status_code}")
                self.health_status['components']['database'] = 'unhealthy'
                return False
                
        except Exception as e:
            print(f"❌ Database health: {str(e)}")
            self.health_status['components']['database'] = 'unhealthy'
            return False
    
    def check_redis_health(self) -> bool:
        """Check Redis connectivity and health"""
        try:
            print("🔴 Checking Redis health...")
            response = self.session.get(
                urljoin(self.base_url, '/api/v1/health/redis'),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('redis_status') == 'connected':
                    print("✅ Redis health: OK")
                    self.health_status['components']['redis'] = 'healthy'
                    
                    # Store Redis metrics
                    if 'memory_usage' in data:
                        self.health_status['metrics']['redis'] = {
                            'memory_usage': data['memory_usage']
                        }
                    
                    return True
                else:
                    print(f"❌ Redis health: {data.get('redis_status', 'unknown')}")
                    self.health_status['components']['redis'] = 'unhealthy'
                    return False
            else:
                print(f"❌ Redis health: HTTP {response.status_code}")
                self.health_status['components']['redis'] = 'unhealthy'
                return False
                
        except Exception as e:
            print(f"❌ Redis health: {str(e)}")
            self.health_status['components']['redis'] = 'unhealthy'
            return False
    
    def check_api_endpoints(self) -> bool:
        """Check critical API endpoints"""
        print("🔌 Checking API endpoints...")
        
        critical_endpoints = [
            ('/api/v1/status', 'API Status'),
            ('/api/v1/auth/login', 'Authentication'),  # POST endpoint, expect 400/422
            ('/api/v1/culturas', 'Culturas API'),  # Might need auth, expect 401
        ]
        
        healthy_endpoints = 0
        
        for endpoint, name in critical_endpoints:
            try:
                if 'login' in endpoint:
                    # POST request for login endpoint
                    response = self.session.post(
                        urljoin(self.base_url, endpoint),
                        json={'email': 'test', 'password': 'test'},
                        timeout=10
                    )
                    # Expect 400/401/422 for invalid credentials
                    expected_codes = [400, 401, 422]
                else:
                    # GET request for other endpoints
                    response = self.session.get(
                        urljoin(self.base_url, endpoint),
                        timeout=10
                    )
                    # Expect 200 or 401 (if auth required)
                    expected_codes = [200, 401]
                
                if response.status_code in expected_codes:
                    print(f"✅ {name}: OK (HTTP {response.status_code})")
                    healthy_endpoints += 1
                else:
                    print(f"❌ {name}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {name}: {str(e)}")
        
        success_rate = healthy_endpoints / len(critical_endpoints)
        
        if success_rate >= 0.8:  # 80% of endpoints healthy
            self.health_status['components']['api_endpoints'] = 'healthy'
            return True
        else:
            self.health_status['components']['api_endpoints'] = 'unhealthy'
            return False
    
    def check_performance_metrics(self) -> bool:
        """Check performance metrics"""
        print("📊 Checking performance metrics...")
        
        try:
            # Test response times
            start_time = time.time()
            response = self.session.get(
                urljoin(self.base_url, '/health'),
                timeout=self.timeout
            )
            response_time = time.time() - start_time
            
            self.health_status['metrics']['response_time_ms'] = round(response_time * 1000, 2)
            
            if response_time < 2.0:  # Under 2 seconds
                print(f"✅ Response time: {response_time:.2f}s")
                self.health_status['components']['performance'] = 'healthy'
                return True
            elif response_time < 5.0:  # Under 5 seconds
                print(f"⚠️  Response time: {response_time:.2f}s (slow)")
                self.health_status['components']['performance'] = 'degraded'
                return True
            else:
                print(f"❌ Response time: {response_time:.2f}s (too slow)")
                self.health_status['components']['performance'] = 'unhealthy'
                return False
                
        except Exception as e:
            print(f"❌ Performance check: {str(e)}")
            self.health_status['components']['performance'] = 'unhealthy'
            return False
    
    def wait_for_healthy(self, max_wait_time: int = 300) -> bool:
        """Wait for application to become healthy"""
        print(f"⏳ Waiting for application to become healthy (max {max_wait_time}s)...")
        
        start_time = time.time()
        attempt = 1
        
        while time.time() - start_time < max_wait_time:
            print(f"Attempt {attempt}...")
            
            if self.check_basic_connectivity():
                if self.check_application_health():
                    print("🎉 Application is healthy!")
                    return True
            
            attempt += 1
            time.sleep(10)  # Wait 10 seconds between attempts
        
        print(f"❌ Application did not become healthy within {max_wait_time}s")
        return False
    
    def run_comprehensive_check(self) -> bool:
        """Run comprehensive health check"""
        print(f"🏥 Running comprehensive health check: {self.base_url}")
        print("=" * 60)
        
        checks = [
            self.check_basic_connectivity,
            self.check_application_health,
            self.check_database_health,
            self.check_redis_health,
            self.check_api_endpoints,
            self.check_performance_metrics
        ]
        
        healthy_checks = 0
        total_checks = len(checks)
        
        for check in checks:
            try:
                if check():
                    healthy_checks += 1
                time.sleep(1)  # Brief pause between checks
            except Exception as e:
                print(f"❌ Check failed: {check.__name__} - {str(e)}")
        
        # Determine overall health
        health_percentage = (healthy_checks / total_checks) * 100
        
        print("\n" + "=" * 60)
        print("📊 HEALTH CHECK SUMMARY")
        print(f"Healthy components: {healthy_checks}/{total_checks}")
        print(f"Health percentage: {health_percentage:.1f}%")
        
        if health_percentage == 100:
            self.health_status['overall'] = 'healthy'
            print("🎉 System is fully healthy!")
            return True
        elif health_percentage >= 80:
            self.health_status['overall'] = 'degraded'
            print("⚠️  System is mostly healthy with some issues")
            return True
        else:
            self.health_status['overall'] = 'unhealthy'
            print("❌ System has significant health issues")
            return False
    
    def save_health_report(self, filename: str):
        """Save health report to file"""
        self.health_status['end_time'] = time.time()
        self.health_status['duration_seconds'] = self.health_status['end_time'] - self.health_status['start_time']
        
        with open(filename, 'w') as f:
            json.dump(self.health_status, f, indent=2)
        
        print(f"📋 Health report saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(description="AgroTech Health Check")
    parser.add_argument('--url', required=True, help='Base URL to check')
    parser.add_argument('--timeout', type=int, default=60, help='Request timeout in seconds')
    parser.add_argument('--wait', action='store_true', help='Wait for application to become healthy')
    parser.add_argument('--max-wait', type=int, default=300, help='Maximum wait time in seconds')
    parser.add_argument('--output', help='Output file for health report (JSON)')
    
    args = parser.parse_args()
    
    health_checker = HealthChecker(args.url, args.timeout)
    
    if args.wait:
        # Wait mode - useful for deployments
        success = health_checker.wait_for_healthy(args.max_wait)
    else:
        # Comprehensive check mode
        success = health_checker.run_comprehensive_check()
    
    # Save report if requested
    if args.output:
        health_checker.save_health_report(args.output)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
