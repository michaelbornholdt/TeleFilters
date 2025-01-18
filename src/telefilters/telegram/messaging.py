import logging

from telegram import Bot
from telegram.error import TelegramError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


async def send_telegram_message(bot: Bot, chat_id: int, message: str) -> None:
    """Send a message to the specified Telegram chat."""
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        logger.info(f"Message sent successfully to chat {chat_id}")
    except TelegramError as e:
        logger.error(f"Failed to send message to chat {chat_id}: {str(e)}")
        raise
