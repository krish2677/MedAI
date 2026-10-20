"""
keep_alive.py — Anti-sleep sentinel for Render free tier.

Render free services spin down after 15 minutes of inactivity.
This script pings the health endpoint every 10 minutes to keep it awake.

Usage (run this locally or on a separate free cron service like cron-job.org):
  python keep_alive.py

Or deploy it to a free cron hosting service and point it at your Render URL.
# Tip: Use https://cron-job.org (free) to run a GET request every 10 minutes
#      → URL: https://medai-api-tivz.onrender.com/api/v1/health
"""

import time
import logging
import os
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
HEALTH_URL   = os.getenv(
    "RENDER_HEALTH_URL",
    "https://medai-api-tivz.onrender.com/api/v1/health",
)
PING_INTERVAL = int(os.getenv("PING_INTERVAL_SECONDS", "600"))  # 10 minutes
REQUEST_TIMEOUT = 30  # seconds


def ping() -> bool:
    """Ping the health endpoint. Returns True if successful."""
    try:
        res = requests.get(HEALTH_URL, timeout=REQUEST_TIMEOUT)
        res.raise_for_status()
        data = res.json()
        logger.info(f"✅ Server awake — status={data.get('status')} version={data.get('version')}")
        return True
    except requests.exceptions.Timeout:
        logger.warning("⏱️  Ping timed out — server may be waking up (cold start).")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"❌ Connection error: {e}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"❌ HTTP error {e.response.status_code}: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
    return False


def keep_awake():
    """Infinite loop — ping server every PING_INTERVAL seconds."""
    logger.info(f"🛡️  Anti-Sleep Sentinel activated. Pinging every {PING_INTERVAL}s → {HEALTH_URL}")
    consecutive_failures = 0

    while True:
        success = ping()
        if success:
            consecutive_failures = 0
        else:
            consecutive_failures += 1
            if consecutive_failures >= 5:
                logger.critical(
                    f"🚨 Server has been unreachable for {consecutive_failures} consecutive pings. "
                    "Check your Render deployment."
                )

        time.sleep(PING_INTERVAL)


if __name__ == "__main__":
    keep_awake()
