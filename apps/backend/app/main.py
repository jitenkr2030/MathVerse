from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn

from app.modules.auth.routes import router as auth_router
from app.modules.users.routes import router as users_router
from app.modules.courses.routes import router as courses_router
from app.modules.lessons.routes import router as lessons_router
from app.modules.videos.routes import router as videos_router
from app.modules.quizzes.routes import router as quizzes_router
from app.modules.progress.routes import router as progress_router
from app.modules.payments.routes import router as payments_router
from app.modules.creators.routes import router as creators_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("MathVerse Backend API starting up...")
    yield
    # Shutdown
    print("MathVerse Backend API shutting down...")

app = FastAPI(
    title="MathVerse API",
    description="Animation-first Mathematics Learning Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(courses_router, prefix="/api/courses", tags=["Courses"])
app.include_router(lessons_router, prefix="/api/lessons", tags=["Lessons"])
app.include_router(videos_router, prefix="/api/videos", tags=["Videos"])
app.include_router(quizzes_router, prefix="/api/quizzes", tags=["Quizzes"])
app.include_router(progress_router, prefix="/api/progress", tags=["Progress"])
app.include_router(payments_router, prefix="/api/payments", tags=["Payments"])
app.include_router(creators_router, prefix="/api/creators", tags=["Creators"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to MathVerse API",
        "description": "Animation-first Mathematics Learning Platform",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mathverse-backend"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )