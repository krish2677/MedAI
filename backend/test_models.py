import os
from dotenv import load_dotenv

load_dotenv()
google_key = os.getenv("GOOGLE_API_KEY")

if not google_key or google_key == "your_google_gemini_api_key_here":
    print("NO VALID GOOGLE KEY FOUND!")
    exit(1)

try:
    import google.generativeai as genai
    genai.configure(api_key=google_key)
    print("Supported models for this key:")
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f"Error listing models: {e}")
