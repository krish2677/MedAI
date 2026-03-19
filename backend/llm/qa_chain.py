import os
import logging
from typing import List
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

QA_SYSTEM_PROMPT = """You are a compassionate medical AI assistant helping a patient understand their diagnostic results.

The patient's diagnostic context:
{diagnosis_context}

Your role:
- Answer follow-up questions about the diagnosis in clear, accessible language
- Explain medical terms when asked
- Provide general wellness and prevention information
- Guide the patient on when to seek immediate medical attention

STRICT RULES:
- Never prescribe medications or specific dosages
- Never definitively diagnose — use language like "findings suggest" or "may indicate"
- Always recommend consulting a qualified healthcare provider for medical decisions
- If asked about emergency symptoms, always advise seeking immediate care
- Be empathetic, clear, and avoid unnecessary alarm

Answer the user's question helpfully and compassionately."""

SAFETY_DISCLAIMER = "\n\n*Note: Always consult a qualified healthcare provider for medical advice.*"


class QAChain:
    """Conversational Q&A chain for patient follow-up questions."""

    def __init__(self, google_api_key: str = None, openai_api_key: str = None):
        self.llm = self._init_llm(google_api_key, openai_api_key)

    def _init_llm(self, google_api_key: str, openai_api_key: str):
        google_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        if google_key and google_key != "your_google_gemini_api_key_here":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                return ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=google_key,
                    temperature=0.5,
                )
            except Exception as e:
                logger.warning(f"Gemini QA init failed: {e}")

        if openai_key and openai_key != "your_openai_api_key_here":
            try:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model="gpt-4o-mini",
                    openai_api_key=openai_key,
                    temperature=0.5,
                )
            except Exception as e:
                logger.warning(f"OpenAI QA init failed: {e}")

        return None

    def chat(
        self,
        message: str,
        conversation_history: List[dict],
        diagnosis_context: str,
    ) -> tuple[str, List[dict]]:
        """
        Generate a response to the user's follow-up question.
        Returns (response_text, updated_history).
        """
        if self.llm is not None:
            try:
                from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

                messages = [
                    SystemMessage(content=QA_SYSTEM_PROMPT.format(
                        diagnosis_context=diagnosis_context
                    ))
                ]
                for turn in conversation_history[-10:]:  # Keep last 10 turns
                    if turn["role"] == "user":
                        messages.append(HumanMessage(content=turn["content"]))
                    elif turn["role"] == "assistant":
                        messages.append(AIMessage(content=turn["content"]))

                messages.append(HumanMessage(content=message))

                response = self.llm.invoke(messages)
                answer = response.content if hasattr(response, "content") else str(response)
                answer += SAFETY_DISCLAIMER

            except Exception as e:
                logger.error(f"QA chain failed: {e}")
                answer = self._fallback_response(message) + SAFETY_DISCLAIMER
        else:
            answer = self._fallback_response(message) + SAFETY_DISCLAIMER

        updated_history = conversation_history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": answer},
        ]
        return answer, updated_history

    def _fallback_response(self, message: str) -> str:
        message_lower = message.lower()

        if any(word in message_lower for word in ["emergency", "severe", "can't breathe", "chest pain"]):
            return (
                "This sounds potentially serious. If you are experiencing severe chest pain, "
                "difficulty breathing, or feel this is an emergency, please call emergency services "
                "(911 in the US) or go to the nearest emergency room immediately."
            )
        elif any(word in message_lower for word in ["mean", "what is", "explain", "define"]):
            return (
                "This is a great question to discuss with your healthcare provider. They can explain "
                "your specific results in the context of your complete medical history and examination. "
                "Based on the diagnostic findings, I recommend scheduling an appointment promptly."
            )
        elif any(word in message_lower for word in ["worried", "scared", "should i"]):
            return (
                "It's completely understandable to have concerns about your health. The most important "
                "step is to share these results with a qualified healthcare provider who can give you "
                "personalized guidance. Many conditions have effective treatments when caught early."
            )
        else:
            return (
                "Thank you for your question. For personalized medical advice specific to your situation, "
                "please consult with a qualified healthcare provider. They can interpret these AI findings "
                "in conjunction with your full medical history, physical examination, and additional tests."
            )
