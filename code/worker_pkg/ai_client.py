# worker_pkg/ai_client.py
import time
import requests
import config

def post_with_retry(url, json):
    """
    Gửi POST request với retry và timeout.
    Nếu lỗi, log ra và thử lại theo chiến lược exponential backoff.
    """
    delay = config.RETRY["base_delay_sec"]
    for attempt in range(config.RETRY["max_attempts"]):
        try:
            print(f"[post] Attempt {attempt+1} to {url} with payload={json}")
            resp = requests.post(url, json=json, timeout=config.RETRY["timeout_sec"])
            resp.raise_for_status()
            # Nếu server trả về JSON hợp lệ
            return resp.json()
        except Exception as e:
            print(f"[post] Error on attempt {attempt+1}: {e}")
            if attempt == config.RETRY["max_attempts"] - 1:
                # Trả về rỗng thay vì treo vô hạn
                return {"labels": []}
            time.sleep(min(delay, config.RETRY["max_delay_sec"]))
            delay *= 2