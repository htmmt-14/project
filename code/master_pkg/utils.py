# master_pkg/utils.py
import os
import datetime

def ensure_dir(path: str):
    """Tạo thư mục nếu chưa tồn tại"""
    if not os.path.exists(path):
        os.makedirs(path)

def timestamp() -> str:
    """Trả về timestamp hiện tại dạng YYYYMMDD_HHMMSS"""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def safe_filename(name: str) -> str:
    """Chuyển tên bất kỳ thành tên file an toàn"""
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in name)

def log(msg: str):
    """In log với timestamp"""
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")
