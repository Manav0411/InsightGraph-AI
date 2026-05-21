from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import newsletter, users, metrics

app = FastAPI(
    title="InsightGraph API",
    description="Production backend for InsightGraph - the Adaptive AI Intelligence Platform.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(newsletter.router)
app.include_router(users.router)
app.include_router(metrics.router)

@app.get("/health", tags=["Health"])
async def health():
    """
    Basic health check route.
    """
    return {"status": "ok"}
