# config.py
MASTER_PORT = 7001
WORKERS = [
    {"name": "worker-1", "url": "http://localhost:6001"},
    {"name": "worker-2", "url": "http://localhost:6002"},
    {"name": "worker-3", "url": "http://localhost:6003"},
]
AI_SERVICE_URL = "http://localhost:7000"

RETRY = {
    "max_attempts": 5,
    "base_delay_sec": 0.5,
    "max_delay_sec": 4.0,
    "timeout_sec": 5.0
}

CAUSES = [
    "product quality & defects",
    "pricing & costs",
    "shipping & packaging",
    "customer support",
    "refund, return & warranty",
    "shopping experience"
]

MAX_SENTENCE_LEN = 512          # token-aware cắt câu nếu cần
ASSIGNMENT_MODE = "by_line"     # or "by_sentence"
REPORT_OUT_DIR = "reports"      # CSV + PNG

USE_SPACY = False           # True nếu muốn dùng spaCy cho tách câu
SPACY_MODEL = "en_core_web_sm"

# Ngưỡng mặc định và ngưỡng theo từng nguyên nhân (override)
DEFAULT_THRESHOLD = 0.5
LABEL_THRESHOLDS = {
    "product quality & defects" : 0.35,
    "pricing & costs" : 0.4,
    "shipping & packaging" : 0.6,
    "customer support" : 0.5,
    "refund, return & warranty" : 0.6,
    "shopping experience" : 0.45
    # thêm nếu cần; nếu không có trong dict, dùng DEFAULT_THRESHOLD
}