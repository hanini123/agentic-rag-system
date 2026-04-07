"""
Agent Layer: RAG + Tool-augmented Conversational Engine

This module is the core of the system. It builds and runs the AI agent
responsible for generating responses using:

- LLM (NVIDIA-hosted model)
- External tools (web + Wikipedia search)
- Conversation memory (thread-based)

Architecture:
-------------
User سؤال → Agent → (LLM + Tools + Memory) → Response

Key Features:
-------------
- Tool-augmented reasoning (ReAct-style behavior)
- Thread-based conversational memory
- Async response generation
- Markdown-to-HTML rendering for frontend display
"""

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
import markdown
from core import tools, prompts
from config import settings
import os


# ================================
# API Keys Configuration
# ================================
# Keys are loaded securely from .env via config.py
os.environ['NVIDIA_API_KEY'] = settings.nvidia_api_key
os.environ['TAVILY_API_KEY'] = settings.tavily_api_key


# ================================
# Tools (Retrieval Layer)
# ================================
# These tools enable Retrieval-Augmented Generation (RAG)
tool_list = [
    tools.search_web,
    tools.search_wikipedia
]


# ================================
# LLM Configuration
# ================================
llm = ChatNVIDIA(
    model="mistralai/devstral-2-123b-instruct-2512",
    temperature=0.2,   # low randomness → more deterministic answers
    top_p=0.7
)


# ================================
# Memory (Conversation State)
# ================================
# Stores conversation history per thread_id
checkpointer = InMemorySaver()


# ================================
# Agent Initialization
# ================================
agent = create_agent(
    model=llm,
    tools=tool_list,
    system_prompt=prompts.SYSTEM_PROMPT,
    checkpointer=checkpointer
)


# ================================
# Generate Response (ASYNC)
# ================================
async def generate_response(question: str, thread_id: str):
    """
    Generate a response using the agent.

    Workflow:
    ---------
    1. Attach thread_id (for conversation memory)
    2. Send user message to agent
    3. Agent decides:
        - Direct answer OR
        - Use tools (RAG)
    4. Convert Markdown → HTML (for frontend rendering)

    Args:
        question (str): User input
        thread_id (str): Unique conversation identifier

    Returns:
        str: HTML-formatted response
    """

    # Attach thread_id to maintain memory
    config = {"configurable": {"thread_id": thread_id}}

    messages = {
        "messages": [
            {"role": "user", "content": question}
        ]
    }

    # Async agent execution
    result = await agent.ainvoke(messages, config=config)

    # Convert Markdown output → HTML for UI
    html_content = markdown.markdown(
        result["messages"][-1].content,
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "nl2br"
        ]
    )

    return html_content