# worker_pkg/worker_core.py
import config
from worker_pkg.ai_client import post_with_retry

def process_batch(items):
    """
    Nhận batch comments, gọi AI service để phân loại,
    gộp nhãn theo id gốc, gửi kết quả về master.
    """
    print(f"[worker] Received batch with {len(items)} items")
    aggregated = {}

    for item in items:
        print(f"[worker] Processing id={item['id']} (star={item['star']})")
        text = item["text"]
        call_id = item.get("sid", item["id"])

        try:
            res = post_with_retry(
                config.AI_SERVICE_URL + "/classify",
                {"id": call_id, "text": text, "candidate_labels": config.CAUSES}
            )
            labels = res.get("labels", [])
            print(f"[worker] AI response for id={item['id']}: {labels}")
        except Exception as e:
            print(f"[worker] Error calling AI for id={item['id']}: {e}")
            labels = []

        agg = aggregated.setdefault(item["id"], set())
        for l in labels:
            agg.add(l)

    # gửi về master: union labels theo id
    payload = [{"id": k, "labels": sorted(list(v))} for k, v in aggregated.items()]
    print(f"[worker] Sending result to master with {len(payload)} items")

    try:
        post_with_retry(
            f"http://localhost:{config.MASTER_PORT}/result",
            {"from": "worker", "data": payload}
        )
        print("[worker] Result sent successfully to master")
    except Exception as e:
        print(f"[worker] Error sending result to master: {e}")

    return aggregated
