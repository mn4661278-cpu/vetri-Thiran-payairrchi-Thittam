from google.genai import types
from .config import GEMINI_WORKOUT_MODEL
from .gemini_client import get_gemini_client
from .schemas import UserInput, WorkoutPlanResponse
from .gemini_generator import format_workout_plan

def update_workout_plan(user: UserInput, original_plan: str, feedback: str):
    prompt = f"""Revise this user's 7-day workout plan based on their feedback.

User goal: {user.goal}
Intensity: {user.intensity}
Original plan:
{original_plan}

User feedback:
{feedback}

Return exactly 7 days. Keep the plan safe and practical."""
    response = get_gemini_client().models.generate_content(
        model=GEMINI_WORKOUT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are FitBuddy. Do not diagnose or prescribe medication.",
            response_mime_type="application/json",
            response_schema=WorkoutPlanResponse,
            temperature=0.7,
            max_output_tokens=6000,
        ),
    )
    plan = WorkoutPlanResponse.model_validate_json(response.text)
    if len(plan.days) != 7:
        raise ValueError("Gemini returned a revised plan that is not exactly 7 days.")
    return format_workout_plan(plan)
