import json
import logging
import os

import boto3
from telethon.sync import TelegramClient

from openai import OpenAI

client = boto3.client("secretsmanager")
logger = logging.getLogger(__name__)


def get_telegram_client(user_id: str):
    """Authenticate with Telegram API and return client"""

    secret_name = os.environ["BOT_SECRET"]
    response = client.get_secret_value(SecretId=secret_name)
    secret_value = json.loads(response.get("SecretString"))
    logger.info("Authenticating with Telegram API")

    user_secrets = secret_value.get("users").get(user_id)
    
    api_id = user_secrets.get("telegram_api_id")
    api_hash = user_secrets.get("telegram_api_hash")

    telegram_client = TelegramClient(
        str("session_path"),  # Convert Path to string for Telethon
        api_id=api_id,
        api_hash=api_hash,
    )

    return telegram_client


def get_openai_client():
    """Authenticate with OpenAI API and return client"""

    secret_name = os.environ["OPENAI_SECRET"]
    response = client.get_secret_value(SecretId=secret_name)
    secret_value = json.loads(response.get("SecretString"))
    logger.info("Authenticating with OpenAI API")

    openai_client = OpenAI(api_key=secret_value.get("openai_api_key"))
    return openai_client
