"""
Main entry point for the Simple RAG Chatbot API.

This FastAPI application provides:
- A web-based chat interface (served with Jinja2 templates)
- A backend API for handling user messages
- Session management using a thread_id stored in cookies

Architecture overview:
----------------------
Frontend (HTML/JS)
        ↓
FastAPI routes (main.py)
        ↓
Agent layer (core/agent.py)
        ↓
RAG pipeline (retrieval + generation)

Key Features:
-------------
- Stateless backend with session tracking via cookies
- Thread-based conversation memory
- Simple greeting fallback (for quick responsiveness)
- Async response generation via agent module
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uuid
from fastapi.responses import HTMLResponse

from core import agent

# ================================
# App Initialization
# ================================
app = FastAPI()

# Mount static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 template configuration
templates = Jinja2Templates(directory="templates")


# ================================
# Request Schema
# ================================
class ChatRequest(BaseModel):
    """
    Schema for incoming chat messages.

    Attributes:
        message (str): User input message sent from frontend
    """
    message: str


# ================================
# Route: Start New Chat
# ================================
@app.get("/new_chat")
def new_chat(request: Request):
    """
    Initialize a new chat session.

    - Generates a unique thread_id
    - Stores it in a secure HTTP-only cookie
    - Returns the chat interface

    Why thread_id?
    --------------
    It allows the backend (agent) to:
    - Track conversation history
    - Maintain context across multiple messages

    Security:
    ---------
    - httponly=True → prevents JavaScript access (XSS protection)
    - samesite="Lax" → protects against CSRF attacks
    """

    thread_id = str(uuid.uuid4())

    response = templates.TemplateResponse(
        request,
        "chat.html",
    )

    # Store thread_id securely in cookie
    response.set_cookie(
        key="thread_id",
        value=thread_id,
        httponly=True,
        samesite="Lax"
    )

    return response


# ================================
# Route: Chat API
# ================================
@app.post("/api/chat")
async def chat(request: Request, body: ChatRequest):
    """
    Main chat endpoint.

    Workflow:
    ---------
    1. Retrieve thread_id from cookies
    2. Fallback: create new thread if missing
    3. Handle simple greetings (fast path)
    4. Forward request to agent (RAG pipeline)
    5. Return generated response

    Args:
        request (Request): FastAPI request object (used for cookies)
        body (ChatRequest): User message payload

    Returns:
        dict: JSON response with generated reply
    """

    # Retrieve session thread_id
    thread_id = request.cookies.get("thread_id")

    # Fallback if cookie is missing
    if not thread_id:
        thread_id = str(uuid.uuid4())

    # Simple rule-based shortcut (avoid unnecessary LLM calls)
    if body.message.lower() in ["hello", "hi"]:
        return {"reply": "Hello, how can I help you today?"}

    # Generate response using agent (RAG / LLM pipeline)
    reply = await agent.generate_response(body.message, thread_id)

    return {"reply": reply}