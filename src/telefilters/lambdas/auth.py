import os
import json
import boto3
from telethon.sync import TelegramClient

from openai import OpenAI

client = boto3.client('secretsmanager')


def get_telegram_client():
    """Authenticate with Telegram API and return client"""

    secret_name = os.environ['BOT_SECRET']
    response = client.get_secret_value(SecretId=secret_name)
    secret_value = json.loads(response.get('SecretString'))

    api_id = secret_value.get("telegram_api_id")
    api_hash = secret_value.get("telegram_api_hash")

    telegram_client = TelegramClient(
        str("session_path"),  # Convert Path to string for Telethon
        api_id=api_id,
        api_hash=api_hash,
    )

    return telegram_client


def get_openai_client():
    """Authenticate with OpenAI API and return client"""

    secret_name = os.environ['OPENAI_SECRET']
    response = client.get_secret_value(SecretId=secret_name)
    secret_value = json.loads(response.get('SecretString'))

    openai_client = OpenAI(api_key=secret_value.get("openai_api_key"))
    return openai_client
