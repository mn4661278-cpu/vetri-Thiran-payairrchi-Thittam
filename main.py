from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .config import APP_NAME
from .database import init_db
from .routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title=APP_NAME, version="1.0.0", description="AI-powered fitness plan generator using Gemini.")
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "healthy", "application": APP_NAME}
