# test_existing_input.py
import requests
import json
import time
import os
import config
import csv
from collections import Counter, defaultdict
import statistics
import re

# Định nghĩa các hằng số
MASTER_URL = f"http://localhost:{config.MASTER_PORT}"
START_URL = f"{MASTER_URL}/start"
INPUT_FILE = "input.txt"  # SỬ DỤNG FILE INPUT ĐÃ CÓ SẴN

def check_input_file():
    """Kiểm tra file input đã tồn tại chưa."""
    print(f"--- 1. KIỂM TRA FILE ĐẦU VÀO: {INPUT_FILE} ---")
    if os.path.exists(INPUT_FILE):
        print(f"✓ Tìm thấy file input: {INPUT_FILE}")
        
        # Đếm số dòng trong file
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        print(f"✓ Số lượng bình luận: {len(lines)}")
        return True
    else:
        print(f"✗ KHÔNG tìm thấy file input: {INPUT_FILE}")
        print("Vui lòng đảm bảo file input.txt tồn tại trong thư mục hiện tại.")
        return False

def start_analysis():
    """Gửi request /start đến Master để bắt đầu quy trình."""
    print("\n--- 2. GỬI LỆNH BẮT ĐẦU PHÂN TÍCH (/start) ---")
    payload = {"file_path": INPUT_FILE}
    
    try:
        response = requests.post(START_URL, json=payload, timeout=1000)
        
        if response.status_code == 200:
            data = response.json()
            assigned_count = data.get("assigned", 0)
            print(f"✓ Master chấp nhận. Đã phân phối {assigned_count} đơn vị công việc.")
            return True
        else:
            print(f"✗ LỖI Master trả về: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"✗ LỖI: Không kết nối được Master tại {MASTER_URL}. Đảm bảo master.py đang chạy.")
        return False
    except Exception as e:
        print(f"✗ LỖI không xác định khi khởi động: {e}")
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
            print(f"\n✓ THÀNH CÔNG: Master đã tạo báo cáo đầy đủ.")
            print(f"  - CSV: {csv_path}")
            print(f"  - Biểu đồ: {chart_path}")
            return True
        
        # Kiểm tra từng file
        if os.path.exists(csv_path) and not files_created:
            print(f"✓ Đã tạo file CSV: {csv_path}")
            files_created = True
        
        if os.path.exists(chart_path) and not files_created:
            print(f"✓ Đã tạo file biểu đồ: {chart_path}")
            files_created = True
        
        if not files_created:
            print("... Đang chờ Worker xử lý và Master tổng hợp...")
            time.sleep(5)
        else:
            # Nếu đã có ít nhất một file, tiếp tục chờ file còn lại
            time.sleep(2)
    
    print("\n✗ HẾT GIỜ: Master không hoàn thành báo cáo trong thời gian quy định.")
    
    # Kiểm tra xem có file nào đã được tạo không
    if os.path.exists(csv_path) or os.path.exists(chart_path):
        print("Các file đã được tạo:")
        if os.path.exists(csv_path):
            print(f"  - CSV: {csv_path}")
        if os.path.exists(chart_path):
            print(f"  - Biểu đồ: {chart_path}")
        return True
    
    return False

def parse_input_file_for_stars():
    """Parse file input để lấy thông tin star cho mỗi id."""
    LINE_RE = re.compile(r"^\s*(\d+)\.\s*\((\d)\)\s*(.+)$")
    id_to_star = {}
    
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                m = LINE_RE.match(line)
                if not m:
                    # Thử parse format khác nếu cần
                    print(f"⚠ Cảnh báo: Không thể parse dòng: {line}")
                    continue
                id_, star, _ = m.group(1), int(m.group(2)), m.group(3)
                id_to_star[id_] = star
    except Exception as e:
        print(f"✗ Lỗi khi đọc file input để lấy thông tin số sao: {e}")
    
    print(f"✓ Đã đọc thông tin số sao cho {len(id_to_star)} bình luận")
    return id_to_star

def compute_top_causes_with_stars():
    """Tính toán top causes với số sao trung bình từ file CSV và input."""
    csv_path = os.path.join(config.REPORT_OUT_DIR, "report.csv")
    
    if not os.path.exists(csv_path):
        print("✗ Không tìm thấy file CSV để tính toán.")
        return []
    
    # Đọc file CSV
    id_to_labels = {}
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                id_ = row['id']
                labels = row['labels'].split(';') if row['labels'] else []
                id_to_labels[id_] = labels
    except Exception as e:
        print(f"✗ Lỗi khi đọc file CSV: {e}")
        return []
    
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
    print("\n" + "=" * 70)
    print("KẾT QUẢ CUỐI CÙNG")
    print("=" * 70)
    
    report_dir = config.REPORT_OUT_DIR
    csv_path = os.path.join(report_dir, "report.csv")
    chart_path = os.path.join(report_dir, "top5_with_stars.png")

    # Hiển thị file CSV
    if os.path.exists(csv_path):
        print(f"\n📄 File Báo cáo CSV ({csv_path}):")
        print("-" * 60)
        with open(csv_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i == 0:
                    print(f"📋 HEADER: {line.strip()}")
                else:
                    print(f"📝 ROW {i}: {line.strip()}")
        print("-" * 60)
    else:
        print(f"\n✗ Không tìm thấy file CSV: {csv_path}")
    
    # Hiển thị thông tin top causes với số sao trung bình
    top_causes = compute_top_causes_with_stars()
    
    if top_causes:
        print(f"\n🏆 TOP 5 NGUYÊN NHÂN VỚI SỐ SAO TRUNG BÌNH:")
        print("=" * 60)
        print(f"{'Nguyên nhân':<25} {'Tần suất':<10} {'Sao TB':<10}")
        print("-" * 60)
        for cause, count, avg_star in top_causes:
            print(f"{cause:<25} {count:<10} {avg_star:<10.2f}")
        print("=" * 60)
        
        # In giải thích
        print("\n📊 GIẢI THÍCH:")
        print("• Tần suất: Số lần nguyên nhân xuất hiện trong các bình luận")
        print("• Sao TB: Số sao trung bình của các bình luận có nguyên nhân này")
        print("  (1-5 sao, càng thấp càng tiêu cực)")
    else:
        print("\n⚠ Không thể tính toán top causes.")
    
    # Hiển thị thông tin biểu đồ
    if os.path.exists(chart_path):
        print(f"\n✅ Biểu đồ Top 5 nguyên nhân (với số sao trung bình) đã được tạo:")
        print(f"   📈 {chart_path}")
        
        # Hiển thị mô tả biểu đồ
        print("\n📐 BIỂU ĐỒ BAO GỒM:")
        print("• Cột màu XANH: Tần suất xuất hiện của nguyên nhân")
        print("• Cột màu CAM: Số sao trung bình (1-5)")
        print("• Số trên đỉnh cột: Giá trị tương ứng")
    else:
        print(f"\n✗ Không tìm thấy file biểu đồ mới: {chart_path}")
        
        # Kiểm tra file cũ
        old_chart_path = os.path.join(report_dir, "top5_bar.png")
        if os.path.exists(old_chart_path):
            print(f"  ⚠ Tìm thấy biểu đồ cũ tại: {old_chart_path}")

def preview_input_file():
    """Xem trước nội dung file input."""
    print("\n📋 XEM TRƯỚC FILE INPUT:")
    print("-" * 60)
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            print(content)
    except Exception as e:
        print(f"✗ Lỗi khi đọc file input: {e}")
    print("-" * 60)

if __name__ == "__main__":
    print("=" * 70)
    print("TEST HỆ THỐNG VỚI FILE INPUT ĐÃ CÓ SẴN")
    print("=" * 70)
    
    # Xem trước file input
    preview_input_file()
    
    # Kiểm tra file input
    if not check_input_file():
        print("\n✗ Không thể tiếp tục vì thiếu file input.")
        exit(1)
    
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
    
    print("\n" + "=" * 70)
    print("QUÁ TRÌNH CHẠY THỬ HOÀN TẤT")
    print("=" * 70)