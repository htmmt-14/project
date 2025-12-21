import requests

url = "http://localhost:6001/assign"
payload = {
    "batch": [
        {"id": "test1", "star": 2, "text": "The product arrived broken"},
        {"id": "test2", "star": 3, "text": "Shipping was late"}
    ]
}

resp = requests.post(url, json=payload, timeout=10)
print("Status:", resp.status_code)
print("Response:", resp.text)
