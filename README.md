# FitBuddy — AI Fitness Plan Generator

A FastAPI + SQLite + Gemini application that creates personalized 7-day workout plans, provides a nutrition/recovery tip, stores plans, and revises plans from feedback.

## Setup

1. Install Python 3.11+.
2. Open this folder in VS Code.
3. Create a virtual environment:
   - Windows: `python -m venv venv`
   - PowerShell: `venv\Scripts\Activate.ps1`
4. Install packages: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env`.
6. Add your Gemini API key to `.env`.
7. Run:
   `uvicorn app.main:app --reload`
8. Open `http://127.0.0.1:8000`.

API docs: `http://127.0.0.1:8000/docs`
Health: `http://127.0.0.1:8000/health`
Admin: `http://127.0.0.1:8000/view-all-users`
Default demo admin password: `admin123`

## Tests

Run `pytest`.

## Notes

The Gemini model names are configurable through `.env`. Use a model available to your Gemini API account if the default model is unavailable. This application provides general fitness information and is not medical advice.
