import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import ai_service

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-12345")

# Socratic Persona Modes
SYSTEM_MODES = {
    "socratic": "You are a Socratic tutor. Never give direct answers immediately; guide the student step-by-step with targeted questions.",
    "debugger": "You are a senior code reviewer and debugger. Help students spot syntax and logic bugs, explaining edge cases clearly.",
    "exam_prep": "You are an exam preparation tutor. Emphasize recall, clear definitions, and common test pitfalls.",
    "simplifier": "You explain complex computational and architectural concepts in simple, intuitive analogies (Feynman Technique)."
}

# -------------------------------------------------------------
# Web & Health Check Routes
# -------------------------------------------------------------

@app.route("/")
def home():
    """Serves the main interactive Student Copilot dashboard."""
    return render_template("index.html")
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint used by Azure App Service to verify the app is alive."""
    engine_type, _, _ = ai_service.get_ai_client()
    return jsonify({
        "status": "healthy",
        "service": "Azure Student Copilot",
        "ai_engine": engine_type
    }), 200

# -------------------------------------------------------------
# AI API Endpoints
# -------------------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def chat():
    """Handles Socratic chat conversation turns."""
    data = request.get_json() or {}
    messages = data.get("messages", [])
    mode = data.get("mode", "socratic")
    
    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    system_prompt = SYSTEM_MODES.get(mode, SYSTEM_MODES["socratic"])
    reply = ai_service.chat_completion(messages, system_prompt=system_prompt)
    
    return jsonify({
        "reply": reply,
        "mode": mode
    })

@app.route("/api/study/flashcards", methods=["POST"])
def flashcards():
    """Generates study flashcards from a topic or text."""
    data = request.get_json() or {}
    topic = data.get("topic", "Cloud Architecture")
    text = data.get("text", "")
    
    cards = ai_service.generate_flashcards(topic, text)
    return jsonify({
        "topic": topic,
        "cards": cards
    })

@app.route("/api/study/quiz", methods=["POST"])
def quiz():
    """Generates an interactive practice quiz."""
    data = request.get_json() or {}
    topic = data.get("topic", "Cloud Fundamentals")
    
    questions = ai_service.generate_quiz(topic)
    return jsonify({
        "topic": topic,
        "questions": questions
    })

@app.route("/api/study/summarize", methods=["POST"])
def summarize():
    """Generates structured notes from raw lecture text."""
    data = request.get_json() or {}
    content = data.get("content", "")
    
    if not content:
        return jsonify({"error": "Content required for summarization"}), 400
    
    summary = ai_service.chat_completion(
        messages=[{"role": "user", "content": f"Summarize the following lecture content into key concepts and takeaways:\n\n{content}"}],
        system_prompt="You are an academic summarizer. Provide concise bullet points, key definitions, and practical takeaways."
    )
    return jsonify({"summary": summary})

# -------------------------------------------------------------
# Local Development Runner
# -------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)