import math, requests, config

def split_even(items, n):
    # chênh lệch ≤ 1
    size = math.ceil(len(items)/n)
    return [items[i*size:(i+1)*size] for i in range(n)]

def send_assignments(batches):
    for worker, batch in zip(config.WORKERS, batches):
        requests.post(worker["url"] + "/assign", json={"batch": batch}, timeout=5)

def ping_workers():
    """Ping tất cả worker trong config.WORKERS để kiểm tra tình trạng"""
    alive = []
    for i, url in enumerate(config.WORKERS):
        try:
            resp = requests.get(f"{url}/health", timeout=5)
            if resp.status_code == 200 and resp.json().get("ok"):
                print(f"[dispatcher] Worker-{i+1} at {url} is alive")
                alive.append(url)
            else:
                print(f"[dispatcher] Worker-{i+1} at {url} responded but not healthy")
        except Exception as e:
            print(f"[dispatcher] Worker-{i+1} at {url} not reachable: {e}")
    return alive
