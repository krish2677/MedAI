import os
import logging
from typing import List
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

REPORT_PROMPT_TEMPLATE = """You are a medical AI assistant generating a structured diagnostic report.
You have access to the following relevant medical literature:

{retrieved_context}

Based on:
- Patient-reported symptoms: {symptoms}
- AI-predicted conditions (ranked by confidence): 
{diagnosis_list}

Generate a structured clinical report with the following sections:

## 1. Summary
A 2-3 sentence plain English overview of the diagnostic findings.

## 2. Top Predicted Conditions
A brief, accurate description of each predicted condition and its clinical significance.

## 3. What This Means
Explain the findings in accessible layperson terms, what they might indicate, and what could have caused them.

## 4. Recommended Next Steps
Specify what type of specialist to consult (e.g., pulmonologist, cardiologist, dermatologist), and what diagnostic tests might be ordered (e.g., CT scan, biopsy, blood panel).

## 5. Urgency Assessment
One of: IMMEDIATE attention (go to emergency room now), URGENT (see a doctor within 24-48 hours), ROUTINE (schedule an appointment within 1-2 weeks), or LOW (monitor symptoms, consult if worsening).

---

CRITICAL RULES:
- Never prescribe specific medications, dosages, or treatments.
- Never state definitively "you have X" — use probabilistic language: "findings suggest", "may indicate", "consistent with".
- Be compassionate and clear, avoiding unnecessary medical jargon.
- Always end your report with this exact disclaimer on its own line:
  ⚠️ DISCLAIMER: This AI-generated report is for informational purposes only and is NOT a substitute for professional medical diagnosis, advice, or treatment. Always consult a qualified healthcare provider.

Report:"""

SAFETY_DISCLAIMER = (
    "⚠️ DISCLAIMER: This AI-generated report is for informational purposes only and is NOT "
    "a substitute for professional medical diagnosis, advice, or treatment. "
    "Always consult a qualified healthcare provider."
)


class ReportGenerator:
    def __init__(self, google_api_key: str = None, openai_api_key: str = None):
        self.llm = self._init_llm(google_api_key, openai_api_key)

    def _init_llm(self, google_api_key: str = None, openai_api_key: str = None):
        """Initialize LLM with Groq as primary, Gemini Flash as secondary, GPT-4o-mini as fallback."""
        groq_key = os.getenv("GROQ_API_KEY")
        google_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        if groq_key and groq_key != "your_groq_api_key_here":
            try:
                from langchain_groq import ChatGroq
                logger.info("Using Groq Llama 3 (70B) for report generation.")
                return ChatGroq(
                    model="llama-3.3-70b-versatile",
                    groq_api_key=groq_key,
                    temperature=0.3,
                )
            except Exception as e:
                logger.warning(f"Groq init failed: {e}")

        if google_key and google_key != "your_google_gemini_api_key_here":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                logger.info("Using Google Gemini for report generation.")
                return ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                    google_api_key=google_key,
                    temperature=0.3,
                )
            except Exception as e:
                logger.warning(f"Gemini init failed: {e}")

        if openai_key and openai_key != "your_openai_api_key_here":
            try:
                from langchain_openai import ChatOpenAI
                logger.info("Using OpenAI GPT-4o-mini for report generation.")
                return ChatOpenAI(
                    model="gpt-4o-mini",
                    openai_api_key=openai_key,
                    temperature=0.3,
                )
            except Exception as e:
                logger.warning(f"OpenAI init failed: {e}")

        logger.warning("No LLM API keys configured. Using template-based report generation.")
        return None

    def generate(
        self,
        diagnosis_list: list,
        symptoms: str,
        retrieved_context: List[str],
    ) -> str:
        context_str = "\n\n".join(retrieved_context) if retrieved_context else "No context available."
        diag_str = "\n".join([
            f"  - {d['condition']}: {d['final_score'] * 100:.1f}% confidence"
            for d in diagnosis_list
        ])

        if self.llm is not None:
            try:
                prompt = REPORT_PROMPT_TEMPLATE.format(
                    retrieved_context=context_str,
                    symptoms=symptoms,
                    diagnosis_list=diag_str,
                )
                response = self.llm.invoke(prompt)
                report = response.content if hasattr(response, "content") else str(response)
                if SAFETY_DISCLAIMER not in report:
                    report += f"\n\n{SAFETY_DISCLAIMER}"
                return report
            except Exception as e:
                logger.error(f"LLM report generation failed: {e}")

        # Fallback: structured template report
        return self._template_report(diagnosis_list, symptoms)

    def _template_report(self, diagnosis_list: list, symptoms: str) -> str:
        top = diagnosis_list[0] if diagnosis_list else {"condition": "Unknown", "final_score": 0}
        others = diagnosis_list[1:4]

        report = f"""## 1. Summary
Based on the uploaded medical image and reported symptoms ("{symptoms}"), the AI analysis suggests findings most consistent with **{top['condition']}** ({top['final_score']*100:.1f}% confidence). This is supplemented by additional differential diagnoses from both visual and clinical data analysis.

## 2. Top Predicted Conditions
- **{top['condition']}** ({top['final_score']*100:.1f}%): This condition was identified as the primary finding based on image and symptom correlation.
{chr(10).join([f"- **{d['condition']}** ({d['final_score']*100:.1f}%): Secondary consideration based on pattern analysis." for d in others])}

## 3. What This Means
The AI system detected patterns in your medical image and symptoms that are associated with the conditions listed above. These findings require professional medical evaluation to confirm. The results should be interpreted alongside your complete medical history and physical examination.

## 4. Recommended Next Steps
- Schedule an appointment with your primary care physician as soon as possible.
- Bring this report and your original medical images to your appointment.
- Depending on the findings, you may be referred to a specialist (e.g., pulmonologist, radiologist, or dermatologist).
- Additional tests such as blood work, CT scan, or biopsy may be recommended.

## 5. Urgency Assessment
Based on the predicted conditions and confidence levels, please consult a healthcare provider promptly. If you experience severe symptoms such as difficulty breathing, chest pain, or sudden deterioration, seek emergency care immediately.

---

{SAFETY_DISCLAIMER}"""
        return report

    @property
    def is_loaded(self) -> bool:
        return True  # Always "loaded" because fallback is available
