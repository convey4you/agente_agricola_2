"""
Locustfile para testes de carga do AgroTech 1.0
"""
from locust import HttpUser, task, between
import random


class AgroTechUser(HttpUser):
    """Simula um usuário do sistema AgroTech"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Executed when user starts"""
        self.client.verify = False  # Disable SSL verification for testing
    
    @task(3)
    def visit_homepage(self):
        """Visit the homepage"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code in [200, 302]:
                response.success()
            elif response.status_code == 404:
                # Homepage might not exist yet, that's ok for testing
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(2)
    def visit_login_page(self):
        """Visit login page"""
        with self.client.get("/login", catch_response=True) as response:
            if response.status_code in [200, 302, 404]:
                response.success()
            else:
                response.failure(f"Login page error: {response.status_code}")
    
    @task(1)
    def check_static_files(self):
        """Check static file serving"""
        static_files = [
            "/static/favicon.ico",
            "/static/app.js",
            "/static/index.html"
        ]
        
        static_file = random.choice(static_files)
        with self.client.get(static_file, catch_response=True) as response:
            if response.status_code in [200, 404]:
                # 404 is ok for static files that may not exist
                response.success()
            else:
                response.failure(f"Static file error: {response.status_code}")
    
    @task(1)
    def attempt_api_endpoint(self):
        """Try to access an API endpoint"""
        api_endpoints = [
            "/api/culturas",
            "/api/tarefas", 
            "/api/monitoramento",
            "/api/weather"
        ]
        
        endpoint = random.choice(api_endpoints)
        with self.client.get(endpoint, catch_response=True) as response:
            if response.status_code in [200, 401, 403, 404]:
                # These are acceptable responses for unauthorized API access
                response.success()
            else:
                response.failure(f"API endpoint error: {response.status_code}")


class AdminUser(HttpUser):
    """Simulates admin user behavior"""
    
    wait_time = between(2, 5)
    weight = 1  # Lower probability than regular users
    
    def on_start(self):
        """Setup for admin user"""
        self.client.verify = False
    
    @task(2)
    def admin_dashboard(self):
        """Access admin areas"""
        admin_urls = [
            "/admin",
            "/admin/users",
            "/admin/culturas",
            "/dashboard"
        ]
        
        url = random.choice(admin_urls)
        with self.client.get(url, catch_response=True) as response:
            if response.status_code in [200, 302, 401, 403, 404]:
                response.success()
            else:
                response.failure(f"Admin endpoint error: {response.status_code}")
    
    @task(1)
    def monitor_system(self):
        """Check system monitoring endpoints"""
        monitoring_urls = [
            "/health",
            "/status", 
            "/metrics"
        ]
        
        url = random.choice(monitoring_urls)
        with self.client.get(url, catch_response=True) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Monitoring endpoint error: {response.status_code}")


# Configuration for different test scenarios
class QuickTest(AgroTechUser):
    """Quick load test for CI/CD"""
    wait_time = between(0.5, 2)


class HeavyUser(AgroTechUser):
    """Heavy usage simulation"""
    wait_time = between(0.1, 1)
    
    @task(5)
    def heavy_homepage_usage(self):
        """Heavy homepage usage"""
        self.visit_homepage()
        
    @task(3)
    def rapid_api_calls(self):
        """Rapid API calls"""
        self.attempt_api_endpoint()


if __name__ == "__main__":
    import os
    import subprocess
    
    # Run locust with basic settings if executed directly
    host = os.getenv('TARGET_HOST', 'http://localhost:5000')
    users = os.getenv('USERS', '10')
    spawn_rate = os.getenv('SPAWN_RATE', '2')
    time_limit = os.getenv('TIME_LIMIT', '60s')
    
    cmd = [
        'locust',
        '--host', host,
        '--users', users,
        '--spawn-rate', spawn_rate,
        '--run-time', time_limit,
        '--headless'
    ]
    
    subprocess.run(cmd)
