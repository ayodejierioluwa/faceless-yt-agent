import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def test_imagen():
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)
    
    prompt = "Cinematic close up of a futuristic robot wearing a fast food headset, neon drive-thru lights, 4k, realistic"
    output_path = "test_imagen_image.png"
    
    print(f"Starting Imagen generation for: {prompt}")
    try:
        # Note: model name might vary, using imagen-3.0-generate-001 as per docs
        response = client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="9:16"
            )
        )
        
        if response.generated_images:
            image_data = response.generated_images[0]
            # Download bytes and save
            with open(output_path, "wb") as f:
                f.write(image_data.image.image_bytes)
            print(f"Image saved to {output_path}")
        else:
            print("No image generated.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_imagen()
