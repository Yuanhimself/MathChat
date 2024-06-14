import base64

def encode_images(image_paths):
    base64_images = []
    for image_path in image_paths:
        with open(image_path, "rb") as image_file:
            base64_images.append(base64.b64encode(image_file.read()).decode("utf-8"))
    return base64_images