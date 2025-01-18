from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_secretsmanager as secretsmanager,
    RemovalPolicy
)
from constructs import Construct


class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Retrieve secret from Secrets Manager
        secret = secretsmanager.Secret.from_secret_name_v2(
            self, "Bot", secret_name="dev/bot"
        )

        # Create an S3 bucket
        bucket = s3.Bucket(
            self, "UserData",
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        # Create a Lambda layer for Python packages
        lambda_layer = _lambda.LayerVersion(
            self, "Packages",
            code=_lambda.Code.from_asset("src/lambda_layer"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            description="A layer for Python dependencies"
        )

        bot_lambda_function = _lambda.Function(
            self, "BotFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="main.lambda_handler",
            code=_lambda.Code.from_asset("src/bot"),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "BOT_SECRET": secret.secret_name,
            },
            layers=[lambda_layer]
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
