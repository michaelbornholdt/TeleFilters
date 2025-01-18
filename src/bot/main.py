import json
import logging
import typing as t

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: t.Dict, context: t.Dict) -> t.Dict:
    logger.info(f"Event: {json.dumps(event)}")

    chat_id = event["message"]["chat"]["id"]
    user_name = event["message"]["from"]["username"]
    message_text = event["message"]["text"]

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": f"Received message from {user_name} in chat {chat_id}: {message_text}"
            }
        ),
    }
