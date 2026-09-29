from google import genai
from .config import GEMINI_API_KEY

_client = None

def get_gemini_client():
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is missing.")
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client
