import os
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class VectorStore:
    """
    FAISS-backed vector store for medical literature retrieval.
    Falls back to curated static snippets when no index is available.
    """

    FALLBACK_DOCUMENTS = [
        "Pneumonia is an infection that inflames air sacs in one or both lungs, which may fill with fluid. Symptoms include cough, fever, chills, and difficulty breathing. Treatment typically involves antibiotics for bacterial pneumonia.",
        "Atelectasis is a complete or partial collapse of the entire lung or area (lobe) of the lung. It occurs when the tiny air sacs (alveoli) within the lung become deflated or possibly filled with alveolar fluid.",
        "Pulmonary edema is a condition caused by excess fluid in the lungs, making breathing difficult. Most cases are caused by heart problems. Quick treatment is essential to prevent life-threatening complications.",
        "Pneumothorax is a collapsed lung. It occurs when air leaks into the space between your lung and chest wall. This air pushes on the outside of your lung and makes it collapse. Treatment depends on the cause and severity.",
        "Emphysema is a lung condition that causes shortness of breath. In people with emphysema, the air sacs in the lungs (alveoli) are damaged. Over time, the inner walls of the air sacs weaken and rupture.",
        "Cardiomegaly refers to an enlarged heart. It is not a disease itself, but a sign of another condition. Causes include coronary artery disease, high blood pressure, viral infections, or complications during pregnancy.",
        "Pleural effusion is excess fluid that accumulates in the pleural cavity, the fluid-filled space between the lungs and the chest wall. Symptoms include chest pain and shortness of breath.",
        "Melanoma is the most serious type of skin cancer because it can spread to other parts of the body. It develops in the cells that give skin its color. Most melanomas are caused by overexposure to UV light.",
        "Diabetic retinopathy is a diabetes complication that affects eyes. It's caused by damage to the blood vessels of the light-sensitive tissue at the back of the eye (retina). Treatment may include laser surgery or injections.",
        "Chest X-rays can detect many conditions including pneumonia, heart failure, emphysema, lung cancer, and pneumothorax. The imaging shows differences in how X-rays are absorbed by different tissues in the chest.",
        "Arterial blood gas analysis is used to measure the pH, partial pressure of oxygen, and carbon dioxide in arterial blood. It helps assess how well the lungs are delivering oxygen to blood and removing carbon dioxide.",
        "Spirometry is used to assess lung health and diagnose conditions such as asthma and COPD. It measures how much air you can breathe in and out of your lungs and how quickly you can exhale.",
    ]

    def __init__(self, index_path: str = "rag/faiss_medical_index"):
        self.db = None
        self._load_index(index_path)

    def _load_index(self, index_path: str):
        try:
            from langchain_community.vectorstores import FAISS
            from langchain_community.embeddings import HuggingFaceEmbeddings

            faiss_file = os.path.join(index_path, "index.faiss")
            if os.path.isfile(faiss_file):
                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )
                self.db = FAISS.load_local(
                    index_path,
                    embeddings,
                    allow_dangerous_deserialization=True,
                )
                logger.info(f"Loaded FAISS index from {index_path}")
            else:
                logger.info(
                    f"No FAISS index file found at '{faiss_file}'. "
                    "Using high-speed curated fallback medical documents (RAM-optimized)."
                )
        except Exception as e:
            logger.warning(f"FAISS load error: {e}. Using fallback documents.")

    def query(self, query_text: str, k: int = 4) -> List[str]:
        """Retrieve top-k relevant medical context chunks."""
        if self.db is not None:
            try:
                docs = self.db.similarity_search(query_text, k=k)
                return [doc.page_content for doc in docs]
            except Exception as e:
                logger.error(f"FAISS query failed: {e}")

        # Fallback: keyword-based selection from static documents
        query_lower = query_text.lower()
        scored = []
        for doc in self.FALLBACK_DOCUMENTS:
            score = sum(1 for word in query_lower.split() if word in doc.lower())
            scored.append((score, doc))
        scored.sort(reverse=True, key=lambda x: x[0])
        return [doc for _, doc in scored[:k]]

    @property
    def is_loaded(self) -> bool:
        return self.db is not None
