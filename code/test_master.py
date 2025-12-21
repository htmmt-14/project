# test_master_new.py
import requests
import json
import time
import os
import config
import csv
from collections import Counter, defaultdict
import statistics

# Định nghĩa các hằng số
MASTER_URL = f"http://localhost:{config.MASTER_PORT}"
START_URL = f"{MASTER_URL}/start"
INPUT_FILE = "input.en.txt"  # SỬ DỤNG FILE TIẾNG ANH

def create_input_file():
    """Tạo file đầu vào input.en.txt với các bình luận tiếng Anh."""
    print(f"--- 1. TẠO FILE ĐẦU VÀO: {INPUT_FILE} (English) ---")
    content = """
1. (4) The product shipping was very slow. The quality of the product was not as described.
2. (1) I contacted support many times but no one answered. The customer service is terrible.
3. (3) The computer's battery has a technical defect. I want to exchange or return it immediately.
4. (5) This is a wonderful product, 5 stars.
5. (2) The packaging was sloppy; the box was dented upon arrival. The device inside was luckily not damaged.
6. (1) Despite the high price, the product still has many small quality issues.
7. (3) I received no response regarding my exchange request.
8. (2) The shipping fee is too expensive and the delivery time is very long.
9. (1) I don't like this shit, too bad for $50
"""
    with open(INPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)
    print("Đã tạo file đầu vào tiếng Anh thành công.")

