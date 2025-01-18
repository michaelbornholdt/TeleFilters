import asyncio
import json
import logging
import os
import typing as t

from telefilters.lambdas.commands import get_bvg_risk

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

        # if message_text.startswith("/summarize"):
        #     return summarize(message_text, user_id, chat_id)
        if message_text.startswith("/get_bvg_risk"):
            # Create new event loop for async operation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    get_bvg_risk(message_text, user_id, chat_id)
                )
            finally:
                loop.close()
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
