import os
import boto3
import dotenv
import argparse
from PIL import Image, ImageDraw, ImageFont


dotenv.load_dotenv()


def display_image(img_fp, response):
    image = Image.open(img_fp).convert("RGBA")

    # Ready image to draw bounding boxes on it.
    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    # calculate and display bounding boxes for each detected custom label
    print("Detected custom labels for ")
    for customLabel in response["CustomLabels"]:
        if "Geometry" in customLabel:
            box = customLabel["Geometry"]["BoundingBox"]
            left = imgWidth * box["Left"]
            top = imgHeight * box["Top"]
            width = imgWidth * box["Width"]
            height = imgHeight * box["Height"]

            area = height*width
            # if area > 500000:
            #     continue
            # if area < 20000:
            #     continue
            print(f"{customLabel['Name']}: {customLabel['Confidence']:0.2f}")
            print(f"{area=}")

            # print("Left: " + "{0:.0f}".format(left))
            # print("Top: " + "{0:.0f}".format(top))
            # print("Label Width: " + "{0:.0f}".format(width))
            # print("Label Height: " + "{0:.0f}".format(height))

            points = (
                (left, top),
                (left + width, top),
                (left + width, top + height),
                (left, top + height),
                (left, top),
            )
            draw.line(points, fill="#00d400", width=10)
            draw.text(
                (left, top),
                customLabel["Name"],
                fill="#ff0000",
                font=ImageFont.load_default(size=50),
            )
    image.show()


def show_custom_labels(model, img_fp, min_confidence):
    client = boto3.client("rekognition")
    with open(img_fp, "rb") as image_f:
        img_bytes = image_f.read()

    # Call DetectCustomLabels
    response = client.detect_custom_labels(
        Image={"Bytes": img_bytes},
        MinConfidence=min_confidence,
        ProjectVersionArn=model,
    )

    # For object detection use case, uncomment below code to display image.
    display_image(img_fp, response)

    return len(response["CustomLabels"])


def main(model: str, min_confidence: float, img_fp: str):
    label_count = show_custom_labels(model, img_fp, min_confidence)
    print("Custom labels detected: " + str(label_count))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process image")
    parser.add_argument("img_fp", type=str, help="Image file path")
    parser.add_argument(
        "--model", type=str, default=os.getenv("MODEL"), help="Model ARN"
    )
    parser.add_argument(
        "--min_confidence",
        type=float,
        default=os.getenv("MIN_CONFIDENCE"),
        help="Minimum confidence",
    )

    args = parser.parse_args()
    main(args.model, args.min_confidence, args.img_fp)
