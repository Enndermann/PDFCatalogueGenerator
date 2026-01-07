import base64
import io
import json
from openai import OpenAI

def encode_image(image):
    """Encodes a PIL Image to base64 string"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def extract_toc_from_images(images, api_key, base_url="https://api.openai.com/v1", model="gpt-4o"):
    """
    Sends images to OpenAI and retrieves structured TOC data.
    """
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    content = [
        {"type": "text", "text": "Extract the table of contents from these images. Return ONLY a JSON object with a key 'toc' which is a list of items. Each item must have 'level' (int, 1 for main chapters, 2 for sections, etc.), 'title' (string), and 'page' (int, the page number shown in the image). Do not include any markdown formatting or code blocks, just the raw JSON."}
    ]
    
    for img in images:
        base64_image = encode_image(img)
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        })

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": content}
            ],
            response_format={"type": "json_object"}
        )
        
        result = response.choices[0].message.content
        data = json.loads(result)
        return data.get('toc', [])
        
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return []
