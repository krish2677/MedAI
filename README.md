# 🧬 MedAI: AI-Powered Medical Diagnosis Assistant

![MedAI Banner](https://img.shields.io/badge/Status-Production_Ready-success?style=for-the-badge) ![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi) ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white) 

MedAI is a comprehensive, full-stack, multimodal artificial intelligence platform designed to assist healthcare professionals by analyzing medical imagery, processing patient symptoms, and generating highly structured, explainable clinical reports.

## ✨ Core Features

*   **Multimodal Image Analysis:** Utilizes sophisticated Hugging Face `EfficientNet` architectures to rapidly classify Chest X-rays, Skin Lesions, and Retinal Scans.
*   **Explainable AI (Grad-CAM):** We don't just give a black-box diagnosis. MedAI generates overlay heatmaps on patient scans, visually highlighting exactly which biological areas triggered the AI's classification so human doctors can trust the output.
*   **LLM Clinical Synthesis:** Fuses the AI's raw image analysis with the patient's self-reported text/voice symptoms. It routes this data through advanced Large Language Models (supporting Groq, Gemini, or ChatGPT) to print a professional medical report.
*   **Conversational Triage Chat (RAG):** Features a memory-augmented FAISS Vector Database, allowing users to interactively chat with their medical report and ask follow-up questions about their diagnosis.
*   **Voice-to-Text Dictation:** Integrates the browser's native SpeechRecognition API, allowing patients or doctors to speak their symptoms effortlessly.
*   **Specialist Locator:** Automatically maps the pathology findings to recommend the correct medical specialist (e.g., Dermatologist, Pulmonologist) and links directly to localized Google Maps searches.
*   **Progressive Web App (PWA):** Fully installable natively on iOS, Android, and Desktop environments directly from the browser for a native application feel.
*   **Hyper-Secure Architecture:** Hardened backend using `slowapi` rate limiting (to prevent DDoS), extremely strict CORS origins, rapid MIME-type file sanitization, and 100% ephemeral processing where absolutely zero patient data is permanently saved to any hard drive.

## 🛠️ Technology Stack

**Frontend (Client)**
*   **Framework:** React (+ Vite)
*   **Styling:** Tailwind CSS
*   **Animations:** Framer Motion (3D spatial transitions) & AOS (Scroll animations)
*   **Icons:** Lucide React
*   **PWA:** `vite-plugin-pwa` Service Workers

**Backend (API Server)**
*   **Framework:** FastAPI (Python)
*   **Machine Learning:** PyTorch (CPU-optimized for edge clouds), OpenCV, Hugging Face `transformers`
*   **Vector Database:** FAISS (Facebook AI Similarity Search)
*   **LLM Orchestration:** LangChain
*   **Security:** `slowapi` (Rate limiter), `python-multipart`

## 🚀 How It Works (The Pipeline)

1.  **Ingestion:** The user uploads a medical scan and optionally types or speaks their current symptoms into the dynamic React interface.
2.  **Validation & Sanitization:** The FastAPI backend intercepts the file, strictly validates its MIME type, and holds the image securely in temporary RAM to ensure zero HIPAA/Privacy violations.
3.  **Inference:** The PyTorch models classify the pathology (e.g., "Pneumonia Detected" or "Benign Nevus") with a confidence score.
4.  **Explainability:** The Grad-CAM generator recalculates the neural network gradients to produce a thermal heatmap outlining the disease location, which is encoded in Base64.
5.  **Synthesis:** A specialized LangChain prompt forces an LLM to read the AI's findings alongside the patient's symptoms, orchestrating a structured "Doctor's Report" (Findings, Assessment, Plan).
6.  **Delivery:** The React frontend beautifully renders the synthesized report, displays the heatmap, mounts the interactive RAG chat module, and generates local specialist referrals.

## 💻 Local Development (Quickstart)

Because MedAI relies on a complex ML architecture, the project is cleanly split into two asynchronous environments.

### 1. Start the API (Backend)
```bash
cd backend
python -m venv venv
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. Start the User Interface (Frontend)
```bash
cd frontend
npm install
npm run dev
```

*Note: Ensure your `backend/.env` file is populated with your preferred LLM API keys (`GROQ_API_KEY`, `GOOGLE_API_KEY`, etc.) before spinning up the server.*

## ☁️ Cloud Deployment Architecture

MedAI is constructed with "Always-Awake" Infrastructure-as-Code (IaC), allowing it to side-step heavy ML server freezing.
*   **Frontend `vercel.json`:** Ready out-of-the-box for global edge deployment on Vercel.
*   **Backend `render.yaml` & `Dockerfile`:** Containerizes the massive PyTorch environment into a slim Debian wrapper for Render or Railway cloud computing.
*   **Keep-Alive Daemon:** Includes a `keep_alive.py` ping script to eternally bypass free-tier API sleeping mechanics.
