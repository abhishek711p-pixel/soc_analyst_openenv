import time
import requests
import json
from env import SOCTriageEnv
from schemas import SOCAction

def adversarial_test():
    base_url = "http://127.0.0.1:7860"
    print("==================================================")
    print("🔥 INITIATING ADVERSARIAL STRESS TESTS 🔥")
    print("==================================================\n")

    # Step 1: Initialize the environment
    try:
        requests.post(f"{base_url}/reset/hard")
    except:
        print("Please ensure the FastAPI server is running on port 7860 before running this script.")
        return

    # TEST A: LLM Hallucinates a completely fake command
    print("--- TEST A: The 'Hallucinating AI' Attack ---")
    print("Sending command: 'NUKE_DATACENTER'")
    bad_payload_1 = {
        "command": "NUKE_DATACENTER",
        "target": "127.0.0.1",
        "reason": "Because I'm evil."
    }
    r1 = requests.post(f"{base_url}/step", json=bad_payload_1)
    print(f"Status: {r1.status_code}")
    print(f"Response: {json.dumps(r1.json(), indent=2)}\n")

    # TEST B: LLM forgets to include required fields
    print("--- TEST B: The 'Lazy AI' Attack ---")
    print("Sending command with Missing 'reason' field (which Pydantic requires).")
    bad_payload_2 = {
        "command": "READ_LOGS"
        # Missing 'reason'
    }
    r2 = requests.post(f"{base_url}/step", json=bad_payload_2)
    print(f"Status: {r2.status_code}")
    print(f"Response: {json.dumps(r2.json(), indent=2)}\n")

    # TEST C: Wrong Data Types
    print("--- TEST C: The 'Type Confusion' Attack ---")
    print("Sending integer as target instead of string.")
    bad_payload_3 = {
        "command": "BLOCK_IP",
        "target": 12345678,
        "reason": "Oops, integer."
    }
    r3 = requests.post(f"{base_url}/step", json=bad_payload_3)
    print(f"Status: {r3.status_code}")
    # Show partial response down to the error details
    print(f"Response snippet: {json.dumps(r3.json(), indent=2)[:200]}...\n")
    
    # TEST D: Trying to act after Episode is Finished
    print("--- TEST D: The 'Zombie AI' Attack ---")
    print("Closing the ticket to end the episode gracefully...")
    requests.post(f"{base_url}/step", json={"command": "CLOSE_RESOLVED", "target": None, "reason": "Closing"})
    
    print("\nAttempting to send an action AFTER the environment is done.")
    zombie_payload = {
        "command": "READ_LOGS",
        "target": None,
        "reason": "Agent is stuck in an infinite loop."
    }
    r4 = requests.post(f"{base_url}/step", json=zombie_payload)
    print(f"Status: {r4.status_code} (Should be 200 handled gracefully by our logic)")
    print(f"Reward Output: {r4.json().get('reward', 'ERROR')}")

if __name__ == "__main__":
    adversarial_test()
