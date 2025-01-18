import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    body = json.loads(event['body'])

    print("*** Received event")

    return {
        'statusCode': 200,
        'body': json.dumps(body)
    }
