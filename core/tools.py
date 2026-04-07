"""
Tools Layer: Retrieval Functions for RAG

These tools provide external knowledge to the agent:
- Web search (real-time information)
- Wikipedia (structured knowledge)

Each tool:
- Retrieves documents
- Formats them into a structured context
- Returns them to the agent for reasoning
"""

from langchain_tavily import TavilySearch 
from langchain_community.document_loaders import WikipediaLoader
from langchain.tools import tool


# ================================
# Tool: Web Search
# ================================
@tool
def search_web(search_query):
    """
    Retrieve relevant documents from the web.

    Use case:
    - Current events
    - Recent updates
    - Real-time information

    Returns:
        dict: Formatted documents as context
    """

    tavily_search = TavilySearch(max_results=3)
    data = tavily_search.invoke({"query": search_query})

    search_docs = data.get("results", data)

    # Format documents for LLM consumption
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}


# ================================
# Tool: Wikipedia Search
# ================================
@tool
def search_wikipedia(search_query):
    """
    Retrieve structured knowledge from Wikipedia.

    Use case:
    - Definitions
    - Historical facts
    - Scientific explanations

    Returns:
        dict: Formatted documents as context
    """

    search_docs = WikipediaLoader(
        query=search_query,
        load_max_docs=2
    ).load()

    # Format documents
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )

    return {"context": [formatted_search_docs]}