import boto3
import argparse
import json
import base64
import pprint
import dotenv
import os

dotenv.load_dotenv()

# Create session and establish connection to client['
lambda_client = boto3.client(
    "lambda",
    region_name="us-east-1",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    # aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
)

# Replace with the name of your Lambda function
function_name = "image-processing"


def analyze_image_local(img_path):
    print("Analyzing local image:")

    with open(img_path, "rb") as image_file:
        image_bytes = image_file.read()
        data = base64.b64encode(image_bytes).decode("utf8")

        lambda_payload = {"image": data}

        # Invoke the Lambda function with the event payload
        response = lambda_client.invoke(
            FunctionName=function_name, Payload=(json.dumps(lambda_payload))
        )

        decoded = json.loads(response["Payload"].read().decode())
        pprint.pprint(decoded)


def main(path_to_image):
    analyze_image_local(path_to_image)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process image")
    parser.add_argument(
        "image_path", type=str, help="Path to the image file to process"
    )
    args = parser.parse_args()
    main(args.image_path)
