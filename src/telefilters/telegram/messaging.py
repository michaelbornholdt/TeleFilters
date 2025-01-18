import logging
import os
import json
import requests
logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

def sendReply(bot_token, chat_id, message):
    reply = {
        "chat_id": chat_id,
        "text": message
    }

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    encoded_data = json.dumps(reply).encode('utf-8')
    requests.post(url, json=reply, headers={'Content-Type': 'application/json'})
    
    print(f"*** Reply : {encoded_data}")


def send_telegram_message(bot, chat_id: int, message: str) -> None:
    """Send a message to the specified Telegram chat."""
    logger.debug(f"Sending message to chat {chat_id}")

    try:
        bot.send_message(PeerUser(user_id=chat_id), message)
        logger.info(f"Message sent successfully to chat {chat_id}")
    except Exception as e:
        logger.error(f"Failed to send message to chat {chat_id}: {str(e)}")
        raise
