import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from models.cv_model import CVModel
from models.nlp_model import NLPModel
from rag.vectorstore import VectorStore
from llm.report_generator import ReportGenerator
from llm.qa_chain import QAChain

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s — %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load all models and resources at startup."""
    logger.info("🚀 Starting AI Medical Diagnosis API...")

    google_api_key = os.getenv("GOOGLE_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    logger.info("Loading EfficientNet-B4 CV model...")
    app.state.cv_model = CVModel(
        weights_path=os.getenv("MODEL_WEIGHTS_PATH", "models/weights/efficientnet_chestxray.pth"),
        modality="chest_xray"
    )

    logger.info("Loading Skin Lesion CV model...")
    app.state.skin_model = CVModel(
        weights_path=os.getenv("SKIN_MODEL_WEIGHTS_PATH", "models/weights/efficientnet_skin.pth"),
        modality="skin"
    )

    logger.info("Loading Retina CV model...")
    app.state.retina_model = CVModel(
        weights_path=os.getenv("RETINA_MODEL_WEIGHTS_PATH", "models/weights/efficientnet_retina.pth"),
        modality="retina"
    )

    logger.info("Loading NLP model...")
    app.state.nlp_model = NLPModel()

    logger.info("Loading FAISS vector store...")
    app.state.vectorstore = VectorStore(
        index_path=os.getenv("FAISS_INDEX_PATH", "rag/faiss_medical_index")
    )

    logger.info("Initializing LLM report generator...")
    app.state.report_generator = ReportGenerator(
        google_api_key=google_api_key,
        openai_api_key=openai_api_key,
    )

    logger.info("Initializing Q&A chain...")
    app.state.qa_chain = QAChain(
        google_api_key=google_api_key,
        openai_api_key=openai_api_key,
    )

    logger.info("✅ All components loaded. API is ready.")
    yield

    logger.info("🛑 Shutting down API...")


from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from utils.security import limiter

# ...

app = FastAPI(
    title="AI Medical Diagnosis API",
    description=(
        "Multimodal medical image analysis + NLP symptom extraction + "
        "LLM-powered diagnostic report generation."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# 1. Anti-DDoS Setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# 2. Strict CORS Policies (No wildcard domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://medai-production-url.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
