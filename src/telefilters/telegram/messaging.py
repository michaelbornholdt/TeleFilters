import logging
import os

import aiohttp

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


async def sendReply(bot_token: str, chat_id: int, message: str):
    """Async version of sendReply using aiohttp"""
    reply = {"chat_id": chat_id, "text": message}
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=reply) as response:
            await response.json()
            logger.info(f"Sent reply: {message}")
