# AI Medical Diagnosis Assistant

![MedAI Banner Placeholder](https://via.placeholder.com/1200x400?text=MedAI+Diagnosis+Dashboard)

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.3-ee4c2c.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

A full-stack, multimodal AI-powered Medical Diagnosis Assistant web application. The system analyzes medical images (like Chest X-Rays) and patient symptoms to output a structured diagnostic report with confidence scores, a visual heatmap (Grad-CAM), and an LLM-generated clinical summary grounded in medical literature (RAG).

## Features

- ✅ **Image Upload & CV Inference:** Fine-tuned `EfficientNet-B4` CNN classifications.
- ✅ **Grad-CAM Visualizations:** Explainable AI overlays isolating regions of focus.
- ✅ **NLP Symptom Mapping:** Extracts medical entities using BioBERT.
- ✅ **Multimodal Fusion Engine:** Weighted ensemble of visual and text predictions.
- ✅ **RAG-Powered LLM Reports:** Gemini 1.5/GPT-4o text generation grounded in FAISS vector store.
- ✅ **Conversational Follow-up Q&A:** Ask your AI assistant about the diagnosis context.
- ✅ **Urgency Classification:** Automated triaging (LOW, MODERATE, HIGH).

## Tech Stack

| Domain | Technology |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, Recharts |
| **Backend API** | FastAPI, Python 3.11 |
| **CV / Vision** | PyTorch, `EfficientNet-B4`, Torchvision |
| **Explainable AI** | `pytorch-grad-cam` |
| **NLP** | HuggingFace Transformers, `dmis-lab/biobert-v1.1` |
| **LLM & RAG** | LangChain, FAISS, `sentence-transformers`, Gemini 1.5 Flash |

## Datasets

- **Primary (Chest X-Ray):** [NIH ChestX-ray14](https://nihcc.app.box.com/v/ChestXray-NIHCC)
- **Secondary (optional):** ISIC 2019 Skin Lesions
- **NLP Symptoms:** DDXPlus Dataset

## Installation & Deployment

### Run via Docker Compose (Recommended)

1. Clone the repository and navigate to the directory:
   ```bash
   git clone https://github.com/your-repo/ai-medical-diagnosis.git
   cd ai-medical-diagnosis
   ```
2. Set your `.env` File in the `backend/` folder:
   ```env
   GOOGLE_API_KEY=your_gemini_key
   OPENAI_API_KEY=optional_openai_key
   ```
3. Run with Docker Compose:
   ```bash
   docker-compose up --build
   ```
   * The Frontend will be available at `http://localhost:3000`.
   * The Backend API docs at `http://localhost:8000/docs`.

## Benchmarks & Evaluation Targets

| Metric | Target Value |
|--------|-------|
| AUC-ROC (Chest X-Ray) | > 0.82 |
| Sensitivity (Recall) | > 0.75 |
| Specificity | > 0.85 |
| F1 Score (Macro) | > 0.72 |
| Inference Time | ~1.4s (CPU) |

## Contributing
We welcome contributions. Please review our safety guidelines when contributing to the medical prompts and models. Ensure guardrails are not bypassed during PRs.

## Disclaimer
⚠️ **MEDICAL AI SAFETY WARNING:** This system is built for research and demonstration purposes. It is **NOT** a substitute for professional medical advice, diagnosis, or treatment. The LLM guardrails actively prevent the prescription of medication or definitive diagnosis.

## License
MIT License
