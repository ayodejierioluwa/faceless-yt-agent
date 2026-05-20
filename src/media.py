import os
import time
import subprocess
import requests
import sys
from dotenv import load_dotenv

load_dotenv()

def generate_audio(text: str, output_path: str, voice: str = "Puck") -> bool:
    """
    Uses Gemini 3.1 Pro native Audio generation (Omni) to synthesize highly expressive voiceovers.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found for Gemini TTS.")
        return False

    try:
        from google import genai
        from google.genai import types
        
        print(f"     [Gemini Voice] Generating expressive native audio for: '{text[:30]}...'")
        client = genai.Client(api_key=api_key)
        
        # We tell the model to narrate the text as an expressive storyteller
        prompt = f"Please narrate the following text exactly as written, with a dramatic, suspenseful tone suitable for a dark history documentary:\\n\\n{text}"
        
        response = client.models.generate_content(
            model="gemini-3.1-pro",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice
                        )
                    )
                )
            )
        )
        
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.mime_type.startswith("audio/"):
                    with open(output_path, "wb") as f:
                        f.write(part.inline_data.data)
                    return True
                    
        print("     [Gemini Voice] Failed to extract audio bytes from response.")
        return False
        
    except Exception as e:
        print(f"Error generating Gemini TTS audio: {e}")
        return False

def generate_flux_image(prompt: str, output_path: str, retries: int = 2) -> bool:
    """
    Uses Google Imagen Premium AI with robust fallback to Pollinations.ai (Turbo) and Pexels Photo API.
    """
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai
            from google.genai import types
            print(f"     [Imagen] Requesting Premium Google Imagen generation for: '{prompt[:40]}...'")
            client = genai.Client(api_key=api_key)
            response = client.models.generate_images(
                model="imagen-3.0-generate-001",
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio="9:16"
                )
            )
            if response.generated_images:
                with open(output_path, "wb") as f:
                    f.write(response.generated_images[0].image.image_bytes)
                print(f"     [Imagen] Premium Google Imagen generated successfully!")
                return True
        except Exception as e:
            pass
            
    # Fallback to Pollinations AI (Turbo Model)
    for attempt in range(retries):
        try:
            print(f"     [Pollinations] Generating cinematic image (Turbo)...")
            encoded_prompt = requests.utils.quote(prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&model=turbo&nologo=true&seed={int(time.time())}"
            res = requests.get(url, timeout=15)
            res.raise_for_status()
            with open(output_path, "wb") as f:
                f.write(res.content)
            return True
        except Exception as e:
            pass
            
    # Ultimate Fallback: Pexels Stock Photo API (100% Uptime Guarantee)
    try:
        print(f"     [Pexels Photo] Fetching professional portrait stock photo for: '{prompt[:35]}...'")
        pexels_key = os.getenv("PEXELS_API_KEY", "Iu4uqM5DDFrjYMJ1qZ2B339y3xPGlZ00VJmO6PVPAKpkkPvlzmY8tkP2")
        headers = {"Authorization": pexels_key}
        search_query = prompt.split(",")[0] if "," in prompt else prompt
        search_url = f"https://api.pexels.com/v1/search?query={search_query}&per_page=3&orientation=portrait"
        
        res = requests.get(search_url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            photos = data.get("photos", [])
            if photos:
                photo_url = photos[0]["src"]["large2x"]
                img_res = requests.get(photo_url, timeout=15)
                if img_res.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(img_res.content)
                    print("     [Pexels Photo] Stock photo acquired successfully!")
                    return True
    except Exception as e:
        print(f"     [Pexels Photo] Fallback failed: {e}")
        
    return False

def fetch_pexels_video(query: str, output_path: str) -> bool:
    """
    Searches Pexels API. If the specific query fails, it tries broader terms.
    """
    api_key = os.getenv("PEXELS_API_KEY", "Iu4uqM5DDFrjYMJ1qZ2B339y3xPGlZ00VJmO6PVPAKpkkPvlzmY8tkP2")
    if not api_key or api_key == "your_pexels_api_key_here":
        return False

    headers = {"Authorization": api_key}
    
    # Try multiple search variations if the first one fails
    search_queries = [query, "abstract technology", "cyberpunk futuristic", "artificial intelligence"]
    
    for q in search_queries:
        print(f"     [Pexels] Searching for: '{q[:30]}...'")
        search_url = f"https://api.pexels.com/videos/search?query={q}&per_page=5&orientation=portrait"
        try:
            res = requests.get(search_url, headers=headers, timeout=10)
            res.raise_for_status()
            data = res.json()
            
            if not data.get("videos"):
                continue
                
            video_data = data["videos"][0]
            video_files = video_data.get("video_files", [])
            
            best_link = None
            for file_info in video_files:
                if file_info.get("file_type") == "video/mp4" and file_info.get("quality") == "hd":
                    best_link = file_info.get("link")
                    break
            
            if not best_link and video_files:
                best_link = video_files[0].get("link")
                
            if best_link:
                vid_res = requests.get(best_link, stream=True, timeout=30)
                vid_res.raise_for_status()
                with open(output_path, 'wb') as f:
                    for chunk in vid_res.iter_content(chunk_size=8192):
                        if chunk: f.write(chunk)
                return True
        except Exception as e:
            print(f"     [Pexels] Query '{q}' failed: {e}")
            
    return False

def fetch_background_music(output_path: str) -> bool:
    """
    Downloads a royalty-free cinematic background track.
    Using a reliable free source for cinematic music.
    """
    try:
        print(f"     [Music] Fetching cinematic background track...")
        # Link to a high-quality, royalty-free cinematic track (example from a free provider)
        # In a real scenario, we'd search an API, but for now, we use a curated high-quality free link.
        url = "https://www.chosic.com/wp-content/uploads/2021/07/The-Grand-Score.mp3"
        
        res = requests.get(url, timeout=30)
        res.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(res.content)
        return True
    except Exception as e:
        print(f"     [Music] Failed to fetch music: {e}")
        return False

def generate_veo_video(prompt: str, output_path: str) -> bool:
    """
    Generates a high-quality video clip using Google's Veo model (veo-3.1-generate-preview).
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("     [Veo] Error: GOOGLE_API_KEY not found in environment.")
        return False

    try:
        from google import genai
        from google.genai import types
        
        print(f"     [Veo] Initializing client...")
        client = genai.Client(api_key=api_key)
        
        print(f"     [Veo] Requesting 6s preview video for: '{prompt[:45]}...'")
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio="9:16",
                duration_seconds=6
            )
        )
        
        print("     [Veo] Processing on Google Cloud. This usually takes 60-90 seconds...")
        while not operation.done:
            print("     [Veo] Still generating...")
            time.sleep(10)
            
        if operation.result and operation.result.generated_videos:
            video_file = operation.result.generated_videos[0]
            print(f"     [Veo] Generation complete. Downloading: {video_file.file_name}")
            video_bytes = client.files.download(file_name=video_file.file_name)
            
            with open(output_path, "wb") as f:
                f.write(video_bytes)
            print(f"     [Veo] Video saved to {output_path} successfully!")
            return True
        else:
            print(f"     [Veo] Failed: No video returned from the Veo operation.")
            return False
            
    except Exception as e:
        print(f"     [Veo] Error generating video: {e}")
        return False

if __name__ == "__main__":
    generate_audio("Test", "test.mp3")

