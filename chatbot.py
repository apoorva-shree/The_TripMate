"""
TripMate AI - Chatbot Engine
==============================
Handles interaction with the official Google Gemini SDK (google-genai),
conversation history formatting, streaming responses, retry handling with
exponential backoff, and comprehensive error handling for authentication,
rate limits, and network issues.
"""

import os
import time
import logging
from typing import Generator, List, Dict, Optional, Tuple
from dotenv import load_dotenv

# Import Google GenAI SDK
from google import genai
from google.genai import types, errors

# Retry support
import tenacity
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

from config import SYSTEM_INSTRUCTION, DEFAULT_MODEL

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Custom Exceptions
# ---------------------------------------------------------------------------

class TripMateError(Exception):
    """Base exception for TripMate AI chatbot errors."""
    pass


class MissingAPIKeyError(TripMateError):
    """Raised when the Gemini API key is missing or not configured."""
    pass


class AuthenticationError(TripMateError):
    """Raised when the Gemini API key is invalid or unauthorized."""
    pass


class RateLimitError(TripMateError):
    """Raised when the Gemini API rate limit or quota is exceeded."""
    pass


class NetworkError(TripMateError):
    """Raised when network or connectivity issues prevent reaching the Gemini API."""
    pass


# ---------------------------------------------------------------------------
# Retry helpers
# ---------------------------------------------------------------------------

def _is_retryable(exc: BaseException) -> bool:
    """Returns True for transient errors worth retrying."""
    if isinstance(exc, errors.ServerError):
        return True
    if isinstance(exc, errors.APIError):
        # 429 = quota / rate limit, 500/502/503 = server side
        return getattr(exc, "code", 0) in (429, 500, 502, 503)
    # Network / connection errors from httpx or standard library
    exc_str = str(exc).lower()
    return any(t in exc_str for t in [
        "connect", "getaddrinfo", "timeout", "network", "socket",
        "connectionerror", "remotedisconnected", "read error",
    ])


def _make_retry_decorator(max_attempts: int = 3):
    return retry(
        retry=tenacity.retry_if_exception(_is_retryable),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )


# ---------------------------------------------------------------------------
# Main Chatbot class
# ---------------------------------------------------------------------------

