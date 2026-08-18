# Azure Student Copilot

A full-stack, cloud-ready AI tutoring web application built with Python (Flask) and deployed on Azure App Service. It features Socratic chat guidance, 3D interactive flashcards, practice quizzes, and lecture note synthesis with intelligent local fallback simulation.

---

## Features
- **Socratic AI Tutor:** Conversational guidance with multi-persona support (Socratic, Debugger, Exam Prep, Simplifier).
- **Study Deck Generator:** Interactive 3D flip flashcards for key technical concepts.
- **Practice Quiz Center:** Instant grading with rationale breakdown.
- **Note Synthesizer:** Converts raw lecture text into structured markdown study notes.
- **Cloud Resilient:** Operates seamlessly via Azure OpenAI / OpenAI, with an automated fallback engine when cloud credentials are not provisioned.

---

## Architecture & Tech Stack
- **Backend:** Python 3.11+, Flask, Gunicorn, python-dotenv
- **AI Integration:** Azure OpenAI Service / OpenAI API
- **Frontend:** HTML5, Modern CSS3, JavaScript (Fetch API)
- **Deployment:** Azure App Service via GitHub Actions CI/CD

---

## API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the main Student Copilot dashboard |
| `GET` | `/api/health` | Health probe for Azure App Service |
| `POST` | `/api/chat` | Handles conversational AI turns |
| `POST` | `/api/study/flashcards` | Generates study flashcards |
| `POST` | `/api/study/quiz` | Generates multiple-choice quizzes |
| `POST` | `/api/study/summarize` | Synthesizes lecture notes |