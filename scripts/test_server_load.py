import time
import requests
import json

def test_server():
    base_url = "http://127.0.0.1:7860"
    print("Checking if FastAPI server is responsive on Port 7860...\n")
    
    # Wait for server to boot up
    server_up = False
    for _ in range(5):
        try:
            r = requests.get(f"{base_url}/")
            if r.status_code == 200:
                server_up = True
                print(f"[SUCCESS] Root Endpoint: {r.json()}")
                break
        except requests.ConnectionError:
            time.sleep(1)
            
    if not server_up:
        print("Server failed to respond.")
        return

    print("\n" + "="*50)
    print("TEST 1: INITIALIZING 'HARD' TASK ENVIRONMENT")
    print("="*50)
    r_reset = requests.post(f"{base_url}/reset/hard")
    print(json.dumps(r_reset.json(), indent=2))

    print("\n" + "="*50)
    print("TEST 2: SENDING HEAVY JSON / LARGE DATA TO /step API")
    print("="*50)
    # We send an intentionally bloated reason string to simulate a heavy 'large data' payload
    action_payload = {
        "command": "READ_LOGS",
        "target": "file_server_main",
        "reason": "Automated reasoning log padding: " * 500
    }
    
    start_time = time.time()
    r_step = requests.post(f"{base_url}/step", json=action_payload)
    end_time = time.time()
    
    print(f"API Latency: {round((end_time - start_time) * 1000, 2)} ms")
    print("Server Response:")
    print(json.dumps(r_step.json(), indent=2))

if __name__ == "__main__":
    test_server()
