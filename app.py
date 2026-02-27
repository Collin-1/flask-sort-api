from flask import Flask, request, jsonify, render_template
import urllib.parse
import requests

app = Flask(__name__)

# --- BONUS UI ---
@app.get("/")
def home():
    return render_template("index.html")

# --- REQUIRED TASK ENDPOINT ---
@app.post("/sort")
def sort_chars():
    payload = request.get_json(silent=True) or {}
    data = payload.get("data")

    if not isinstance(data, str):
        return jsonify({"error": '"data" must be a string'}), 400

    # optional safety limit
    if len(data) > 10000:
        return jsonify({"error": '"data" too long'}), 413

    return jsonify({"word": sorted(list(data))}), 200

@app.get("/health")
def health():
    return "ok", 200

# --- BONUS: server-side call to the validator (avoids CORS) ---
@app.get("/validate")
def validate():
    email = request.args.get("email", "").strip()
    url = request.args.get("url", "").strip()

    if not email or not url:
        return jsonify({"error": "Missing email or url"}), 400

    validator_base = "https://yhxzjyykdsfkdrmdxgho.supabase.co/functions/v1/application-task"
    qs = urllib.parse.urlencode({"url": url, "email": email})
    validator_url = f"{validator_base}?{qs}"

    try:
        r = requests.get(validator_url, timeout=20)
        # return exactly what the validator returns
        return (r.text, r.status_code, {"Content-Type": r.headers.get("Content-Type", "application/json")})
    except requests.RequestException as e:
        return jsonify({"error": f"Validator request failed: {str(e)}"}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)