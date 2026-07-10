"""
End-to-end test for the /api/chat/query endpoint.
"""
import requests
import json

BASE_URL = "http://localhost:3001"

def test_chat_query():
    payload = {
        "query": "Show me cases where victim is lakshmi devi",
        "session_id": "test-session-123"
    }
    print(f"\n[TEST] Sending query: {payload['query']}")
    
    response = requests.post(
        f"{BASE_URL}/api/chat/query",
        json=payload,
        timeout=120
    )
    
    print(f"[TEST] Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n[RESPONSE] message_id: {data.get('message_id')}")
        print(f"[RESPONSE] response_text: {data.get('response_text')}")
        print(f"[RESPONSE] sql_query: {data.get('sql_query')}")
        print(f"[RESPONSE] scanned_records: {data.get('scanned_records')}")
        print(f"[RESPONSE] sources: {data.get('sources')}")
        print(f"[RESPONSE] entities count: {len(data.get('entities', []))}")
        print(f"[RESPONSE] follow_ups: {data.get('follow_ups')}")
        print(f"[RESPONSE] table_data count: {len(data.get('table_data', []))}")
        if data.get('table_data'):
            print(f"[RESPONSE] first table row: {data['table_data'][0]}")
        print("\n[TEST] PASSED")
    else:
        print(f"[TEST] FAILED")
        print(f"[TEST] Response: {response.text}")


def test_new_conversation():
    print(f"\n[TEST] Creating new conversation...")
    response = requests.post(f"{BASE_URL}/api/chat/new", json={}, timeout=10)
    print(f"[TEST] Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"[RESPONSE] session_id: {data.get('session_id')}")
        print("[TEST] PASSED")
    else:
        print(f"[TEST] FAILED: {response.text}")


def test_chat_history():
    print(f"\n[TEST] Fetching chat history...")
    response = requests.get(f"{BASE_URL}/api/chat/history", timeout=10)
    print(f"[TEST] Status code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        convs = data.get('conversations', [])
        print(f"[RESPONSE] conversations count: {len(convs)}")
        if convs:
            print(f"[RESPONSE] first conversation: {convs[0]}")
        print("[TEST] PASSED")
    else:
        print(f"[TEST] FAILED: {response.text}")


def test_db_status():
    print(f"\n[TEST] Checking DB status (row counts)...")
    try:
        response = requests.get(f"{BASE_URL}/api/chat/db-status", timeout=10)
        print(f"[TEST] Status code: {response.status_code}")
        if response.status_code == 200:
            print("[RESPONSE] Database Table Counts:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"[TEST] FAILED: {response.text}")
    except Exception as e:
        print(f"[TEST] Connection failed: {e}")


if __name__ == "__main__":
    test_db_status()
    test_new_conversation()
    test_chat_query()
    test_chat_history()
