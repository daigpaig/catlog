from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import chat, user, schedule
from .auth.router import router as auth_router
from .config.settings import settings

app = FastAPI(title="Northwestern Course AI API")

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