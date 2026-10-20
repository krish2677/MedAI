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
    """
    Production-grade fast startup:
    Binds HTTP port 8000 instantly (<1s) to satisfy cloud health scanners (Render/AWS/GCP),
    while lazy-loading heavy vision and NLP models on demand to conserve RAM (<512MB).
    """
    logger.info("🚀 Starting MedAI API (Instant Cloud-Ready Boot Mode)...")

    # In-memory model cache for lazy loading
    app.state.models = {}
    app.state.nlp_model = None
    app.state.vectorstore = None

    google_api_key = os.getenv("GOOGLE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # ── LLM Report Generator & Q&A Chain (Lightweight initialization) ───────────
    try:
        logger.info("Initializing LLM report generator and QA chain...")
        app.state.report_generator = ReportGenerator(
            google_api_key=google_api_key,
            openai_api_key=openai_api_key,
        )
        app.state.qa_chain = QAChain(
            google_api_key=google_api_key,
            openai_api_key=openai_api_key,
        )
    except Exception as e:
        logger.warning(f"LLM initialization warning: {e}")

    logger.info("✅ Core services initialized. Server listening on port 8000.")
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

# 5. ── CORS — strict, domain-driven with automatic Vercel preview support ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
    max_age=600,  # preflight cache 10 minutes
)

from fastapi.responses import JSONResponse

# ── Global Exception Handler (Ensures CORS headers are always returned on 500) ───
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
        headers={"Access-Control-Allow-Origin": "*"}
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
