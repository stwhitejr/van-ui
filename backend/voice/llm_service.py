"""LLM service for interpreting voice commands using Ollama."""

import json
import time
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

The available commands below are in the format of "command_name: description".
{commands_list}

Your task:
1. Match the spoken text to the most appropriate command from the list above
2. Leverage the description of the command to help you match the command to the user's intent
3. Use partial matches when reasonable (e.g., "fan" → toggle_fan, "leds" → turn_on_leds or turn_off_leds)
4. Assess confidence based on how clear the match is
5. Only attempt to match if the text can be interpreted as a command

CRITICAL: Only match if the spoken text clearly relates to van control commands. Common words like "hello", "hi", "yes", "no", "thanks" should return null.

Confidence scoring guidelines:
- 0.9-1.0: Very clear, explicit match (e.g., "toggle the inverter" → toggle_inverter)
- 0.75-0.89: Good match, clear intent (e.g., "fan" → toggle_fan, "turn on lights" → toggle_lights)
- 0.6-0.74: Reasonable match but some ambiguity (e.g., "lights" could be toggle_lights or turn_on_leds)
- 0.4-0.59: Weak match, needs confirmation
- Below 0.4: Unclear or unrelated - MUST return null

What MUST return null (confidence 0.0):
- Greetings: "hello", "hi", "hey", "good morning"
- Responses: "yes", "no", "okay", "thanks", "thank you"
- Questions: "how are you", "what's the weather", "what time is it"
- Unrelated words that don't match any command description
- If you're not confident it's a command, return null

Examples:
- "fan" → toggle_fan (confidence ~0.8, clearly refers to fan command)
- "turn on the fan" → toggle_fan (confidence ~0.95, explicit)
- "hello" → null (confidence 0.0, greeting, not a command)
- "hi" → null (confidence 0.0, greeting, not a command)
- "yes" → null (confidence 0.0, response word, not a command)
- "how are you" → null (confidence 0.0, question, not a command)
- "leds" → turn_on_leds or turn_off_leds (confidence ~0.7, needs context)
- "blue" → blue_leds (confidence ~0.85, clear intent for LED color)
- "inverter" → toggle_inverter (confidence ~0.8, clearly refers to inverter)
- "lights" → toggle_lights (confidence ~0.75, likely refers to main lights)

Respond ONLY with valid JSON in this exact format:
{{
    "command": "command_name" or null,
    "confidence": 0.85,
    "needs_confirmation": false,
    "user_message": "Executing command to toggle the inverter",
    "clarification": null or "What would you like me to do?"
}}

Rules:
- Match partial words ONLY when they clearly refer to a command (e.g., "fan" = toggle_fan, "inverter" = toggle_inverter)
- Common words like "hello", "hi", "yes", "no" are NOT commands - return null
- Use "command" field with one of the available command names, or null if:
  * The text is a greeting, response, or question
  * The text doesn't relate to any command description
  * You're uncertain it's a command (confidence < 0.4)
- Use "confidence" field with a value between 0.0 and 1.0
- Set "needs_confirmation" to true if confidence is below {self.confidence_threshold}
- Use "user_message" for what to say to the user (natural language)
- Use "clarification" when command is null (e.g., "I didn't understand. What would you like me to do?")
- Be concise in user_message (under 20 words typically)
- When in doubt, return null rather than guessing

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

            print(f"Calling Ollama API at {self.host}/api/chat with model {self.model}")
            start_time = time.time()

            # Call Ollama API
            response = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Even lower for faster, more deterministic responses
                        "num_predict": 150,  # Limit response length (JSON is short)
                    },
                },
                timeout=10,
            )

            elapsed = time.time() - start_time
            print(f"Ollama API response received in {elapsed:.2f}s, status: {response.status_code}")

            if response.status_code != 200:
                print(f"Ollama API error: {response.status_code}")
                try:
                    error_body = response.text[:200]  # First 200 chars
                    print(f"Error response body: {error_body}")
                except:
                    pass
                return None

            result = response.json()
            content = result.get("message", {}).get("content", "").strip()
            print(f"LLM response content length: {len(content)} chars")
            if len(content) > 500:
                print(f"LLM response preview: {content[:200]}...")
            else:
                print(f"LLM response: {content}")

            # Try to extract JSON from response
            # Sometimes LLM adds extra text, so we try to find JSON
            json_start = content.find("{")
            json_end = content.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                print(f"Extracted JSON: {json_str}")
                parsed = json.loads(json_str)

                # Validate and normalize response
                command = parsed.get("command")
                confidence = float(parsed.get("confidence", 0.0))
                user_message = parsed.get("user_message", "")
                clarification = parsed.get("clarification")
                needs_confirmation = parsed.get(
                    "needs_confirmation", confidence < self.confidence_threshold
                )

                # If command is null or empty, treat as no match
                if not command or command == "null" or command.lower() == "null":
                    return {
                        "command": None,
                        "confidence": 0.0,
                        "needs_confirmation": False,
                        "user_message": clarification
                        or "I didn't understand that command.",
                        "clarification": clarification
                        or "What would you like me to do?",
                    }

                # Validate command exists
                if command not in AVAILABLE_COMMANDS:
                    return {
                        "command": None,
                        "confidence": 0.0,
                        "needs_confirmation": False,
                        "user_message": "I don't recognize that command.",
                        "clarification": "What would you like me to do?",
                    }

                # Additional safety: if confidence is very low but command is set, be more cautious
                # This catches cases where the model sets a command but with very low confidence
                if confidence < 0.3:
                    return {
                        "command": None,
                        "confidence": 0.0,
                        "needs_confirmation": False,
                        "user_message": "I'm not sure what you want me to do.",
                        "clarification": "What would you like me to do?",
                    }

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
                print(f"Could not parse JSON from LLM response (no JSON found)")
                print(f"Full response content: {content}")
                return None

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Attempted to parse: {json_str if 'json_str' in locals() else 'N/A'}")
            return None
        except requests.exceptions.Timeout as e:
            print(f"LLM request timed out after 30s: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"LLM request error: {type(e).__name__}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in LLM interpretation: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def is_available(self) -> bool:
        """Check if LLM service is available."""
        return self.available
