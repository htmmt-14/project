import config

def _get_threshold_for_label(label: str) -> float:
    """
    Lấy ngưỡng threshold cho từng label từ config.
    Nếu label không có trong dict LABEL_THRESHOLDS thì dùng DEFAULT_THRESHOLD.
    """
    return config.LABEL_THRESHOLDS.get(label, config.DEFAULT_THRESHOLD)

def classify(zero_shot, text: str, labels: list[str]) -> dict:
    """
    Chạy zero-shot classification trên text với danh sách labels.
    Trả về các labels được chọn (score >= threshold) và toàn bộ scores.
    """
    res = zero_shot(text, candidate_labels=labels, multi_label=True)
    scores_map = dict(zip(res["labels"], res["scores"]))
    accepted = []
    for lbl in res["labels"]:
        th = _get_threshold_for_label(lbl)
        if scores_map[lbl] >= th:
            accepted.append(lbl)
    return {"labels": accepted, "scores": scores_map}
