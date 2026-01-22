"""
Google ADK Agent Configuration for LINE Chatbot
Configures an AI agent with Google Search capabilities for intelligent responses.
"""

import os
from google.adk.agents import Agent
from google.adk.tools import google_search


def create_search_agent() -> Agent:
    """
    Creates and returns a Google ADK agent configured with Google Search tool.
    
    The agent is designed to:
    - Answer user questions intelligently using Google Search
    - Provide up-to-date, factual information
    - Cite sources when appropriate
    - Be conversational and helpful
    
    Returns:
        Agent: Configured Google ADK agent with search capabilities
    """
    
    # Get the model from environment or use default
    model = os.getenv('ADK_MODEL', 'gemini-2.5-flash')
    
    agent = Agent(
        name="line_search_assistant",
        model=model,
        description=(
            "A helpful LINE chatbot assistant that can search the web to answer "
            "questions with current, accurate information."
        ),
        instruction=(
            "You are a helpful AI assistant integrated into a LINE messaging app. "
            "When users ask questions, use Google Search to find current, accurate information. "
            "Provide concise but informative responses suitable for a chat interface. "
            "Always be friendly and conversational. "
            "When providing facts, cite your sources when relevant. "
            "If you can't find reliable information, be honest about it. "
            "Keep responses clear and easy to read on mobile devices."
        ),
        tools=[google_search]
    )
    
    return agent


# Initialize the agent (will be used by main.py)
search_agent = create_search_agent()
