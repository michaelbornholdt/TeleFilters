from telethon import TelegramClient
import logging

logger = logging.getLogger(__name__)

async def get_me(client: TelegramClient) -> str:
    """Get the username of the authenticated user"""
    me = await client.get_me()
    username = me.username or me.first_name
    logger.debug(f"Authenticated as user: {username}")
    return username 