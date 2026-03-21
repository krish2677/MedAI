import os
import requests
from dotenv import load_dotenv

load_dotenv()
google_key = os.getenv("GOOGLE_API_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={google_key}"
try:
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        with open("models.txt", "w") as f:
            for model in data.get("models", []):
                if "generateContent" in model.get("supportedGenerationMethods", []):
                    f.write(f"{model.get('name')}\n")
    else:
        with open("models.txt", "w") as f:
            f.write(f"Failed: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
