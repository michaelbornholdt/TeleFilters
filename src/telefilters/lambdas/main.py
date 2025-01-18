import asyncio
import json
import logging
import os
import typing as t

from telefilters.lambdas import auth
from telefilters.prompts import get_freifahren_risk_assessment
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
        elif message_text.startswith("/get_bvg_risk"):
            return asyncio.run(get_bvg_risk(message_text, user_id, chat_id))
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


async def get_bvg_risk(body: str, user_id: int, chat_id: int) -> t.Dict:
    """Get risk assessment for Freifahren channel\
        
    Args:
        body (str): User's input message
        user_id (int): User's ID
        chat_id (int): Chat ID

    Returns:
        dict: Response message
    """

    client, api_id, api_hash, bot_token = auth.get_telegram_client(user_id)
    openai_client = auth.get_openai_client()
    await client.connect()

    sendReply(bot_token, chat_id, "Thanks for the request, thinking...")

    channel = await client.get_entity("t.me/freifahren_BE")
    logger.info(f"Channel: {channel}")

    messages = await client.get_messages(channel, limit=20)[::-1]
    if not messages:
        message_out = "No messages found in Freifahren channel"
        return

    messages = [(msg.date.strftime("%H:%M"), msg.text) for msg in messages]
    logger.info(f"Freifahren messages: {messages}")
    prompt_freifahren = "\n".join([f"{time}: {text}" for time, text in messages])

    message_out = get_freifahren_risk_assessment(
        client=openai_client,
        user_prompt=body,
        freifahren_prompt=prompt_freifahren,
    )
    logger.info(f"Assistant's response:\n{message_out}")

    sendReply(bot_token, chat_id, message_out)
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Authorization successful"}),
    }


if __name__ == "__main__":
    summarize("test")
