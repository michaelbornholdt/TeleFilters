import json
import logging
import typing as t

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: t.Dict, context: t.Dict) -> t.Dict:
    logger.info(f"Event: {json.dumps(event)}")

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Hello from Lambda!"}),
    }
