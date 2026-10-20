import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from api.routes import router
from models.cv_model import CVModel
from models.nlp_model import NLPModel
from rag.vectorstore import VectorStore
from llm.report_generator import ReportGenerator
from llm.qa_chain import QAChain
from utils.middleware import SecurityHeadersMiddleware, RequestTracingMiddleware

load_dotenv()

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── CORS allowed origins from environment (comma-separated) ───────────────────
_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
)
ALLOWED_ORIGINS: list[str] = [o.strip() for o in _raw_origins.split(",") if o.strip()]


# ── Application Lifespan ──────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load all models and resources at startup."""
    logger.info("🚀 Starting MedAI API (Multi-Modality — Production Mode)...")

    google_api_key = os.getenv("GOOGLE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # ── Chest X-Ray Vision Model ──────────────────────────────────────────────
    logger.info("Loading Chest X-Ray Vision Model...")
    app.state.cv_model = CVModel(
        weights_path=os.getenv("MODEL_WEIGHTS_PATH", "models/weights/efficientnet_chestxray.pth"),
        modality="chest_xray",
    )

    # ── Skin Lesion Vision Model ──────────────────────────────────────────────
    logger.info("Loading Skin Lesion Vision Model...")
    app.state.skin_model = CVModel(
        weights_path=os.getenv("SKIN_MODEL_WEIGHTS_PATH", "models/weights/vit_skin.pth"),
        modality="skin",
    )

    # ── Retinal / Eye Disease Vision Model ────────────────────────────────────
    logger.info("Loading Retinal Eye Disease Vision Model...")
    app.state.retina_model = CVModel(
        weights_path=os.getenv("RETINA_MODEL_WEIGHTS_PATH", "models/weights/vit_retina.pth"),
        modality="retina",
    )

    # ── NLP Model ─────────────────────────────────────────────────────────────
    logger.info("Loading NLP model...")
    app.state.nlp_model = NLPModel()

    # ── FAISS Vector Store ────────────────────────────────────────────────────
    logger.info("Loading FAISS vector store...")
    app.state.vectorstore = VectorStore(
        index_path=os.getenv("FAISS_INDEX_PATH", "rag/faiss_medical_index")
    )

    # ── LLM Report Generator ──────────────────────────────────────────────────
    logger.info("Initializing LLM report generator...")
    app.state.report_generator = ReportGenerator(
        google_api_key=google_api_key,
        openai_api_key=openai_api_key,
    )

    # ── Q&A Chain ─────────────────────────────────────────────────────────────
    logger.info("Initializing Q&A chain...")
    app.state.qa_chain = QAChain(
        google_api_key=google_api_key,
        openai_api_key=openai_api_key,
    )

    logger.info("✅ All components loaded. API is ready.")
    yield

    logger.info("🛑 Shutting down API...")


# ── FastAPI App ───────────────────────────────────────────────────────────────
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from utils.security import limiter

app = FastAPI(
    title="MedAI Medical Diagnosis API",
    description=(
        "Multimodal medical image analysis + NLP symptom extraction + "
        "LLM-powered diagnostic report generation. "
        "Supports Chest X-Ray, Skin Lesion, and Retinal imaging modalities."
    ),
    version="2.0.0",
    lifespan=lifespan,
    # Disable /docs and /redoc in production unless DEBUG=true
    docs_url="/docs" if os.getenv("DEBUG", "false").lower() == "true" else None,
    redoc_url="/redoc" if os.getenv("DEBUG", "false").lower() == "true" else None,
    openapi_url="/openapi.json" if os.getenv("DEBUG", "false").lower() == "true" else None,
)

# 1. ── Trusted Host (prevents Host header injection) ─────────────────────────
_trusted_hosts_raw = os.getenv("TRUSTED_HOSTS", "*")
if _trusted_hosts_raw != "*":
    trusted_hosts = [h.strip() for h in _trusted_hosts_raw.split(",") if h.strip()]
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

# 2. ── Security Headers ───────────────────────────────────────────────────────
app.add_middleware(SecurityHeadersMiddleware)

# 3. ── Request Tracing ────────────────────────────────────────────────────────
app.add_middleware(RequestTracingMiddleware)

# 4. ── Anti-DDoS Rate Limiter ─────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# 5. ── CORS — strict, domain-driven ──────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
    max_age=600,  # preflight cache 10 minutes
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
async def root():
    return {"status": "MedAI API is running", "version": "2.0.0", "docs": "/docs (debug mode only)"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true",
        workers=1,  # 1 worker since we have in-memory models
        log_level=LOG_LEVEL.lower(),
        access_log=True,
        proxy_headers=True,        # Trust X-Forwarded-For from Render/Vercel proxies
        forwarded_allow_ips="*",   # All IPs when behind a reverse proxy
    )
