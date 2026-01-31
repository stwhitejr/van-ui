"""LLM service for conversational chat using Ollama."""

import requests
from typing import Optional, List, Dict
from .config import OLLAMA_HOST, OLLAMA_MODEL


class LLMService:
    """Service for conversational chat using local LLM."""

    def __init__(self):
        self.host = OLLAMA_HOST
        self.model = OLLAMA_MODEL
        self.available = False
        self._check_availability()

    def _check_availability(self):
        """Check if Ollama service is available."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=2)
            if response.status_code == 200:
                # Check if model is available
                models = response.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                if any(self.model in name for name in model_names):
                    self.available = True
                    print(f"Ollama service available with model {self.model}")
                else:
                    print(
                        f"Warning: Model {self.model} not found. Available models: {model_names}"
                    )
            else:
                print(f"Ollama API returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Ollama service not available: {e}")
            self.available = False

    def chat(self, messages: List[Dict[str, str]], timeout: int = 60) -> Optional[str]:
        """
        Send messages to LLM and get response.

        Args:
            messages: List of message dicts with "role" and "content" keys
            timeout: Request timeout in seconds

        Returns:
            Response text from LLM, or None if error
        """
        if not self.available:
            return None

        try:
            response = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,  # Conversational temperature
                    },
                },
                timeout=timeout,
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get("message", {}).get("content", "").strip()
                return content if content else None
            else:
                print(f"LLM API error: {response.status_code}")
                return None

        except requests.exceptions.Timeout:
            print(f"LLM request timed out after {timeout}s")
            return None
        except requests.exceptions.RequestException as e:
            print(f"LLM request error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in LLM chat: {e}")
            return None

    def is_available(self) -> bool:
        """Check if LLM service is available."""
        return self.available

