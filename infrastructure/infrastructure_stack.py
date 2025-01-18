from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    RemovalPolicy
)
from constructs import Construct


class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create an S3 bucket
        bucket = s3.Bucket(
            self, "UserData",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        bot_lambda_function = _lambda.Function(
            self, "BotFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="main.lambda_handler",
            code=_lambda.Code.from_asset("src/bot"),
            environment={
                "BUCKET_NAME": bucket.bucket_name
            }
        )

        # Grant Lambda permissions to write to the S3 bucket
        bucket.grant_write(bot_lambda_function)

        # Create an API Gateway
        api = apigateway.RestApi(
            self, "TelegramApi",
            rest_api_name="TelegramApi",
            description="API for Telegram Bot"
        )

        # Create /bot resource
        bot_resource = api.root.add_resource("bot")

        # Add POST method to /bot, integrated with the Lambda function
        bot_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(bot_lambda_function),
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200"
                )
            ]
        )
