import json
import logging
import os

import boto3
from s3fs.core import S3FileSystem
from telethon.sessions import StringSession
from telethon.sync import TelegramClient
from telethon.types import User

from openai import OpenAI

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

client = boto3.client("secretsmanager")
fs = S3FileSystem()

def get_telegram_secrets():
    secret_name = os.environ["BOT_SECRET"]
    response = client.get_secret_value(SecretId=secret_name)
    secret_value = json.loads(response.get("SecretString"))

    bot_token = secret_value.get("bot_token")
    api_id = secret_value.get("telegram_api_id")
    api_hash = secret_value.get("telegram_api_hash")
    return bot_token, api_id, api_hash

def get_telegram_client(user_id: int):
    """Authenticate with Telegram API and return client"""
    
    bot_token, api_id, api_hash = get_telegram_secrets()

    bucket_path = os.environ["BUCKET_NAME"]
    session_path = f"{bucket_path}/sessions/1839661938.session"

    tel_client = None
    if fs.exists(session_path):
        logger.info(f"Session file exists at {session_path}")
        with fs.open(session_path, "r") as f:
            session_string = f.read()
            tel_client = TelegramClient(StringSession(session_string), api_id, api_hash)
            logger.info("Authenticated with Telegram API")
    else:
        logger.info(f"Session file does not exist at {session_path}")

    return tel_client, bot_token


def get_openai_client():
    """Authenticate with OpenAI API and return client"""

    secret_name = os.environ["OPENAI_SECRET"]
    response = client.get_secret_value(SecretId=secret_name)
    secret_value = json.loads(response.get("SecretString"))
    logger.info("Authenticating with OpenAI API")

    openai_client = OpenAI(api_key=secret_value.get("openai_api_key"))
    return openai_client
