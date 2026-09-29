from typing import Literal
from pydantic import BaseModel, Field

GoalType = Literal["weight loss", "muscle gain", "general wellness", "flexibility", "endurance"]
IntensityType = Literal["low", "medium", "high"]

class UserInput(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    user_id: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, le=400)
    goal: GoalType
    intensity: IntensityType

class FeedbackRequest(BaseModel):
    user_id: str
    feedback: str = Field(min_length=3, max_length=2000)

class Exercise(BaseModel):
    name: str
    sets_reps: str
    rest: str

class WorkoutDay(BaseModel):
    day: str
    focus: str
    warmup: str
    exercises: list[Exercise]
    cooldown: str

class WorkoutPlanResponse(BaseModel):
    days: list[WorkoutDay]

class NutritionResponse(BaseModel):
    tip: str
