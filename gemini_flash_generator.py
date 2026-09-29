from google.genai import types
from .config import GEMINI_FAST_MODEL
from .gemini_client import get_gemini_client
from .schemas import NutritionResponse

def generate_nutrition_tip(goal: str, intensity: str) -> str:
    prompt = f"""Give one concise general nutrition and recovery tip for a fitness
user whose goal is {goal} and workout intensity is {intensity}. Avoid diagnosis,
medication advice, dangerous diets, and extreme calorie restriction. Keep it
under 120 words."""
    response = get_gemini_client().models.generate_content(
        model=GEMINI_FAST_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=NutritionResponse,
            temperature=0.5,
            max_output_tokens=300,
        ),
    )
    return NutritionResponse.model_validate_json(response.text).tip
