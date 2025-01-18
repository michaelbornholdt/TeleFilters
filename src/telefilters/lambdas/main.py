import json
import logging
import typing as t

from telefilters.lambdas import auth
from telefilters.telegram.messaging import send_telegram_message

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def lambda_handler(event: t.Dict, context: t.Dict) -> t.Dict:
    try:
        body = json.loads(event["body"])
        logger.info(f"Event: {json.dumps(event)}")

        chat_id = body["message"]["chat"]["id"]
        user_name = body["message"]["from"]["username"]
        message_text = body["message"]["text"]

        if message_text.startswith("/summarize"):
            return summarize(message_text, chat_id)
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


def summarize(body: str, chat_id: int) -> t.Dict:
    try:
        telegram_client = auth.get_telegram_client()
        openai_client = auth.get_openai_client()
        logger.info("Authorization successful")

        # Send authentication success message to user
        message = "✅ Authentication successful! I'm now processing your request..."
        send_telegram_message(telegram_client, chat_id, message)

        return {
            "statusCode": 200,
            "body": json.dumps(
                {"message": "Message sent to user successfully", "chat_id": chat_id}
            ),
        }
    except Exception as e:
        logger.error(f"Error in summarize function: {str(e)}")
        error_message = "❌ Sorry, something went wrong while processing your request."
        try:
            telegram_client = auth.get_telegram_client()
            send_telegram_message(telegram_client, chat_id, error_message)
        except:
            logger.error("Failed to send error message to user")

        return {
            "statusCode": 500,
            "body": json.dumps({"message": str(e)}),
        }


# def refresh_freifahren_df(body: str, user_id: str) -> str:
#     telegram_client = auth.get_telegram_client(user_id)

#     return {
#         "statusCode": 200,
#         "body": json.dumps({"message": "Authorization successful"}),
#     }


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
