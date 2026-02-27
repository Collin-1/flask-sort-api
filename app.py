from flask import Flask, request, jsonify, render_template
import urllib.parse
import requests
import threading
import uuid

app = Flask(__name__)
VALIDATION_JOBS = {}


def _run_validator_job(job_id, email, url):
    validator_base = "https://yhxzjyykdsfkdrmdxgho.supabase.co/functions/v1/application-task"
    try:
        r = requests.get(validator_base, params={"url": url, "email": email}, timeout=60)
        VALIDATION_JOBS[job_id] = {
            "status": "done",
            "http_status": r.status_code,
            "content_type": r.headers.get("Content-Type", "application/json"),
            "body": r.text,
        }
    except requests.Timeout:
        VALIDATION_JOBS[job_id] = {
            "status": "error",
            "error": "Validator request timed out",
        }
    except requests.RequestException as e:
        VALIDATION_JOBS[job_id] = {
            "status": "error",
            "error": f"Validator request failed: {str(e)}",
        }

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

# --- BONUS: async server-side call to validator so UI can display output reliably ---
@app.post("/validate/start")
def validate_start():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip()
    url = (payload.get("url") or "").strip()

    if not email or not url:
        return jsonify({"error": "Missing email or url"}), 400

    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return jsonify({"error": "url must start with http or https"}), 400

    job_id = str(uuid.uuid4())
    VALIDATION_JOBS[job_id] = {"status": "running"}

    worker = threading.Thread(target=_run_validator_job, args=(job_id, email, url), daemon=True)
    worker.start()

    return jsonify({"jobId": job_id}), 202


@app.get("/validate/result/<job_id>")
def validate_result(job_id):
    job = VALIDATION_JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Unknown job id"}), 404
    return jsonify(job), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)