from flask import Flask, request, jsonify
from ai_service_pkg.model_loader import load_zero_shot
from ai_service_pkg.classifier import classify
import config

app = Flask(__name__)
ZS = load_zero_shot()  # load mô hình zero-shot classification

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True})

@app.route("/classify", methods=["POST"])
def classify_endpoint():
    data = request.get_json(force=True)
    text = data.get("text")
    if not text:
        return jsonify({"error": "Missing 'text' field"}), 400

    candidate_labels = data.get("candidate_labels", config.CAUSES)
    out = classify(ZS, text, candidate_labels)
    return jsonify({"id": data.get("id"), **out})

if __name__ == "__main__":
    app.run(port=7000)
