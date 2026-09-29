from google.genai import types
from .config import GEMINI_WORKOUT_MODEL
from .gemini_client import get_gemini_client
from .schemas import UserInput, WorkoutPlanResponse

SYSTEM_INSTRUCTION = """You are FitBuddy, a safe fitness-plan assistant.
Create practical beginner-friendly exercise plans. Do not diagnose conditions,
prescribe medicines, or recommend dangerous/extreme practices. Include rest,
warm-up, cooldown, sets/reps and recovery guidance. Return exactly 7 days."""

def generate_workout_plan(user: UserInput) -> tuple[WorkoutPlanResponse, str]:
    prompt = f"""Create a personalized 7-day workout plan for:
Name: {user.username}
Age: {user.age}
Weight: {user.weight} kg
Goal: {user.goal}
Intensity: {user.intensity}

Make the plan practical and easy to follow."""
    client = get_gemini_client()
    response = client.models.generate_content(
        model=GEMINI_WORKOUT_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=WorkoutPlanResponse,
            temperature=0.7,
            max_output_tokens=6000,
        ),
    )
    plan = WorkoutPlanResponse.model_validate_json(response.text)
    if len(plan.days) != 7:
        raise ValueError("Gemini returned a plan that is not exactly 7 days.")
    return plan, format_workout_plan(plan)

def format_workout_plan(plan: WorkoutPlanResponse) -> str:
    parts = []
    for day in plan.days:
        parts.append(f"{day.day} — {day.focus}")
        parts.append(f"Warm-up: {day.warmup}")
        for ex in day.exercises:
            parts.append(f"• {ex.name} | {ex.sets_reps} | Rest: {ex.rest}")
        parts.append(f"Cooldown: {day.cooldown}")
        parts.append("")
    return "\n".join(parts).strip()
