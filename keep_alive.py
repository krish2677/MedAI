import time
import requests
import threading
import os

# Insert your actual deployed Render URL here once you deploy it
RENDER_URL = "https://medai-backend.onrender.com/api/v1/health"

def keep_awake():
    """
    Infinite loop to casually ping the backend server every 10 minutes.
    This entirely bypasses the 'Spun Down 15 minute' idle limit on free hosting tiers,
    so your ML models never unload from RAM and your frontend is always instantly fast!
    """
    print("🛡️ Anti-Sleep Sentinel activated. Pinging every 10 minutes.")
    while True:
        try:
            res = requests.get(RENDER_URL)
            print(f"[{time.strftime('%X')}] Pinged Server. Status: {res.status_code}")
        except Exception as e:
            print(f"[{time.strftime('%X')}] Ping failed: {e}")
        time.sleep(600)  # 10 minutes = 600 seconds

if __name__ == "__main__":
    keep_awake()
