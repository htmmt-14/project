from flask import Flask, request, jsonify
import requests
import config
# Đã import explode_by_sentences để hỗ trợ chế độ 'by_sentence'
from master_pkg.parser import parse_file, explode_by_sentences 
from master_pkg.utils import log, ensure_dir
from master_pkg.aggregator import Aggregator
from master_pkg.report import write_csv, write_bar_chart

app = Flask(__name__)
# Các biến toàn cục được khởi tạo
AGG = Aggregator()
TOTAL_IDS = set()

def split_even(items, n):
    """Chia đều items cho n worker, lệch không quá 1 đơn vị"""
    batches = [[] for _ in range(n)]
    for i, item in enumerate(items):
        batches[i % n].append(item)
    return batches

def ping_workers():
    """Ping từng worker để kiểm tra tình trạng"""
    alive = []
    for worker in config.WORKERS:
        url = worker["url"]
        name = worker["name"]
        try:
            resp = requests.get(f"{url}/health", timeout=5)
            log(f"Ping {name} → {resp.status_code} {resp.text}")
            if resp.status_code == 200 and resp.json().get("ok"):
                alive.append(worker)
        except Exception as e:
            log(f"{name} unreachable: {e}")
    return alive

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

@app.route("/start", methods=["POST"])
def start():
    try:
        data = request.get_json(force=True)
        items = parse_file(data["file_path"])
        
        for item in items:
            AGG.add_id_star(item["id"], item["star"])

        # FIX: Kích hoạt logic tách câu nếu ASSIGNMENT_MODE là "by_sentence"
        if config.ASSIGNMENT_MODE == "by_sentence": 
            log("Assignment mode is 'by_sentence', exploding comments...")
            items = explode_by_sentences(items) 
        
        if not items:
            log("No items to process after parsing/exploding.")
            return jsonify({"assigned": 0})

        # TOTAL_IDS là tập hợp ID gốc để theo dõi tiến độ
        global TOTAL_IDS
        # Vẫn lấy set của id, bất kể đã explode hay chưa (vì explode giữ id gốc)
        TOTAL_IDS = set([it["id"] for it in items]) 

        alive_workers = ping_workers()
        if not alive_workers:
            log("No workers alive. Cannot start assignment.")
            return jsonify({"error": "No workers alive"}), 500

        batches = split_even(items, len(alive_workers))
        
        log(f"Starting assignment of {len(items)} units to {len(alive_workers)} workers.")

        for i, batch in enumerate(batches):
            if not batch:
                continue
            url = alive_workers[i]["url"]
            name = alive_workers[i]["name"]
            try:
                # Tăng timeout cho worker
                resp = requests.post(f"{url}/assign", json={"batch": batch}, timeout=60) 
                log(f"Sent {len(batch)} items to {name}, status={resp.status_code}")
            except Exception as e:
                log(f"Error sending to {name}: {e}")

        return jsonify({"assigned": sum(len(b) for b in batches)})
    except Exception as e:
        log(f"Error in /start: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/result", methods=["POST"])
def result():
    try:
        # FIX: Khai báo global ở đầu hàm để có thể gán lại giá trị cho biến
        global AGG, TOTAL_IDS 
        
        payload = request.get_json(force=True)
        worker_name = payload.get("from_worker", "unknown")
        
        AGG.add_worker_result(payload["data"])
        
        current_processed_ids = set(AGG.per_id.keys())
        # Kiểm tra xem tất cả ID gốc đã được xử lý xong chưa
        done = current_processed_ids.issuperset(TOTAL_IDS) 

        log(f"Received results from {worker_name}. Processed: {len(current_processed_ids)}/{len(TOTAL_IDS)} unique IDs.")

        if done and TOTAL_IDS: # Đảm bảo có ID để xử lý
            log("All IDs processed. Generating report.")
            ensure_dir(config.REPORT_OUT_DIR)
            
            csv_path = write_csv(AGG.per_id, config.REPORT_OUT_DIR)
            top5 = AGG.top_causes(5)
            top5_for_chart = top5  # (cause, count, avg_star)
            top5_for_response = [(cause, count) for cause, count, _ in top5]  # (cause, count)
            chart_path = write_bar_chart(top5, config.REPORT_OUT_DIR)
            
            # FIX: Reset Aggregator và TOTAL_IDS sau khi hoàn thành
            AGG = Aggregator()
            TOTAL_IDS = set()

            return jsonify({
                "done": True,
                "csv": csv_path,
                "chart": chart_path,
                "top5": top5,
                "total_processed": len(current_processed_ids)
            })
        
        return jsonify({"done": False, "processed": len(current_processed_ids)})
    except Exception as e:
        log(f"Error in /result: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=config.MASTER_PORT)