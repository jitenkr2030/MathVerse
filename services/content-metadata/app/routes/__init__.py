# Routes module
from app.routes.courses import router as courses_router
from app.routes.lessons import router as lessons_router
from app.routes.concepts import router as concepts_router
from app.routes.syllabus import router as syllabus_router
from app.routes.content import router as content_router

__all__ = [
    'courses_router',
    'lessons_router', 
    'concepts_router',
    'syllabus_router',
    'content_router',
]
