import uvicorn
import os
from app.config import settings

if __name__ == "__main__":
    print(f"Starting AI Resume Analyzer Backend on http://{settings.HOST}:{settings.PORT}")
    print(f"Swagger Documentation available at http://{settings.HOST}:{settings.PORT}/docs")
    print(f"Database Mode: {'Supabase PostgreSQL' if settings.is_supabase_configured else 'Zero-Config Local Storage'}")
    print(f"AI Provider: {settings.AI_PROVIDER}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=(settings.ENVIRONMENT == "development")
    )
