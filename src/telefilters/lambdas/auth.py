import json

import fsspec
from telethon.sync import TelegramClient

from openai import OpenAI


def get_telegram_client():
    """Authenticate with Telegram API and return client"""

    with fsspec.open(
        "s3://infrastructurestack-userdata6a2e227b-jjxpj68kosc9/users/14242555/config.json"
    ) as f:
        auth_cfg = json.load(f)

    api_id = auth_cfg["TELEGRAM_API_ID"]
    api_hash = auth_cfg["TELEGRAM_API_HASH"]

    telegram_client = TelegramClient(
        str("session_path"),  # Convert Path to string for Telethon
        api_id=api_id,
        api_hash=api_hash,
    )

    return telegram_client


def get_openai_client():
    """Authenticate with OpenAI API and return client"""

    with fsspec.open(
        "s3://infrastructurestack-userdata6a2e227b-jjxpj68kosc9/openai/openai.json"
    ) as f:
        auth_cfg = json.load(f)
        openai_api_key = auth_cfg["OPENAI_API_KEY"]

    openai_client = OpenAI(api_key=openai_api_key)
    return openai_client
