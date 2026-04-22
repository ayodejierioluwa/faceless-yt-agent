import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def test_veo():
    api_key = os.getenv("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key)
    
    prompt = "Cinematic close up of a futuristic robot wearing a fast food headset, neon drive-thru lights, 4k, realistic"
    output_path = "test_veo_video.mp4"
    
    print(f"Starting Veo generation for: {prompt}")
    try:
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio="9:16"
            )
        )
        
        while not operation.done:
            print("Generating...")
            time.sleep(15)
            
        if operation.result and operation.result.generated_videos:
            video_file = operation.result.generated_videos[0]
            print(f"Download started: {video_file.file_name}")
            video_bytes = client.files.download(file_name=video_file.file_name)
            with open(output_path, "wb") as f:
                f.write(video_bytes)
            print(f"Video saved to {output_path}")
        else:
            print("No video generated.")
            print(f"Operation result: {operation.result}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_veo()
