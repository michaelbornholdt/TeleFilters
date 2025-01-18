import os
import json
import boto3
import logging
import typing as t

from bot import auth

logging.basicConfig(level = logging.INFO)
# Retrieve the logger instance
logger = logging.getLogger()

BUCKET_NAME = os.environ["BUCKET_NAME"]
BOT_SECRET = os.environ['BOT_SECRET']


def lambda_handler(event: t.Dict, context: t.Dict) -> t.Dict:
    
    # Retrieve the secret value
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=BOT_SECRET)
    bot_secret_data = json.loads(response.get('SecretString'))
    
    body = json.loads(event['body'])
    logger.info(f"Event: {json.dumps(body)}")

    chat_id = body["message"]["chat"]["id"]
    user_id = body["message"]["from"]["id"]
    user_name = body["message"]["from"]["username"]
    message_text = body["message"]["text"]

    if message_text.startswith("/summarize"):
        return summarize(message_text, user_id)
    else:
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": f"Uknown command message from {user_name} in chat {chat_id}: {message_text}"
                }
            ),
        }


def summarize(body: str, user_id: str) -> str:
    telegram_client = auth.get_telegram_client(user_id)
    openai_client = auth.get_openai_client()

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Authorization successful"}),
    }


# def auth(event: t.Dict, context: t.Dict) -> t.Dict:
#     logger.info(f"Event: {json.dumps(event)}")

#     from user_manager import UserManager

#     # read authorization token from s3
#     um = UserManager()

#     current_users = um.list_users()
#     logger.info(f"Current users: {current_users}")


#     return {
#         "statusCode": 200,
#         "body": json.dumps({"message": "Authorization successful"}),
#     }

if __name__ == "__main__":
    summarize("test")
