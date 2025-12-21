# worker_pkg/summarizer.py
import re

def simple_summarize(text: str, max_sentences: int = 2) -> str:
    """
    Tóm tắt đơn giản bằng cách lấy vài câu đầu tiên.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return " ".join(sentences[:max_sentences])

def keyword_summarize(text: str, keywords: list) -> str:
    """
    Tóm tắt bằng cách giữ lại câu có chứa từ khóa.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    selected = [s for s in sentences if any(k.lower() in s.lower() for k in keywords)]
    if not selected:
        return sentences[0] if sentences else ""
    return " ".join(selected)

def summarize(text: str, mode: str = "simple", **kwargs) -> str:
    """
    Chọn cách tóm tắt theo mode.
    - simple: lấy vài câu đầu
    - keyword: lọc theo từ khóa
    """
    if mode == "keyword":
        return keyword_summarize(text, kwargs.get("keywords", []))
    return simple_summarize(text, kwargs.get("max_sentences", 2))
