import os
from pathlib import Path
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent

# Telegram Configuration
TELEGRAM_API_ID = "26193299"
TELEGRAM_API_HASH = "74d2288924773750f264eaf282fa9a77"
TELEGRAM_PHONE = "+4915128743727"

# Verify environment variables are loaded
if not all([TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE]):
    raise ValueError(
        "Missing required environment variables. "
        "Please check your .env file contains TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_PHONE"
    )
