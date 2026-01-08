import base64
import io
import json
from openai import OpenAI

def encode_image(image):
    """Encodes a PIL Image to base64 string"""
    # Resize image to reduce payload size
    max_dimension = 1024
    width, height = image.size
    if width > max_dimension or height > max_dimension:
        ratio = min(max_dimension / width, max_dimension / height)
        new_size = (int(width * ratio), int(height * ratio))
        # Use simple resizing
        image = image.resize(new_size)
    
    buffered = io.BytesIO()
    # Convert to RGB to ensure JPEG compatibility and save as JPEG to save space
    image = image.convert("RGB")
    image.save(buffered, format="JPEG", quality=85)
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
                "url": f"data:image/jpeg;base64,{base64_image}"
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
        
        # Additional debug info
        # print(f"DEBUG: Response type: {type(response)}")

        if isinstance(response, str):
            # If response is a string, it might be the raw content or a JSON string
            # Avoid printing massive HTML content
            # print(f"DEBUG: Response is a string: {repr(response)[:200]}...") 

            resp_str = response.strip().lower()
            
            # Check for HTML error (WAF or Landing Page or Generic 404/Authentication page)
            if resp_str.startswith("<!doctype") or resp_str.startswith("<html") or "<body" in resp_str:
                print(f"Error: API returned HTML instead of JSON. Base URL was: {base_url}")
                print("Likely causes:")
                print("1. Base URL is incorrect (e.g. missing '/v1' suffix).")
                print("2. Endpoint is a dashboard/landing page, not the API.")
                print("3. WAF/Proxy blocking the request.")
                return []

            clean_response = response.strip()
            # Remove markdown code blocks if present
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")
                if len(clean_response) >= 3:
                     # Usually [empty, json_content, empty] or similar
                     # Find the part that looks like JSON or just take the middle
                     clean_response = clean_response[1]
                     if clean_response.startswith("json"):
                         clean_response = clean_response[4:]
                else:
                    clean_response = clean_response.strip("`") # fallback
            
            clean_response = clean_response.strip()

            try:
                # Attempt to parse directly as the result dict/list
                # If the string Is the content (e.g. {"toc": ...})
                data_check = json.loads(clean_response)
                
                # Check if it simulates the full response structure
                if "choices" in data_check:
                     result = data_check['choices'][0]['message']['content']
                else:
                     # Assume the string IS the content
                     result = clean_response
            except json.JSONDecodeError as e:
                print(f"Failed to parse cleaned string response: {e}")
                print(f"Cleaned content was: {repr(clean_response)}")
                return []
        else:
            # Normal object access
            result = response.choices[0].message.content

        # Final parse of the content (which should be JSON text)
        try:
             # If result is already a dict, use it (case where we parsed direct content above)
             if isinstance(result, dict):
                 data = result
             else:
                 # Remove potential markdown if it came from the object path
                 clean_result = result.strip()
                 if clean_result.startswith("```"):
                     clean_result = clean_result.split("```")[1]
                     if clean_result.startswith("json"):
                         clean_result = clean_result[4:]
                     clean_result = clean_result.strip()
                 data = json.loads(clean_result)
                 
             return data.get('toc', [])
        except Exception as e:
             print(f"Error parsing final JSON content: {e}")
             print(f"Content was: {repr(result)}")
             return []
        
    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        if "413" in str(e) or "Request Entity Too Large" in str(e):
             print("Error: content too large.")
        return []
