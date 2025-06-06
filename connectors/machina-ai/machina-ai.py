from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from openai import OpenAI

import base64
from io import BytesIO
from PIL import Image


def edit_image(request_data):

    headers = request_data.get("headers")

    params = request_data.get("params")

    api_key = headers.get("api_key", "")

    image_id = params.get("image_id", "")

    model_name = params.get("model", "")

    instruction = params.get("instruction", "")

    images_base64 = params.get("images_base64", [])

    if not api_key:
        return {"status": "error", "message": "API key is required."}

    if not model_name:
        return {"status": "error", "message": "Model name is required."}

    if not images_base64:
        return {"status": "error", "message": "At least one image is required."}

    image_files = []
    try:
        for idx, img_base64 in enumerate(images_base64):
            if ',' in img_base64:
                img_base64 = img_base64.split(',')[1]
            
            img_bytes = base64.b64decode(img_base64)
            
            try:
                img = Image.open(BytesIO(img_bytes))
                if img.format == 'WEBP':
                    if img.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.getchannel('A'))
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    temp_filepath = f"/work/images/temp_{image_id}_{idx}.png"
                    img.save(temp_filepath, 'PNG')
                else:
                    temp_filepath = f"/work/images/temp_{image_id}_{idx}.png"
                    with open(temp_filepath, 'wb') as f:
                        f.write(img_bytes)
            except Exception as e:
                return {"status": "error", "message": f"Error converting image format: {str(e)}"}
            
            image_files.append(temp_filepath)
    except Exception as e:
        return {"status": "error", "message": f"Error saving images: {str(e)}"}

    prompt = f"""
        Create a 3:2 landscape image blog thumbnail, strictly aligned with the imagery guidelines below, using the provided <brandGuidelines> XML:

        Imagery Guidelines:

        Foreground Illustration Style - applies to any foreground subjects supplied in {instruction}:
        - Illustrate each foreground subject in a style reminiscent of the classic SNES video game "International Superstar Soccer"
        - true 16-bit palette, visible 2–3 px outlines, pixel-inspired aesthetics, and dynamic, exaggerated poses typical of retro sports games.  

        Do not use sportsbook sponsors brands like Betano, Betclic, Bwin, Betfair, KTO, Alpha, etc.
        """

    try:
        llm = OpenAI(api_key=api_key)

        image_files = [
            open(path, "rb")
            for path in image_files
        ]

        result = llm.images.edit(
            model=model_name,
            image=image_files,
            prompt=prompt,
            size="1536x1024",
            quality="high",
        )

        image_base64 = result.data[0].b64_json

        image_bytes = base64.b64decode(image_base64)

        full_filepath = f"/work/images/{image_id}.webp"

        with open(full_filepath, 'wb') as f:

            f.write(image_bytes)

        final_filename = f"{image_id}.webp"

        # convert to png

        img = Image.open(full_filepath)
        
        final_filename = f"{image_id}.png"
        
        full_filepath = f"/work/images/{final_filename}"
        
        img.save(full_filepath, 'PNG')

        result = {
            "final_filename": final_filename,
            "full_filepath": full_filepath
        }

        return {"status": True, "data": result, "message": "Image generated."}

    except Exception as e:
        return {"status": False, "message": f"Exception when generating image: {e}"} 


