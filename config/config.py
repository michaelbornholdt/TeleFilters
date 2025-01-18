import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = DATA_DIR / "output.json"

# Telegram Configuration
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE")
SESSION_NAME = "telegram_filter_bot"  # This will create a session file in the data directory

# Verify environment variables are loaded
if not all([TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE]):
    raise ValueError(
        "Missing required environment variables. "
        "Please check your .env file contains TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_PHONE"
    )

# Convert API_ID to int as Telethon requires it
TELEGRAM_API_ID = int(TELEGRAM_API_ID)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o"
OPENAI_TEMPERATURE = 0.0

# Analysis Configuration
RELEVANT_CATEGORIES = [
    "event",
    "request",
    "offer"
]

IRRELEVANT_TOPICS = [
    "flat_shares",
    "job_offers",
    "Announcements that are not events, requests or offers",
    "introductions"
]

# Time Configuration
DEFAULT_DAYS_TO_FETCH = 1