import os
from typing import Optional
# Note: Actual ADK imports will be added when we have data models
# from google.adk.agents.llm_agent import Agent

# Hardcoded model per requirements-impl.md §8
MODEL_ID = "gemini-1.5-flash"


def getApiKey() -> Optional[str]:
    """Get Google API key from environment variable."""
    return os.environ.get("GOOGLE_API_KEY")


async def runAgent(agentId: str, inputText: str, flow, getCredentials) -> str:
    """
    Run a single agent with given input.
    
    Note: This is a placeholder structure. Full implementation requires:
    - Agent data model (M1)
    - Flow data model (M1)
    - ADK Agent instantiation
    
    Args:
        agentId: ID of agent to run
        inputText: User message or upstream agent output
        flow: Flow object containing agent configs
        getCredentials: Function to retrieve credentials
    
    Returns:
        Agent output string
    """
    # TODO: Implement in M3 when data models are available
    raise NotImplementedError("Full implementation requires M1 data models")
