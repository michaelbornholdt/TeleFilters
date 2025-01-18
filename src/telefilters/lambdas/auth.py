import json
import logging
import os

import boto3
from telethon.sessions import StringSession
from telethon.sync import TelegramClient

from openai import OpenAI

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

client = boto3.client("secretsmanager")


def get_telegram_client(user_id: str):
    """Authenticate with Telegram API and return client"""

    secret_name = os.environ["BOT_SECRET"]
    response = client.get_secret_value(SecretId=secret_name)
    secret_value = json.loads(response.get("SecretString"))

    logger.info(f"Retrieved the secrets: {secret_value}")

    user_secrets = secret_value.get("users").get(str(user_id))
    logger.info(f"Retrieved the secrets: {user_secrets}")

    api_id = user_secrets.get("telegram_api_id")
    logger.info(f"Retrieved the secret api_id: {api_id}")
    api_hash = user_secrets.get("telegram_api_hash")

    bot_token = secret_value.get("bot_token")

    with TelegramClient(StringSession(), api_id, api_hash) as telegram_client:
        string = telegram_client.session.save()

    return string, api_id, api_hash, bot_token


def get_openai_client():
    """Authenticate with OpenAI API and return client"""

    secret_name = os.environ["OPENAI_SECRET"]
    response = client.get_secret_value(SecretId=secret_name)
    secret_value = json.loads(response.get("SecretString"))
    logger.info("Authenticating with OpenAI API")

    openai_client = OpenAI(api_key=secret_value.get("openai_api_key"))
    return openai_client