def start_analysis():
    """Gửi request /start đến Master để bắt đầu quy trình."""
    print("\n--- 2. GỬI LỆNH BẮT ĐẦU PHÂN TÍCH (/start) ---")
    payload = {"file_path": INPUT_FILE}
    
    try:
        response = requests.post(START_URL, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            assigned_count = data.get("assigned", 0)
            print(f"Master chấp nhận. Đã phân phối {assigned_count} đơn vị công việc.")
            return True
        else:
            print(f"LỖI Master trả về: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"LỖI: Không kết nối được Master tại {MASTER_URL}. Đảm bảo master.py đang chạy.")
        return False
    except Exception as e:
        print(f"LỖI không xác định khi khởi động: {e}")
        return False

def wait_for_completion(max_wait_time=300):
    """
    Chờ Worker xử lý và Master tạo báo cáo bằng cách kiểm tra file báo cáo.
    """
    print("\n--- 3. CHỜ XỬ LÝ VÀ BÁO CÁO ---")
    
    # Kiểm tra cả file CSV và file biểu đồ mới
    csv_path = os.path.join(config.REPORT_OUT_DIR, "report.csv")
    chart_path = os.path.join(config.REPORT_OUT_DIR, "top5_with_stars.png")
    
    start_time = time.time()
    files_created = False
    
    while time.time() - start_time < max_wait_time:
        if os.path.exists(csv_path) and os.path.exists(chart_path):
            print(f"\n[THÀNH CÔNG] Master đã tạo báo cáo đầy đủ.")
            print(f"  - CSV: {csv_path}")
            print(f"  - Biểu đồ: {chart_path}")
            return True
        
        # Kiểm tra từng file
        if os.path.exists(csv_path) and not files_created:
            print(f"Đã tạo file CSV: {csv_path}")
            files_created = True
        
        if os.path.exists(chart_path) and not files_created:
            print(f"Đã tạo file biểu đồ: {chart_path}")
            files_created = True
        
        if not files_created:
            print("... Đang chờ Worker xử lý và Master tổng hợp...")
            time.sleep(5)
        
    print("\n[HẾT GIỜ] Master không hoàn thành báo cáo trong thời gian quy định.")
    return False

def parse_input_file_for_stars():
    """Parse file input để lấy thông tin star cho mỗi id."""
    import re
    LINE_RE = re.compile(r"^\s*(\d+)\.\s*\((\d)\)\s*(.+)$")
    id_to_star = {}
    
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                m = LINE_RE.match(line.strip())
                if not m:
                    continue
                id_, star, _ = m.group(1), int(m.group(2)), m.group(3)
                id_to_star[id_] = star
    except Exception as e:
        print(f"Error reading input file for stars: {e}")
    
    return id_to_star

def compute_top_causes_with_stars():
    """Tính toán top causes với số sao trung bình từ file CSV và input."""
    csv_path = os.path.join(config.REPORT_OUT_DIR, "report.csv")
    
    if not os.path.exists(csv_path):
        print("Không tìm thấy file CSV để tính toán.")
        return []
    
    # Đọc file CSV
    id_to_labels = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            id_ = row['id']
            labels = row['labels'].split(';') if row['labels'] else []
            id_to_labels[id_] = labels
    
    # Lấy thông tin star từ file input
    id_to_star = parse_input_file_for_stars()
    
    # Tính toán
    counter = Counter()
    label_stars = defaultdict(list)
    
    for id_, labels in id_to_labels.items():
        star = id_to_star.get(id_)
        if star is None:
            continue
            
        for label in labels:
            counter.update([label])
            label_stars[label].append(star)
    
    # Lấy top 5 và tính trung bình
    result = []
    for label, count in counter.most_common(5):
        stars = label_stars[label]
        avg_star = statistics.mean(stars) if stars else 0
        result.append((label, count, round(avg_star, 2)))
    
    return result

def print_final_report():
    """In ra kết quả báo cáo cuối cùng với thông tin số sao trung bình."""
    print("\n--- 4. KẾT QUẢ CUỐI CÙNG ---")
    report_dir = config.REPORT_OUT_DIR
    csv_path = os.path.join(report_dir, "report.csv")
    chart_path = os.path.join(report_dir, "top5_with_stars.png")

    # Hiển thị file CSV
    if os.path.exists(csv_path):
        print(f"\nFile Báo cáo CSV ({csv_path}):")
        print("=" * 60)
        with open(csv_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i == 0:
                    print(f"HEADER: {line.strip()}")
                else:
                    print(f"ROW {i}: {line.strip()}")
        print("=" * 60)
    
    # Hiển thị thông tin top causes với số sao trung bình
    top_causes = compute_top_causes_with_stars()
    
    if top_causes:
        print(f"\nTOP 5 NGUYÊN NHÂN VỚI SỐ SAO TRUNG BÌNH:")
        print("=" * 60)
        print(f"{'Nguyên nhân':<25} {'Tần suất':<10} {'Sao TB':<10}")
        print("-" * 60)
        for cause, count, avg_star in top_causes:
            print(f"{cause:<25} {count:<10} {avg_star:<10.2f}")
        print("=" * 60)
        
        # In giải thích
        print("\nGIẢI THÍCH:")
        print("• Tần suất: Số lần nguyên nhân xuất hiện trong các bình luận")
        print("• Sao TB: Số sao trung bình của các bình luận có nguyên nhân này")
        print("  (1-4 sao, càng thấp càng tiêu cực)")
    
    # Hiển thị thông tin biểu đồ
    if os.path.exists(chart_path):
        print(f"\n✓ Biểu đồ Top 5 nguyên nhân (với số sao trung bình) đã được tạo:")
        print(f"  {chart_path}")
        
        # Hiển thị mô tả biểu đồ
        print("\nBIỂU ĐỒ BAO GỒM:")
        print("• Cột màu XANH: Tần suất xuất hiện của nguyên nhân")
        print("• Cột màu CAM: Số sao trung bình (1-4)")
        print("• Số trên đỉnh cột: Giá trị tương ứng")
    else:
        print("\n✗ Không tìm thấy file biểu đồ mới.")
        # Kiểm tra file cũ
        old_chart_path = os.path.join(report_dir, "top5_bar.png")
        if os.path.exists(old_chart_path):
            print(f"  Tìm thấy biểu đồ cũ tại: {old_chart_path}")

def cleanup():
    """Dọn dẹp file tạm."""
    print("\n--- 5. DỌN DẸP ---")
    
    # Xóa file input
    if os.path.exists(INPUT_FILE):
        os.remove(INPUT_FILE)
        print(f"Đã xóa file input: {INPUT_FILE}")
    
    # Có thể xóa thư mục report nếu muốn
    # import shutil
    # if os.path.exists(config.REPORT_OUT_DIR):
    #     shutil.rmtree(config.REPORT_OUT_DIR)
    #     print(f"Đã xóa thư mục report: {config.REPORT_OUT_DIR}")

if __name__ == "__main__":
    print("=" * 70)
    print("TEST MASTER MỚI - VỚI TÍNH NĂNG SỐ SAO TRUNG BÌNH")
    print("=" * 70)
    
    # Tạo file input
    create_input_file()
    
    # Bắt đầu phân tích
    if start_analysis():
        # Chờ hoàn thành
        if wait_for_completion():
            # In báo cáo
            print_final_report()
        else:
            print("\n❌ Quá trình xử lý không hoàn thành đúng thời hạn.")
    else:
        print("\n❌ Không thể bắt đầu quá trình phân tích.")
    
    # Dọn dẹp (tùy chọn)
    cleanup_option = input("\nXóa file input đã tạo? (y/n): ").lower()
    if cleanup_option == 'y':
        cleanup()
    
    print("\n" + "=" * 70)
    print("QUÁ TRÌNH CHẠY THỬ HOÀN TẤT")
    print("=" * 70)