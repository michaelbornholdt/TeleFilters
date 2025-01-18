import asyncio
import json
import logging
import os
import typing as t

from telefilters.lambdas import auth
from telefilters.telegram.messaging import sendReply

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


def lambda_handler(event: t.Dict, context: t.Dict) -> t.Dict:
    try:
        body = json.loads(event["body"])
        logger.info(f"Event: {json.dumps(event)}")

        chat_id = body["message"]["chat"]["id"]
        user_id = body["message"]["from"]["id"]
        user_name = body["message"]["from"]["first_name"]
        message_text = body["message"]["text"]

        if message_text.startswith("/summarize"):
            return summarize(message_text, user_id, chat_id)
        elif message_text.startswith("/get_freifahren_info"):
            return asyncio.run(get_freifahren_info(message_text, user_id, chat_id))
        else:
            return {
                "statusCode": 200,
                "body": json.dumps(
                    {
                        "message": f"Unknown command message from {user_name} in chat {chat_id}: {message_text}"
                    }
                ),
            }
    except Exception as e:
        logger.error(f"Error in lambda_handler: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error"}),
        }


def summarize(body: str, user_id: int, chat_id: int) -> t.Dict:
    client, api_id, api_hash, bot_token = auth.get_telegram_client(user_id)

    try:
        openai_client = auth.get_openai_client()
        logger.info("Authorization successful")

        # Send authentication success message to user
        message = "✅ Authentication successful! I'm now processing your request..."
        sendReply(bot_token, chat_id, message)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": "Message sent to user successfully", "chat_id": chat_id}
            ),
        }
    except Exception as e:
        logger.error(f"Error in summarize function: {str(e)}")

        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e)}),
        }


async def get_freifahren_info(body: str, user_id: int, chat_id: int) -> t.Dict:
    client, api_id, api_hash, bot_token = auth.get_telegram_client(user_id)
    openai_client = auth.get_openai_client()
    await client.connect()

    sendReply(bot_token, chat_id, "Thanks for the request, thinking...")

    channel = await client.get_entity("t.me/freifahren_BE")
    logger.info(f"Channel: {channel}")
    messages = await client.get_messages(channel, limit=100)
    messages = [msg.text for msg in messages]

    if not messages:
        message_out = "❌ No messages found in Freifahren channel"
    else:
        prompt_freifahren = messages
        prompt_user = body

    sendReply(bot_token, chat_id, message_out)
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
