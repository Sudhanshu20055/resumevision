"""
app.py
Flask backend for the AI Resume Analyzer (powered by Google Gemini API).

Endpoints:
  GET  /                -> serves the frontend
  POST /api/analyze     -> accepts a resume file (+ optional job description),
                            returns structured ATS/skill/interview analysis
  GET  /api/health      -> simple health check
"""
import os
import tempfile
import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from utils.gemini_analyzer import GeminiAnalysisError, analyze_resume
from utils.resume_parser import ResumeParseError, extract_text

load_dotenv()

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return jsonify({"error": "No resume file was uploaded."}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not _allowed_file(file.filename):
        return jsonify({
            "error": f"Unsupported file type. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
        }), 400

    job_description = request.form.get("job_description", "").strip()

    safe_name = secure_filename(file.filename)
    ext = safe_name.rsplit(".", 1)[1].lower()
    tmp_path = os.path.join(tempfile.gettempdir(), f"resume_{uuid.uuid4().hex}.{ext}")

    try:
        file.save(tmp_path)

        try:
            resume_text = extract_text(tmp_path)
        except ResumeParseError as exc:
            return jsonify({"error": str(exc)}), 422

        try:
            result = analyze_resume(resume_text, job_description or None)
        except GeminiAnalysisError as exc:
            return jsonify({"error": str(exc)}), 502

        return jsonify({"result": result})

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.errorhandler(413)
def too_large(_e):
    return jsonify({"error": "File is too large. Max size is 8 MB."}), 413


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
