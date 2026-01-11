from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import chat, user, schedule, plan, schedule_courses
from .auth.router import router as auth_router
from .config.settings import settings
from .database import init_db

app = FastAPI(title="Northwestern Course AI API")

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(chat.router)
app.include_router(user.router)
app.include_router(schedule.router)
app.include_router(schedule_courses.router)
app.include_router(plan.router)