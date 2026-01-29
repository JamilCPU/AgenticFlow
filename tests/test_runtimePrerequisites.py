import os
import pytest
from unittest.mock import patch
from src.runtime.runtimePrerequisites import checkCredentials, validate


def testCheckCredentialsWithKey():
    """Test credential check when GOOGLE_API_KEY is set."""
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key-123"}):
        isValid, message = checkCredentials()
        assert isValid is True
        assert "found" in message.lower()


def testCheckCredentialsWithoutKey():
    """Test credential check when GOOGLE_API_KEY is missing."""
    with patch.dict(os.environ, {}, clear=True):
        isValid, message = checkCredentials()
        assert isValid is False
        assert "not set" in message.lower()


def testCheckCredentialsEmptyKey():
    """Test credential check when GOOGLE_API_KEY is empty."""
    with patch.dict(os.environ, {"GOOGLE_API_KEY": "   "}):
        isValid, message = checkCredentials()
        assert isValid is False
        assert "empty" in message.lower()
