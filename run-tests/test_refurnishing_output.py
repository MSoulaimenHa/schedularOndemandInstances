import os
import requests
import base64
from PIL import Image
from io import BytesIO

styles = ["scandinavian", "contemporary", "modern",
          "countryside", "coastal", "wooden", "industrial", "italian", "traditional"]
rooms = {
    "living room": "https://plus.unsplash.com/premium_photo-1706140675031-1e0548986ad1?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8bGl2aW5ncm9vbXxlbnwwfHwwfHx8MA%3D%3D",
    "bedroom": "https://media.istockphoto.com/id/1390233984/photo/modern-luxury-bedroom.jpg?s=612x612&w=0&k=20&c=po91poqYoQTbHUpO1LD1HcxCFZVpRG-loAMWZT7YRe4=",
    "bathroom": "https://www.neilkelly.com/wp-content/uploads/2019/10/Mcnown-Residence-22s.jpg",
    "kitchen": "https://www.wallpaperflare.com/static/39/121/109/interior-design-style-home-wallpaper.jpg"
}


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


os.makedirs("refurnishing", exist_ok=True)

url = "http://generative-virtual-refurnishing-1596830543.eu-central-1.elb.amazonaws.com/generative-virtual-refurnishing/predict"

for room, link in rooms.items():
    for style in styles:
        payload = {
            "base64_image": "",  # If there's no base64 image, this should be empty
            "image_url": link,
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
                image_path = os.path.join("refurnishing", room, f"{style}.png")
                convert(img_b64, image_path)
                print(f"Image saved at {image_path}")
            else:
                print(f"No image returned for {room} - {style}")
        else:
            print(f"Failed to get a response for {room} - {style}")
