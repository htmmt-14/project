import re
import config
# Đã import spacy để đảm bảo có sẵn cho hàm _get_spacy
import spacy 

# Regex để bắt dòng: id. (star) content
LINE_RE = re.compile(r"^\s*(\d+)\.\s*\((\d)\)\s*(.+)$")

def parse_file(path: str):
    items = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                m = LINE_RE.match(line.strip())
                if not m:
                    continue
                id_, star, text = m.group(1), int(m.group(2)), m.group(3)
                if 1 <= star <= 4:
                    items.append({"id": id_, "star": star, "text": text})
    except Exception as e:
        print(f"[parser] Error reading file: {e}")
    return items


# Regex tách câu đơn giản
SENTENCE_RE = re.compile(r'(?<=[\.\!\?])\s+')

def split_sentences_regex(text: str):
    """Tách câu bằng regex"""
    parts = [p.strip() for p in SENTENCE_RE.split(text) if p.strip()]
    return parts

# spaCy tách câu (nếu bật trong config)
_spacy_nlp = None

def _get_spacy():
    global _spacy_nlp
    if _spacy_nlp is None:
        _spacy_nlp = spacy.load(config.SPACY_MODEL)
    return _spacy_nlp

def split_sentences_spacy(text: str):
    """Tách câu bằng spaCy"""
    nlp = _get_spacy()
    doc = nlp(text)
    return [s.text.strip() for s in doc.sents if s.text.strip()]

def split_sentences(text: str):
    """Chọn cách tách câu theo config"""
    if config.USE_SPACY:
        return split_sentences_spacy(text)
    return split_sentences_regex(text)

def explode_by_sentences(items):
    """Tách comment thành nhiều câu, giữ id gốc để gộp lại"""
    exploded = []
    for it in items:
        sentences = split_sentences(it["text"])
        for idx, sent in enumerate(sentences):
            exploded.append({
                "id": it["id"],             # id gốc
                "sid": f'{it["id"]}_{idx}', # sub-id cho tracking nội bộ
                "star": it["star"],
                "text": sent
            })
    return exploded