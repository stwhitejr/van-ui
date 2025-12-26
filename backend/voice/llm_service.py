"""LLM service for interpreting voice commands using Ollama."""

import json
import requests
from typing import Optional, Dict, Any
from .config import OLLAMA_HOST, OLLAMA_MODEL, CONFIDENCE_THRESHOLD
from .command_executor import AVAILABLE_COMMANDS


class LLMService:
    """Service for interpreting voice commands using local LLM."""

    def __init__(self):
        self.host = OLLAMA_HOST
        self.model = OLLAMA_MODEL
        self.confidence_threshold = CONFIDENCE_THRESHOLD
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

    def _build_prompt(self, spoken_text: str) -> str:
        """Build prompt for LLM with available commands."""
        commands_list = "\n".join(
            [
                f"- {name}: {info['description']}"
                for name, info in AVAILABLE_COMMANDS.items()
            ]
        )

        prompt = f"""You are a voice command interpreter for a camper van control system.
The user has spoken: "{spoken_text}"

Available commands:
{commands_list}

Your task is to:
1. Determine which command the user wants to execute
2. Assess your confidence level (0.0 to 1.0)
3. Provide a natural language response to speak back to the user

Respond ONLY with valid JSON in this exact format:
{{
    "command": "command_name",
    "confidence": 0.85,
    "needs_confirmation": false,
    "user_message": "Executing command to toggle the inverter",
    "clarification": null
}}

Rules:
- Use "command" field with one of the available command names exactly as listed
- Use "confidence" field with a value between 0.0 and 1.0
- Set "needs_confirmation" to true if confidence is below {self.confidence_threshold}
- Use "user_message" for what to say to the user (natural language)
- Use "clarification" only if you need to ask the user something (null otherwise)
- If the command is unclear, set command to null and provide clarification
- Be concise in user_message (under 20 words typically)

Respond with JSON only, no other text:"""

        return prompt

    def interpret_command(
        self, spoken_text: str, conversation_context: Optional[list] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Interpret spoken text as a command.

        Args:
            spoken_text: The transcribed text from voice input
            conversation_context: Optional list of previous messages for context

        Returns:
            Dict with command, confidence, user_message, etc. or None if unavailable
        """
        if not self.available:
            return None

        if not spoken_text or not spoken_text.strip():
            return None

        prompt = self._build_prompt(spoken_text)

        try:
            # Build messages for conversation context
            messages = []
            if conversation_context:
                messages.extend(conversation_context)

            messages.append({"role": "user", "content": prompt})

            # Call Ollama API
            response = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,  # Lower temperature for more consistent command interpretation
                    },
                },
                timeout=10,
            )

            if response.status_code != 200:
                print(f"Ollama API error: {response.status_code}")
                return None

            result = response.json()
            content = result.get("message", {}).get("content", "").strip()

            # Try to extract JSON from response
            # Sometimes LLM adds extra text, so we try to find JSON
            json_start = content.find("{")
            json_end = content.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                parsed = json.loads(json_str)

                # Validate and normalize response
                command = parsed.get("command")
                confidence = float(parsed.get("confidence", 0.0))
                user_message = parsed.get("user_message", "")
                clarification = parsed.get("clarification")
                needs_confirmation = parsed.get(
                    "needs_confirmation", confidence < self.confidence_threshold
                )

                # Ensure confidence-based confirmation flag
                if confidence < self.confidence_threshold:
                    needs_confirmation = True

                return {
                    "command": command,
                    "confidence": confidence,
                    "needs_confirmation": needs_confirmation,
                    "user_message": user_message or "Processing command",
                    "clarification": clarification,
                }
            else:
                print(f"Could not parse JSON from LLM response: {content}")
                return None

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in LLM interpretation: {e}")
            return None

    def is_available(self) -> bool:
        """Check if LLM service is available."""
        return self.available
