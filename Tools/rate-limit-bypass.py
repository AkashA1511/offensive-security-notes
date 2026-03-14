#!/usr/bin/env python3
"""
Advanced Rate Limit Testing Framework
"""

"""
# Install required packages
pip install requests fake-useragent colorama

"""
# CodeRevenant 

import requests
import time
import random
import string
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

class AdvancedRateLimitTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = []
        
    def test_header_spoofing(self, endpoint):
        """Test various header spoofing techniques"""
        headers_to_test = [
            {'X-Forwarded-For': self.random_ip()},
            {'X-Real-IP': self.random_ip()},
            {'X-Originating-IP': self.random_ip()},
            {'X-Remote-IP': self.random_ip()},
            {'X-Remote-Addr': self.random_ip()},
            {'X-Client-IP': self.random_ip()},
            {'X-Host': self.random_ip()},
            {'X-Forwarded-Host': self.random_ip()},
        ]
        
        for headers in headers_to_test:
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                headers={**self.get_base_headers(), **headers}
            )
            self.analyze_response(response, f"Header spoof: {headers}")
    
    def test_session_isolation(self, endpoint, num_sessions=20):
        """Test if rate limiting is per-session"""
        sessions = []
        
        for i in range(num_sessions):
            # Create new session
            new_session = requests.Session()
            
            # Add unique cookies
            new_session.cookies.set('session_id', self.random_string(32))
            new_session.cookies.set('csrf_token', self.random_string(16))
            
            sessions.append(new_session)
        
        # Send requests with different sessions
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for session in sessions:
                future = executor.submit(
                    session.get,
                    f"{self.base_url}{endpoint}",
                    headers=self.get_base_headers()
                )
                futures.append(future)
            
            for future in as_completed(futures):
                response = future.result()
                self.analyze_response(response, "Session isolation test")
    
    def test_request_fragmentation(self, endpoint):
        """Test splitting requests across time windows"""
        windows = [
            {'requests': 10, 'delay': 60},   # 10 requests per minute
            {'requests': 50, 'delay': 3600}, # 50 requests per hour
            {'requests': 100, 'delay': 86400} # 100 requests per day
        ]
        
        for window in windows:
            print(f"\n[*] Testing {window['requests']} requests over {window['delay']}s window")
            
            for i in range(window['requests']):
                response = self.session.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.get_base_headers()
                )
                
                self.analyze_response(response, f"Fragmentation test - request {i+1}")
                
                # Add jitter to avoid pattern detection
                delay = (window['delay'] / window['requests']) * random.uniform(0.8, 1.2)
                time.sleep(delay)
    
    def test_case_sensitivity(self, endpoint):
        """Test if rate limiting is case-sensitive"""
        variations = [
            endpoint.upper(),
            endpoint.lower(),
            endpoint.title(),
            endpoint + '/',
            endpoint + '?',
            endpoint + '#',
            endpoint.replace('/', '//'),
        ]
        
        for var in variations:
            response = self.session.get(
                f"{self.base_url}{var}",
                headers=self.get_base_headers()
            )
            self.analyze_response(response, f"Case sensitivity: {var}")
    
    def test_encoding_bypass(self, endpoint):
        """Test URL encoding bypass techniques"""
        payloads = [
            endpoint,
            requests.utils.quote(endpoint),
            endpoint.replace('/', '%2F'),
            endpoint.replace('?', '%3F'),
            endpoint.replace('=', '%3D'),
            endpoint.replace('&', '%26'),
        ]
        
        for payload in payloads:
            response = self.session.get(
                f"{self.base_url}{payload}",
                headers=self.get_base_headers()
            )
            self.analyze_response(response, f"Encoding test: {payload}")
    
    def random_ip(self):
        """Generate random IP address"""
        return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    
    def random_string(self, length):
        """Generate random string"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def get_base_headers(self):
        """Get base headers with random user agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def analyze_response(self, response, test_name):
        """Analyze response for bypass indicators"""
        result = {
            'test': test_name,
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'content_length': len(response.content),
            'timestamp': time.time()
        }
        
        # Check for rate limit indicators
        rate_limit_headers = ['X-RateLimit-Limit', 'X-RateLimit-Remaining', 
                             'X-RateLimit-Reset', 'Retry-After']
        
        for header in rate_limit_headers:
            if header in response.headers:
                result[header] = response.headers[header]
        
        self.results.append(result)
        
        # Print result
        status_color = '\033[92m' if response.status_code == 200 else '\033[91m'
        print(f"{status_color}[{response.status_code}]\033[0m {test_name}")
        
        return result
    
    def save_results(self, filename='rate_limit_test_results.json'):
        """Save test results to file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n[*] Results saved to {filename}")

# Example usage for testing
if __name__ == "__main__":
    print("⚠️  WARNING: Only use on authorized systems!\n")
    
    # Configure for your test application
    tester = AdvancedRateLimitTester("http://localhost:8080")
    
    # Run tests
    tester.test_header_spoofing("/api/login")
    tester.test_session_isolation("/api/data", num_sessions=10)
    tester.test_request_fragmentation("/api/search")
    tester.test_case_sensitivity("/api/endpoint")
    tester.test_encoding_bypass("/api/endpoint")
    
    # Save results
    tester.save_results()
