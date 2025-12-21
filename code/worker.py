from flask import Flask, request, jsonify
import argparse
import config
# Đã loại bỏ import từ worker_pkg.summarizer
from worker_pkg.ai_client import post_with_retry # Sử dụng hàm POST ổn định hơn

app = Flask(__name__)
PORT = None  # sẽ gán khi chạy

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

@app.route("/assign", methods=["POST"])
def assign():
    data = request.get_json(force=True)
    batch = data.get("batch", [])
    
    # Sử dụng logic process_batch_and_aggregate để gộp nhãn theo ID gốc
    results_payload = process_batch_and_aggregate(batch)

    try:
        # Sử dụng post_with_retry để gửi kết quả về Master
        post_with_retry(
            f"http://localhost:{config.MASTER_PORT}/result",
            {"from_worker": f"worker-{PORT}", "data": results_payload}
        )
        print(f"[worker-{PORT}] Sent {len(results_payload)} aggregated results to master")
    except Exception as e:
        print(f"[worker-{PORT}] Error sending results: {e}")

    return jsonify({"ok": True, "processed": len(batch)})

def process_batch_and_aggregate(items):
    """
    Xử lý batch, gọi AI service, và gộp nhãn theo id gốc (union set).
    """
    print(f"[worker-{PORT}] Received batch with {len(items)} items")
    aggregated = {} # Dùng để gộp nhãn theo ID gốc: {"id": set()}

    for item in items:
        # FIX: Dùng item["text"] trực tiếp (không tóm tắt) để tránh cắt xén dữ liệu đã được Master chuẩn bị.
        text_to_send = item["text"]
        
        # Dùng sid nếu tồn tại (cho chế độ by_sentence), nếu không dùng id
        call_id = item.get("sid", item["id"]) 

        print(f"[worker-{PORT}] Calling AI for id={item['id']} (call_id={call_id})")
        
        try:
            # Gửi text và config.CAUSES
            res = post_with_retry(
                config.AI_SERVICE_URL + "/classify",
                {"id": call_id, "text": text_to_send, "candidate_labels": config.CAUSES}
            )
            labels = res.get("labels", [])
            print(f"[worker-{PORT}] AI response for {item['id']}: {labels}")
        except Exception as e:
            print(f"[worker-{PORT}] Error calling AI for {item['id']}: {e}")
            labels = []

        # Gộp nhãn vào set theo ID gốc
        agg = aggregated.setdefault(item["id"], set())
        for l in labels:
            agg.add(l)

    # Chuyển aggregated results thành payload: [{"id": k, "labels": [...]}, ...]
    payload = [{"id": k, "labels": sorted(list(v))} for k, v in aggregated.items()]
    return payload

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    args = parser.parse_args()
    PORT = args.port
    app.run(port=PORT)