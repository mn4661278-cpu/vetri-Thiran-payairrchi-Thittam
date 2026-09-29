import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "FitBuddy")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fitbuddy.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_WORKOUT_MODEL = os.getenv("GEMINI_WORKOUT_MODEL", "gemini-2.5-flash")
GEMINI_FAST_MODEL = os.getenv("GEMINI_FAST_MODEL", "gemini-2.5-flash")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

def validate_configuration():
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured. Add it to .env.")
