from flask import Flask, request, jsonify

app = Flask(__name__)

@app.post("/sort")
def sort_chars():
    payload = request.get_json(silent=True) or {}
    data = payload.get("data")

    if not isinstance(data, str):
        return jsonify({"error": '"data" must be a string'}), 400

    chars = sorted(list(data))
    return jsonify({"word": chars}), 200

@app.get("/health")
def health():
    return "ok", 200
