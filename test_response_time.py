"""
Response Time Testing Script for ManHas System
Tests various endpoints and measures response times
"""

import time
import requests
import statistics
from typing import List, Dict

# Configuration
BASE_URL = "http://localhost:8000"
TEST_ITERATIONS = 5

def test_endpoint(endpoint: str, method: str = "POST", data: Dict = None) -> float:
    """
    Test a single endpoint and return response time in seconds
    """
    url = f"{BASE_URL}{endpoint}"
    
    start_time = time.time()
    
    try:
        if method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            response = requests.get(url, timeout=30)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"  Status: {response.status_code}, Time: {response_time:.3f}s")
        return response_time
    except Exception as e:
        print(f"  Error: {e}")
        return -1

def test_chat_endpoint():
    """Test the /chat endpoint"""
    print("\n=== Testing /chat Endpoint ===")
    
    data = {
        "messages": [
            {"role": "user", "content": "What is Python?", "attachments": None}
        ]
    }
    
    times = []
    for i in range(TEST_ITERATIONS):
        print(f"Iteration {i+1}/{TEST_ITERATIONS}:")
        response_time = test_endpoint("/chat", "POST", data)
        if response_time > 0:
            times.append(response_time)
        time.sleep(1)  # Wait between requests
    
    if times:
        print(f"\nAverage: {statistics.mean(times):.3f}s")
        print(f"Min: {min(times):.3f}s")
        print(f"Max: {max(times):.3f}s")
        print(f"Median: {statistics.median(times):.3f}s")

def test_chat_stream_endpoint():
    """Test the /chat/stream endpoint"""
    print("\n=== Testing /chat/stream Endpoint ===")
    
    data = {
        "messages": [
            {"role": "user", "content": "What is Python?", "attachments": None}
        ]
    }
    
    times = []
    for i in range(TEST_ITERATIONS):
        print(f"Iteration {i+1}/{TEST_ITERATIONS}:")
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{BASE_URL}/chat/stream",
                json=data,
                stream=True,
                timeout=30
            )
            
            # Consume the stream
            for chunk in response.iter_lines():
                if chunk:
                    pass
            
            end_time = time.time()
            response_time = end_time - start_time
            print(f"  Status: {response.status_code}, Time: {response_time:.3f}s")
            times.append(response_time)
        except Exception as e:
            print(f"  Error: {e}")
        
        time.sleep(1)
    
    if times:
        print(f"\nAverage: {statistics.mean(times):.3f}s")
        print(f"Min: {min(times):.3f}s")
        print(f"Max: {max(times):.3f}s")
        print(f"Median: {statistics.median(times):.3f}s")

def test_rag_query():
    """Test RAG agent response time"""
    print("\n=== Testing RAG Query ===")
    
    data = {
        "messages": [
            {"role": "user", "content": "What is TCP/IP?", "attachments": None}
        ]
    }
    
    times = []
    for i in range(TEST_ITERATIONS):
        print(f"Iteration {i+1}/{TEST_ITERATIONS}:")
        response_time = test_endpoint("/chat", "POST", data)
        if response_time > 0:
            times.append(response_time)
        time.sleep(1)
    
    if times:
        print(f"\nAverage: {statistics.mean(times):.3f}s")
        print(f"Min: {min(times):.3f}s")
        print(f"Max: {max(times):.3f}s")

def test_code_generation():
    """Test code generation response time"""
    print("\n=== Testing Code Generation ===")
    
    data = {
        "messages": [
            {"role": "user", "content": "Write a Python function to add two numbers", "attachments": None}
        ]
    }
    
    times = []
    for i in range(TEST_ITERATIONS):
        print(f"Iteration {i+1}/{TEST_ITERATIONS}:")
        response_time = test_endpoint("/chat", "POST", data)
        if response_time > 0:
            times.append(response_time)
        time.sleep(1)
    
    if times:
        print(f"\nAverage: {statistics.mean(times):.3f}s")
        print(f"Min: {min(times):.3f}s")
        print(f"Max: {max(times):.3f}s")

def test_health_endpoint():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    
    times = []
    for i in range(TEST_ITERATIONS):
        print(f"Iteration {i+1}/{TEST_ITERATIONS}:")
        response_time = test_endpoint("/", "GET")
        if response_time > 0:
            times.append(response_time)
        time.sleep(0.1)
    
    if times:
        print(f"\nAverage: {statistics.mean(times):.3f}s")
        print(f"Min: {min(times):.3f}s")
        print(f"Max: {max(times):.3f}s")

def test_list_chats():
    """Test list chats endpoint"""
    print("\n=== Testing List Chats ===")
    
    times = []
    for i in range(TEST_ITERATIONS):
        print(f"Iteration {i+1}/{TEST_ITERATIONS}:")
        response_time = test_endpoint("/chats", "GET")
        if response_time > 0:
            times.append(response_time)
        time.sleep(0.1)
    
    if times:
        print(f"\nAverage: {statistics.mean(times):.3f}s")
        print(f"Min: {min(times):.3f}s")
        print(f"Max: {max(times):.3f}s")

def main():
    """Run all tests"""
    print("=" * 50)
    print("ManHas System Response Time Testing")
    print("=" * 50)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Iterations: {TEST_ITERATIONS}")
    
    # Test health check first
    test_health_endpoint()
    
    # Test main endpoints
    test_chat_endpoint()
    test_chat_stream_endpoint()
    test_list_chats()
    
    # Test specific agent types
    test_rag_query()
    test_code_generation()
    
    print("\n" + "=" * 50)
    print("Testing Complete")
    print("=" * 50)

if __name__ == "__main__":
    main()
