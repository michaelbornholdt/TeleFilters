import os
import json
import boto3
import logging
import typing as t

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BUCKET_NAME = os.environ["BUCKET_NAME"]
BOT_SECRET = os.environ['BOT_SECRET']

def lambda_handler(event: t.Dict, context: t.Dict) -> t.Dict:
    
    # Retrieve the secret value
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=BOT_SECRET)
    bot_secret_data = json.loads(response.get('SecretString'))
    
    body = json.loads(event['body'])
    logger.info(f"Event: {json.dumps(event)}")

    chat_id = body["message"]["chat"]["id"]
    user_name = body["message"]["from"]["username"]
    message_text = body["message"]["text"]

    if message_text.startswith("/summarize"):
        return summarize(message_text)
    else:
        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": f"Uknown command message from {user_name} in chat {chat_id}: {message_text}"
                }
            ),
        }


def summarize(body: str) -> str:
    import fsspec
    from telethon.sync import TelegramClient

    # base_path: str = "s3://infrastructurestack-userdata6a2e227b-jjxpj68kosc9/users/",
    # cfg_dir: str = "/home/miha/TeleFilters/users/14242555",
    # read authorization token from s3
    with fsspec.open(
        f"s3://{BUCKET_NAME}/users/14242555/config.py"
    ) as f:
        auth_cfg = f.read()
    api_id = auth_cfg["TELEGRAM_API_ID"]
    api_hash = auth_cfg["TELEGRAM_API_HASH"]

    client = TelegramClient(
        str("session_path"),  # Convert Path to string for Telethon
        api_id=api_id,
        api_hash=api_hash,
    )

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
