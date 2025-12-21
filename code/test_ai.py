# test_ai_service.py
import requests

AI_URL = "http://localhost:7000"

def test_health():
    print("=== Test /health ===")
    try:
        resp = requests.get(f"{AI_URL}/health", timeout=5)
        print("Status:", resp.status_code)
        print("Response:", resp.json())
    except Exception as e:
        print("Error:", e)

def test_classify():
    print("\n=== Test /classify ===")
    payload = {
        "id": "1",
        "text": "The product arrived broken and shipping was late",
        "candidate_labels": [
            "shipping delays",
            "product quality issues",
            "customer support",
            "packaging problems",
            "others"
        ]
    }
    try:
        resp = requests.post(f"{AI_URL}/classify", json=payload, timeout=15)
        print("Status:", resp.status_code)
        print("Raw response:", resp.text)
        if resp.headers.get("Content-Type", "").startswith("application/json"):
            print("Parsed JSON:", resp.json())
        else:
            print("Không nhận được JSON hợp lệ từ AI service.")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_health()
    test_classify()
