import logging
import os
from telethon.tl.types import PeerUser
logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


def send_telegram_message(bot, chat_id: int, message: str) -> None:
    """Send a message to the specified Telegram chat."""
    logger.debug(f"Sending message to chat {chat_id}")

    try:
        bot.send_message(PeerUser(user_id=chat_id), message)
        logger.info(f"Message sent successfully to chat {chat_id}")
    except Exception as e:
        logger.error(f"Failed to send message to chat {chat_id}: {str(e)}")
        raise