def generate_image(request_data):

    headers = request_data.get("headers")

    params = request_data.get("params")

    api_key = headers.get("api_key", "")

    image_id = params.get("image_id", "")

    model_name = params.get("model", "")

    instruction = params.get("instruction", "")

    if not api_key:
        return {"status": "error", "message": "API key is required."}

    if not model_name:
        return {"status": "error", "message": "Model name is required."}

    prompt = f"""
        Create a 3:2 landscape image blog thumbnail, strictly aligned with the imagery guidelines below, using the provided <brandGuidelines> XML:

        Imagery Guidelines:

        Foreground Illustration Style - applies to any foreground subjects supplied in {instruction}:
        - Illustrate each foreground subject in a style reminiscent of the classic SNES video game "International Superstar Soccer" – true 16-bit palette, visible 2–3 px outlines, pixel-inspired aesthetics, and dynamic, exaggerated poses typical of retro sports games.  
        - Jerseys or clothing must clearly match each team’s official colors while omitting sponsor logos or recognizable faces.  
        - Convey energetic movement through pixel-art action lines and diagonal streaks; avoid motion blur to preserve crisp retro authenticity.

        General Design Style (all other elements):
        Maintain sharp, modern, professional treatments for backgrounds, DOT graphic elements, and overall composition. Lighting should be high-contrast and crisp, simulating stadium floodlights without HDR glow.

        DOT Graphic Element Usage:
        MASK – Crop the entire foreground illustration within a 900 × 700 px parallelogram tilted 12° right, corner radius 65 px.  
        FILLED – Place a solid DOT in Bright Blue (#0A5EEA) or Bright Deep Blue (#003DC4) behind the foreground subjects to add visual depth.

        Background Canvas Options:
        - Bright Deep Blue (#003DC4) or Bright Dark Blue (#061F3F) for a dramatic night-game mood.  
        - White (#FFFFFF) for a lighter, open feel.

        Gradient (optional, use sparingly):
        – Bright Extra Light Blue (#D3ECFF) to Bright Light Blue (#45CAFF): soft diagonal sweep.  
        – Bright Light Blue (#45CAFF) to Bright Blue (#0A5EEA): energetic diagonal transition.  
        – Bright Deep Blue (#003DC4) to Bright Dark Blue (#061F3F): vertical fade for night intensity.

        Composition:
        Reserve 15–20 percent negative space for text overlays (headlines, match details).

        Camera POV:
        Low-angle or sideline telephoto with shallow depth of field (ƒ2.8–ƒ4).

        Lighting:
        High contrast from stadium floodlights, crisp shadows, no HDR glow.
    """

    try:
        llm = OpenAI(api_key=api_key)

        result = llm.images.generate(
            model=model_name,
            prompt=prompt,
            size="1536x1024",
            quality="high",
        )

        image_base64 = result.data[0].b64_json

        image_bytes = base64.b64decode(image_base64)

        full_filepath = f"/work/images/{image_id}.webp"

        with open(full_filepath, 'wb') as f:

            f.write(image_bytes)

        final_filename = f"{image_id}.webp"

        result = {
            "final_filename": final_filename,
            "full_filepath": full_filepath
        }

        return {"status": True, "data": result, "message": "Image generated."}

    except Exception as e:
        return {"status": False, "message": f"Exception when generating image: {e}"} 
    

def invoke_embedding(params):

    api_key = params.get("api_key", "")

    model_name = params.get("model_name")

    if not api_key:
        return {"status": "error", "message": "API key is required."}

    if not model_name:
        return {"status": "error", "message": "Model name is required."}

    try:
        llm = OpenAIEmbeddings(api_key=api_key, model=model_name)
        # llm = OpenAI(api_key=api_key)

    except Exception as e:
        return {"status": "error", "message": f"Exception when creating model: {e}"}

    return {"status": True, "data": llm, "message": "Model loaded."}


def invoke_prompt(params):

    api_key = params.get("api_key")

    model_name = params.get("model_name")

    if not api_key:
        return {"status": "error", "message": "API key is required."}

    if not model_name:
        return {"status": "error", "message": "Model name is required."}

    try:
        llm = ChatOpenAI(model=model_name, api_key=api_key)

    except Exception as e:
        return {"status": "error", "message": f"Exception when creating model: {e}"}

    return {"status": True, "data": llm, "message": "Model loaded."}


def transcribe_audio_to_text(params):
    """
    Transcribe an audio file to text using the new OpenAI Whisper transcription API.

    :param params: Dictionary containing the 'api_key' and 'audio-path' parameters.
    :return: Transcribed text or error message.
    """

    api_key = params.get("headers").get("api_key")
    file_items = params.get("params").get("audio-path", [])

    audio_file_path = file_items[0]

    try:

        llm = OpenAI(api_key=api_key)

        with open(audio_file_path, "rb") as audio_file:
            print(f"Transcribing file: {audio_file_path}")

            transcript = llm.audio.transcriptions.create(
              model="whisper-1",
              file=audio_file
            )

        return {"status": True, "data": transcript.text}

    except Exception as e:
        return {"status": False, "message": f"Exception when transcribing audio: {e}"} 
