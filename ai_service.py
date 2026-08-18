import os
import json
import logging
from dotenv import load_dotenv

# Load any variables defined in .env
load_dotenv()

logger = logging.getLogger(__name__)

# Read environment variables
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def get_ai_client():
    """
    Determines which AI engine to use based on available environment variables.
    Returns: (engine_type, client_instance, model_name)
    """
    if AZURE_ENDPOINT and AZURE_KEY:
        from openai import AzureOpenAI
        client = AzureOpenAI(
            azure_endpoint=AZURE_ENDPOINT,
            api_key=AZURE_KEY,
            api_version="2024-02-15-preview"
        )
        return "azure", client, AZURE_DEPLOYMENT
    elif OPENAI_KEY:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
        return "openai", client, OPENAI_MODEL
    else:
        # Fallback mode: No cloud keys needed to run and test!
        return "mock", None, None

def chat_completion(messages: list, system_prompt: str = None) -> str:
    """
    Generates a conversational response from the AI model (or mock fallback).
    """
    engine, client, model = get_ai_client()

    # If no keys configured, return simulated Socratic response
    if engine == "mock":
        user_text = messages[-1]["content"] if messages else ""
        return _mock_socratic_response(user_text)

    # Build conversation payload
    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=full_messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error calling AI engine: {e}")
        return f"[Fallback Engine] Unable to reach cloud AI service. Simulated response: {_mock_socratic_response(messages[-1]['content'])}"

def generate_flashcards(topic: str, text: str = "") -> list:
    """
    Returns a list of flashcards: [{'front': '...', 'back': '...'}, ...]
    """
    engine, client, model = get_ai_client()

    if engine == "mock":
        return [
            {
                "front": f"What is the primary role of {topic}?",
                "back": f"{topic} enables reliable, structured computation and efficient data processing in modern systems."
            },
            {
                "front": "What is horizontal scaling (scale-out)?",
                "back": "Adding more computing nodes/instances to distribute workload and increase fault tolerance."
            },
            {
                "front": "What is an API endpoint?",
                "back": "A specific URL where a web service receives client requests and returns structured responses."
            }
        ]

    prompt = (
        f"Generate 4 study flashcards for '{topic}'. Additional context: '{text}'.\n"
        "Return ONLY a JSON array of objects with 'front' and 'back' properties."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an academic flashcard generator that outputs ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        raw = response.choices[0].message.content.strip()
        data = json.loads(raw)
        return data.get("flashcards", data) if isinstance(data, dict) else data
    except Exception as e:
        logger.warning(f"Flashcard parsing error, using fallback: {e}")
        return [{"front": f"Overview of {topic}", "back": "Key study concept."}]

def generate_quiz(topic: str) -> list:
    """
    Returns a list of multiple-choice questions:
    [{'id': 1, 'question': '...', 'options': [...], 'correct_index': 0, 'explanation': '...'}, ...]
    """
    engine, client, model = get_ai_client()

    if engine == "mock":
        return [
            {
                "id": 1,
                "question": f"Which concept is most essential when designing solutions for {topic}?",
                "options": [
                    "High Availability and Fault Tolerance",
                    "Hardcoding database credentials in source code",
                    "Disabling all network security groups",
                    "Using a single server with zero backups"
                ],
                "correct_index": 0,
                "explanation": "High availability ensures services remain reachable and operational even during hardware or network failures."
            },
            {
                "id": 2,
                "question": "What is the primary benefit of a cloud-managed service?",
                "options": [
                    "Reduces operational overhead for patching and hardware maintenance",
                    "Completely eliminates the need for software testing",
                    "Guarantees free infinite computing power",
                    "Makes database normalization unnecessary"
                ],
                "correct_index": 0,
                "explanation": "Managed services handle infrastructure updates and underlying operating system maintenance so you can focus on application logic."
            }
        ]

    prompt = (
        f"Generate 3 multiple-choice practice questions for '{topic}'.\n"
        "Return ONLY a JSON array of objects with: 'id' (int), 'question' (str), 'options' (list of 4 strings), 'correct_index' (0-3), and 'explanation' (str)."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an exam generator that outputs ONLY valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        raw = response.choices[0].message.content.strip()
        data = json.loads(raw)
        return data.get("quiz", data) if isinstance(data, dict) else data
    except Exception as e:
        logger.warning(f"Quiz parsing error, using fallback: {e}")
        return []

def _mock_socratic_response(user_text: str) -> str:
    """Simulates a Socratic tutor response when no external API key is active."""
    return (
        f"That is a great inquiry regarding **'{user_text}'**.\n\n"
        "To help you think through this conceptually:\n"
        "1. What is the main problem or constraint this concept is trying to solve?\n"
        "2. If you had to explain how data flows through this system to a classmate, where does it start?\n\n"
        "*Take a guess or share your initial thought, and we will build from there!*"
    )