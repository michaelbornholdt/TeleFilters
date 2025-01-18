import json
import logging
import typing as t

from telefilters.lambdas import auth

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: t.Dict, context: t.Dict) -> t.Dict:
    body = json.loads(event["body"])
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
    telegram_client = auth.get_telegram_client()
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
