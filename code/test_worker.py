import requests

WORKER_URL = "http://localhost:6001"  # đổi nếu worker chạy port khác

def test_worker_ai():
    print("=== Test worker ↔ AI ===")
    batch = [
        {
            "id": "test-001",
            "star": 2,
            "text": "The product arrived broken and shipping was late"
        },
        {
            "id": "test-002",
            "star": 4,
            "text": "Customer support was helpful but packaging was damaged"
        }
    ]
    try:
        resp = requests.post(f"{WORKER_URL}/assign", json={"batch": batch}, timeout=20)
        print("Status:", resp.status_code)
        print("Raw response:", resp.text)
        if resp.headers.get("Content-Type", "").startswith("application/json"):
            print("Parsed JSON:", resp.json())
        else:
            print("Không nhận được JSON hợp lệ từ worker.")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_worker_ai()