class TripMateChatbot:
    """
    Manages Google Gemini API client sessions, formats multi-turn chat history,
    streams conversational responses, and applies retry with exponential backoff.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the chatbot with an optional API key.
        Falls back to GEMINI_API_KEY / GOOGLE_API_KEY environment variables.
        """
        load_dotenv(override=True)
        self.api_key: Optional[str] = self._resolve_api_key(api_key)
        self._client: Optional[genai.Client] = None

        if self.is_configured():
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception:
                self._client = None

    # ------------------------------------------------------------------
    # API key management
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_api_key(api_key: Optional[str] = None) -> Optional[str]:
        """Resolves API key from argument or environment, filtering placeholders."""
        candidate = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not candidate:
            return None
        candidate = candidate.strip()
        if candidate in ("your_gemini_api_key_here", "YOUR_API_KEY", "") or len(candidate) < 5:
            return None
        return candidate

    def update_api_key(self, api_key: str):
        """Updates the active API key and reinitializes the client."""
        resolved = self._resolve_api_key(api_key)
        if not resolved:
            self.api_key = None
            self._client = None
            raise MissingAPIKeyError("The provided API key is empty or invalid.")
        self.api_key = resolved
        try:
            self._client = genai.Client(api_key=self.api_key)
        except Exception as e:
            self._client = None
            raise AuthenticationError(f"Failed to initialize Gemini client: {str(e)}") from e

    def is_configured(self) -> bool:
        """Returns True if a valid API key string is present."""
        return bool(self.api_key and len(self.api_key) >= 5)

    def _get_client(self) -> genai.Client:
        """Returns the active GenAI client or raises MissingAPIKeyError."""
        if not self.is_configured():
            raise MissingAPIKeyError(
                "Gemini API key is not configured. Please set GEMINI_API_KEY in your .env file "
                "or enter it in the sidebar settings."
            )
        if self._client is None:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                raise AuthenticationError(
                    f"Unable to initialize Gemini client: {str(e)}"
                ) from e
        return self._client

    # ------------------------------------------------------------------
    # History formatting
    # ------------------------------------------------------------------

    def _format_history_to_contents(
        self,
        history: List[Dict[str, str]],
        new_prompt: str,
    ) -> List[types.Content]:
        """
        Converts Streamlit message history + new prompt into google-genai
        Content structures.  Streamlit uses 'assistant'; Gemini expects 'model'.
        """
        contents: List[types.Content] = []

        for msg in history:
            role = msg.get("role")
            text = msg.get("content", "").strip()
            if not text:
                continue
            gemini_role = "user" if role == "user" else "model"
            contents.append(
                types.Content(
                    role=gemini_role,
                    parts=[types.Part.from_text(text=text)],
                )
            )

        # Append the current user prompt as the final turn
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=new_prompt.strip())],
            )
        )
        return contents

    # ------------------------------------------------------------------
    # Error classification
    # ------------------------------------------------------------------

    def _classify_api_error(self, exc: Exception) -> TripMateError:
        """Maps SDK / network exceptions to typed TripMate errors."""
        if isinstance(exc, errors.APIError):
            code = getattr(exc, "code", 0)
            msg = str(exc)
            if code in (401, 403) or any(t in msg for t in [
                "API_KEY_INVALID", "PERMISSION_DENIED", "api key not valid"
            ]):
                return AuthenticationError(
                    "Invalid or unauthorized Gemini API key. "
                    "Please verify your key at Google AI Studio."
                )
            if code == 429 or any(t in msg.lower() for t in [
                "resource_exhausted", "quota", "rate limit"
            ]):
                return RateLimitError(
                    "Gemini API rate limit or quota exceeded. "
                    "Please wait a moment and try again."
                )
            return TripMateError(f"Gemini API Error ({code or 'Unknown'}): {msg}")

        # Generic network / connection errors
        exc_str = str(exc).lower()
        if any(t in exc_str for t in [
            "connect", "getaddrinfo", "timeout", "network", "socket",
            "connectionerror", "remotedisconnected",
        ]):
            return NetworkError(
                "Network connection error: Unable to reach the Gemini API server. "
                "Please check your internet connection."
            )
        if "api_key" in exc_str and "invalid" in exc_str:
            return AuthenticationError(
                "Gemini API key error. Please verify your API key is correctly formatted."
            )
        return TripMateError(f"An unexpected error occurred: {str(exc)}")

    # ------------------------------------------------------------------
    # Streaming response with retry
    # ------------------------------------------------------------------

    def stream_response(
        self,
        history: List[Dict[str, str]],
        new_prompt: str,
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        max_retries: int = 3,
    ) -> Generator[str, None, None]:
        """
        Streams response chunks from Google Gemini API with automatic retry
        on transient errors (rate limits, server errors, network blips).
        """
        client = self._get_client()
        contents = self._format_history_to_contents(history, new_prompt)
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=temperature,
        )

        last_exc: Optional[Exception] = None

        for attempt in range(1, max_retries + 1):
            try:
                response_stream = client.models.generate_content_stream(
                    model=model,
                    contents=contents,
                    config=config,
                )
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
                return  # Success — exit generator cleanly

            except Exception as exc:
                last_exc = exc

                # Classify the error immediately for non-retryable types
                if isinstance(exc, errors.APIError):
                    code = getattr(exc, "code", 0)
                    # Auth errors are never retried
                    if code in (401, 403) or "API_KEY_INVALID" in str(exc):
                        raise self._classify_api_error(exc) from exc

                # If we still have retry budget and error is transient, wait and retry
                if attempt < max_retries and _is_retryable(exc):
                    wait_secs = min(2 ** attempt, 8)  # 2, 4, 8 seconds
                    time.sleep(wait_secs)
                    continue

                # Exhausted retries or non-retryable — raise classified error
                raise self._classify_api_error(exc) from exc

        # Should not reach here, but safeguard
        if last_exc:
            raise self._classify_api_error(last_exc) from last_exc

    # ------------------------------------------------------------------
    # Connection test
    # ------------------------------------------------------------------

    def test_connection(self, model: str = DEFAULT_MODEL) -> Tuple[bool, str]:
        """
        Tests the current API configuration with a minimal prompt.
        Returns (success, status_message).
        """
        if not self.is_configured():
            return False, "API key is not configured."

        try:
            client = self._get_client()
            resp = client.models.generate_content(
                model=model,
                contents="Ping. Reply with 'OK'.",
                config=types.GenerateContentConfig(max_output_tokens=10),
            )
            if resp.text:
                return True, "API Key is valid and connected to Gemini!"
            return False, "Received empty response from Gemini."

        except errors.APIError as e:
            msg = str(e)
            if "API_KEY_INVALID" in msg or "PERMISSION_DENIED" in msg:
                return False, "Invalid API key. Please verify at Google AI Studio."
            if "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
                return False, "Rate limit hit during test. Your key is likely valid — try again soon."
            return False, f"API Error: {msg}"

        except Exception as e:
            exc_str = str(e).lower()
            if any(t in exc_str for t in ["connect", "getaddrinfo", "network", "socket", "timeout"]):
                return False, "Network error: Cannot reach Gemini API servers. Check your internet connection."
            return False, f"Connection test failed: {str(e)}"
