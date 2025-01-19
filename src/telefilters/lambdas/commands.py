import json
import logging
import os
import typing as t

from telefilters import auth
from telefilters.prompts import get_freifahren_risk_assessment
from telefilters.telegram.messaging import sendReply

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))


async def summarize(body: str, user_id: int, chat_id: int) -> t.Dict:
    raise NotImplementedError("This function is not working right yet.")
    client, api_id, api_hash, bot_token = auth.get_telegram_client(user_id)

    try:
        openai_client = auth.get_openai_client()
        logger.info("Authorization successful")

        # Send authentication success message to user
        message = "✅ Authentication successful! I'm now processing your request..."
        sendReply(bot_token, chat_id, message)

        from telefilters.telegram.scraper import scrape_messages
        from telefilters.telegram.process import analyze_conversations

        #scraped_content = scrape_messages(client=client)
        #processed_content = analyze_conversations(openai_client, scraped_content)
    
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
    """Get risk assessment for Freifahren channel"""
    try:
        client, api_id, api_hash, bot_token = auth.get_telegram_client(user_id)

        # Send thinking message
        await sendReply(bot_token, chat_id, "Thanks for the request, thinking...")

        try:
            await client.connect()
            channel = await client.get_entity("t.me/freifahren_BE")
            logger.info(f"Channel: {channel}")

            # Get messages and reverse them after converting to list
            messages = await client.get_messages(channel, limit=20)
            messages = list(messages)[::-1]

            if not messages:
                message_out = "No messages found in Freifahren channel"
                await sendReply(bot_token, chat_id, message_out)
                return {
                    "statusCode": 200,
                    "body": json.dumps({"message": message_out}),
                }

            messages = [(msg.date.strftime("%H:%M"), msg.text) for msg in messages]
            logger.info(f"Freifahren messages: {messages}")

            prompt_freifahren = "\n".join(
                [f"{time}: {text}" for time, text in messages]
            )
            openai_client = auth.get_openai_client()

            message_out = await get_freifahren_risk_assessment(
                client=openai_client,
                user_prompt=body,
                freifahren_prompt=prompt_freifahren,
            )

            logger.info(f"Assistant's response:\n{message_out}")
            await sendReply(bot_token, chat_id, message_out)

            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Request processed successfully"}),
            }

        finally:
            await client.disconnect()

    except Exception as e:
        error_message = f"Error processing request: {str(e)}"
        logger.error(error_message)
        await sendReply(
            bot_token,
            chat_id,
            "Sorry, an error occurred while processing your request.",
        )
        return {
            "statusCode": 500,
            "body": json.dumps({"message": error_message}),
        }
