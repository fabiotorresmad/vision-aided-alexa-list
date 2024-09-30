import boto3
import os
import logging
from botocore.exceptions import ClientError
import json
import base64

LOG = logging.getLogger(__name__)
model = os.getenv("MODEL")
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("ProductsList")
rekognition = boto3.client("rekognition")

LABELS = [
    "club-social-purple",
    "club-social-red",
    "club-social-yellow",
    "lacta",
    "piraque",
]


def load_image(event):
    """Load image from S3 or base64 encoded image bytes.
    Args:
        event: Lambda event
    Returns:
        image: Image bytes
    Raises:
        ValueError: If image is not found
    """
    image = None
    if "S3Bucket" in event and "S3Object" in event:
        s3 = boto3.resource("s3")
        s3_object = s3.Object(event["S3Bucket"], event["S3Object"])
        image = s3_object.get()["Body"].read()

    elif "image" in event:
        image_bytes = event["image"].encode("utf-8")
        img_b64decoded = base64.b64decode(image_bytes)
        image = img_b64decoded
    elif image is None:
        raise ValueError("Missing image, check image or bucket path.")

    else:
        raise ValueError("Only base 64 encoded image bytes or S3Object are supported.")
    return image


def process_image(event):
    image = load_image(event)
    try:
        response = rekognition.detect_custom_labels(
            Image={"Bytes": image},
            MinConfidence=40,
            ProjectVersionArn=model,
        )
    except ClientError as client_err:
        raise ValueError(
            "Couldn't analyze image: " + client_err.response["Error"]["Message"]
        )
    labels = [
        {
            "name": label["Name"],
            "confidence": label["Confidence"],
            "area": label["Geometry"]["BoundingBox"]["Width"]*label["Geometry"]["BoundingBox"]["Height"],
        }
        for label in response["CustomLabels"]
    ]
    return labels


def update_db(labels):
    """Update DynamoDB table with product labels."""
    # count labels and update db
    products = {name: 0 for name in LABELS}
    for label in labels:
        # if label["area"] > 500_000:
        #     continue
        # if label["area"] < 20_000:
        #     continue
        if label["name"] in products:
            products[label["name"]] += 1

    for product, quantity in products.items():
        # put item if doesn't exist; otherwise, replace quantity
        response = table.get_item(Key={"ProductName": product})
        if "Item" in response:
            table.update_item(
                Key={"ProductName": product},
                UpdateExpression="set Quantity = :q",
                ExpressionAttributeValues={":q": quantity},
            )
        else:
            table.put_item(
                Item={
                    "ProductName": product,
                    "Brand": "unknown",
                    "Quantity": quantity,
                    "Category": "unknown",
                }
            )
    return products



def lambda_handler(event, context):
    try:
        body = {}
        body["labels"] = process_image(event)
        body["saved"] = update_db(body["labels"])
        lambda_response = {"statusCode": 200, "body": json.dumps(body)}

    except ClientError as client_err:
        error_message = client_err.response["Error"]["Message"]
        lambda_response = {
            "statusCode": 400,
            "body": {
                "Error": client_err.response["Error"]["Code"],
                "ErrorMessage": error_message,
            },
        }
        LOG.error("Error function %s: %s", context.invoked_function_arn, error_message)

    except ValueError as val_error:
        lambda_response = {
            "statusCode": 400,
            "body": {"Error": "ValueError", "ErrorMessage": format(val_error)},
        }
        LOG.error(
            "Error function %s: %s", context.invoked_function_arn, format(val_error)
        )

    return lambda_response
