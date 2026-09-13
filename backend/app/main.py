from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.api.routes import auth, purchase, financial_data, savings

# Make sure all models are registered on Base before create_all runs.
from app.models import user, transaction, commitment, purchase as purchase_model  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description=(
        "Agentic AI financial decision assistant. An LLM (via Groq) reasons "
        "over each user's real balance, commitments, transactions and "
        "preferences to decide whether a purchase is safe to make now, "
        "with a plan, later, or not at all."
    ),
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(purchase.router)
app.include_router(financial_data.router)
app.include_router(savings.router)


@app.get("/")
def home():
    return {
        "message": f"{settings.app_name} API is running!",
        "status": "success",
        "ai_mode": "agentic-llm",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
