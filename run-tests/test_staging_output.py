import os
import requests
import base64
from PIL import Image
from io import BytesIO

styles = ["scandinavian", "contemporary", "modern",
          "countryside", "coastal", "wooden", "industrial", "italian"]
rooms = ["living room", "bedroom"]


def base64_to_image(base64_string):
    # Remove the data URI prefix if present
    if "data:image" in base64_string:
        base64_string = base64_string.split(",")[1]

    # Decode the Base64 string into bytes
    image_bytes = base64.b64decode(base64_string)
    return image_bytes


def create_image_from_bytes(image_bytes):
    # Create a BytesIO object to handle the image data
    image_stream = BytesIO(image_bytes)

    # Open the image using Pillow (PIL)
    image = Image.open(image_stream)
    return image


def convert(base64_string, path):
    # Convert Base64 to image bytes
    image_bytes = base64_to_image(base64_string)

    # Create an image from bytes
    img = create_image_from_bytes(image_bytes)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Save the image to the specified path
    img.save(path)


os.makedirs("staging", exist_ok=True)

url = "http://generative-virtual-staging-1376216257.eu-central-1.elb.amazonaws.com/generative-virtual-staging/predict"

for room in rooms:
    for style in styles:
        payload = {
            "base64_image": "",  # If there's no base64 image, this should be empty
            "image_url": "https://media.istockphoto.com/id/521806786/photo/3d-rendering-of-empty-room-interior-white-brown-colors.jpg?s=612x612&w=0&k=20&c=njPof128FBEo4KjyC8ONDUPS0aBBkFEial5Uy8xoqdA=",
            "room_type": room,
            "architecture_style": style
        }
        # Use json=payload to send as JSON
        response = requests.post(url=url, json=payload)
        print(f"Status Code for {room} - {style}: {response.status_code}")

        if response.status_code == 200:
            jsonResponse = response.json()
            img_b64 = jsonResponse.get("result")

            if img_b64:
                image_path = os.path.join("staging", room, f"{style}.png")
                convert(img_b64, image_path)
                print(f"Image saved at {image_path}")
            else:
                print(f"No image returned for {room} - {style}")
        else:
            print(f"Failed to get a response for {room} - {style}")
