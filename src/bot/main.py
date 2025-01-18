import json
import logging
import typing as t

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: t.Dict, context: t.Dict) -> t.Dict:
    body = json.loads(event['body'])
    logger.info(f"Event: {json.dumps(event)}")

    chat_id = body["message"]["chat"]["id"]
    user_name = body["message"]["from"]["username"]
    message_text = body["message"]["text"]

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": f"Received message from {user_name} in chat {chat_id}: {message_text}"
            }
        ),
    }


# def auth(event: t.Dict, context: t.Dict) -> t.Dict:
#     logger.info(f"Event: {json.dumps(event)}")

#     from user_manager import UserManager

#     # read authorization token from s3
#     um = UserManager()

#     um.


#     return {
#         "statusCode": 200,
#         "body": json.dumps(
#             {
#                 "message": "Authorization successful"
#             }
#         ),
#     }
