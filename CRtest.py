from openai import OpenAI
import os
import base64
## Set the API key
client = OpenAI(api_key="sk-proj-duozMzg3L6ardgQeu6g4T3BlbkFJcoPr49KLa9JqPVGitNk6")

MODEL="gpt-4o"


import base64

IMAGE_PATH = "C:/Users/Lenovo/Desktop/微信图片_20240607180220.png"

# Open the image file and encode it as a base64 string
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

base64_image = encode_image(IMAGE_PATH)

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a helpful assistant that responds in Markdown. Help me with my math homework!"},
        {"role": "user", "content": [
            {"type": "text", "text": "请帮我解决图中的问题"},
            {"type": "image_url", "image_url": {
                "url": f"data:image/png;base64,{base64_image}"}
            }
        ]}
    ],
    temperature=0.0,
)
print(response.choices[0].message.content)
