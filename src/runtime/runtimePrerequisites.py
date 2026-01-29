import os
from typing import Tuple


def checkCredentials() -> Tuple[bool, str]:
    """Check if GOOGLE_API_KEY environment variable is set."""
    apiKey = os.environ.get("GOOGLE_API_KEY")
    if not apiKey:
        return False, "GOOGLE_API_KEY environment variable is not set"
    if not apiKey.strip():
        return False, "GOOGLE_API_KEY environment variable is empty"
    return True, "Credentials found"


def validateApiConnection() -> Tuple[bool, str]:
    """Validate that Google API is reachable (placeholder for now)."""
    # TODO: Implement lightweight API ping in M3
    # For now, just return True if credentials exist
    credsOk, msg = checkCredentials()
    if not credsOk:
        return False, msg
    return True, "API connection validation skipped (will be implemented in M3)"


def validate(flow=None) -> Tuple[bool, str]:
    """
    Validate runtime prerequisites.
    
    Args:
        flow: Optional Flow object (for future use in M3)
    
    Returns:
        Tuple of (is_valid, message)
    """
    credsOk, credsMsg = checkCredentials()
    if not credsOk:
        return False, credsMsg
    
    # Future: validate flow structure, agent configs, etc.
    
    return True, "Validation passed"
