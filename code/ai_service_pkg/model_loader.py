from transformers import pipeline

def load_zero_shot():
    """
    Load mô hình zero-shot classification từ Hugging Face.
    Mặc định chạy trên CPU (device=-1). Nếu có GPU, set device=0.
    """
    print("Loading zero-shot classification model (facebook/bart-large-mnli)...")
    return pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=0  # -1:CPU; set to 0 for GPU
    )
