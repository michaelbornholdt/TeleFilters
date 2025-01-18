# Telegram Bot
This bot is designed to handle various Telegram commands using Python.

# Development
This project deploys an AWS infrastructure using the AWS Cloud Development Kit (CDK). It includes:

- An S3 bucket.
- An API Gateway with a POST `/bot` endpoint.
- A Lambda function triggered by the API Gateway.
- A Lambda Layer for Python dependencies.
- Integration with AWS Secrets Manager to pass a secret to the Lambda function as an environment variable.

## Prerequisites

1. **AWS Account**: You must have an active AWS account.
2. **AWS CLI**: Install and configure the AWS Command Line Interface with a valid profile.
   ```bash
   aws configure
   ```
3. **Node.js**: Install Node.js (version 14.x or later).
    ```bash
    node -v
    ```
4. **Python**: Install Python (3.9 or later) and pip.
    ```bash
    python3 --version
    pip3 --version
    ```
5. **AWS CDK CLI**: Install the AWS CDK CLI globally using npm.
    ```bash
    npm install -g aws-cdk
    ```
    Verify installation:
    ```bash
    cdk --version
    ```
6. **Bootstrap Your AWS Environment**: Bootstrap the CDK environment (if not done already).
    ```bash
    cdk bootstrap aws://<AWS_ACCOUNT_ID>/<AWS_REGION>
    ```

## Deployment Steps
1. **Clone the Repository**: Clone this repository or copy the project files to your working directory.
2. **Install Dependencies**:
 - Install Python packages for the Lambda Layer:
    ```bash
    pip install -r lambda_layer/python/requirements.txt -t lambda_layer/python
    pip install -t lambda_layer/python --platform manylinux2014_x86_64 --only-binary=:all: --upgrade pydantic pydantic_core
    ```
3. **Configure the CDK App**: Ensure the app.py file references the correct resources and environment variables, such as the Secrets Manager secret name.
4. **Deploy the CDK Stack**: Run the following command to deploy the stack:
    ```bash
    cdk deploy
    ```
    The CDK CLI will prompt for confirmation. Type y to proceed.

## Cleanup
To avoid incurring charges, destroy the stack when you no longer need it:
```bash
cdk destroy
```

## Notes
Update the `dev/bot` in the CDK stack to the name of your existing secret in Secrets Manager.
Avoid committing sensitive information (e.g., AWS credentials) to version control.
For production, ensure your Lambda function's environment variables are encrypted and use IAM roles with the least privilege.
Troubleshooting

If you encounter issues during deployment, verify that your AWS CLI is correctly configured and your CDK environment is bootstrapped.
Check the AWS CloudFormation console for detailed error messages.
Ensure all required packages are installed in the Lambda Layer directory.
