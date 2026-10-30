import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.core.config import settings
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.core.logging import logger
from backend.app.data.seed_data import seed_database
from backend.app.agents.llm_client import llm_client

# Import API routes
from backend.app.api.routes import (
    dashboard, resources, schedules, disruptions,
    agents, recovery, analytics, audit
)

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Agentic AI-powered Smart Campus Resource Management and Autonomous Disruption Recovery Platform"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Health endpoint
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "database": "connected",
        "llm_engine": {
            "provider": "Groq",
            "model": settings.GROQ_MODEL,
            "llm_available": llm_client.is_available(),
            "mode": "Active Groq LLM" if llm_client.is_available() else "Deterministic Agent Mode"
        },
        "optimisation_engine": "Google OR-Tools CP-SAT 9.15",
        "multi_agent_framework": "LangGraph 1.2"
    }

# Register API routers under /api
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(resources.router, prefix=settings.API_V1_STR)
app.include_router(schedules.router, prefix=settings.API_V1_STR)
app.include_router(disruptions.router, prefix=settings.API_V1_STR)
app.include_router(agents.router, prefix=settings.API_V1_STR)
app.include_router(recovery.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(audit.router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def on_startup():
    logger.info("Nexora Campus backend starting up...")
    seed_database()
    logger.info("Nexora Campus ready to serve API requests.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
