import json
import logging
import os

import requests

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


def sendReply(bot_token, chat_id, message):
    reply = {"chat_id": chat_id, "text": message}

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    encoded_data = json.dumps(reply).encode("utf-8")
    requests.post(url, json=reply, headers={"Content-Type": "application/json"})

    print(f"*** Reply : {encoded_data}")
