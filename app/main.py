import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logger import logger
from app.api.routes import runs, targets, benchmarks, memory, ws

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Frontend Dev Server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes — runs router owns its own prefixes (/api/runs + /api/run aliases)
app.include_router(runs.router, prefix=settings.API_V1_STR)
app.include_router(targets.router, prefix=settings.API_V1_STR)
app.include_router(benchmarks.router, prefix=settings.API_V1_STR)
app.include_router(memory.router, prefix=settings.API_V1_STR)
app.include_router(ws.router)

# Mount mock target apps for local testing & judging demo
if os.path.exists(settings.MOCK_APPS_DIR):
    app.mount("/mock_apps", StaticFiles(directory=settings.MOCK_APPS_DIR), name="mock_apps")

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "docs": "/docs",
        "routes": {
            "runs": f"{settings.API_V1_STR}/runs",
            "targets": f"{settings.API_V1_STR}/targets",
            "benchmarks": f"{settings.API_V1_STR}/benchmarks",
            "memory": f"{settings.API_V1_STR}/memory/stats",
            "ws": "/ws/runs/{run_id}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
