import os
import time
import subprocess
import requests
import sys
from dotenv import load_dotenv

load_dotenv()

def generate_audio(text: str, output_path: str, voice: str = "en-US-ChristopherNeural") -> bool:
    """
    Uses edge-tts to generate MP3 from text.
    """
    try:
        cmd = [sys.executable, "-m", "edge_tts", "--voice", voice, "--text", text, "--write-media", output_path]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"Error generating TTS audio: {e}")
        return False

def generate_flux_image(prompt: str, output_path: str, retries: int = 3) -> bool:
    """
    Uses Pollinations.ai (Flux model) with robust retry logic.
    """
    for attempt in range(retries):
        try:
            # Increase delay between requests to be respectful to the free API
            wait_time = 10 * (attempt + 1)
            if attempt > 0:
                print(f"     [Flux] Retry {attempt}/{retries} after {wait_time}s...")
            time.sleep(wait_time) 
            
            print(f"     [Flux] Generating cinematic image (Attempt {attempt+1})...")
            encoded_prompt = requests.utils.quote(prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&model=flux&nologo=true&seed={int(time.time())}"
            
            res = requests.get(url, timeout=45)
            res.raise_for_status()
            
            with open(output_path, "wb") as f:
                f.write(res.content)
            return True
        except Exception as e:
            print(f"     [Flux] Attempt {attempt+1} failed: {e}")
            if attempt == retries - 1:
                return False
    return False

def fetch_pexels_video(query: str, output_path: str) -> bool:
    """
    Searches Pexels API. If the specific query fails, it tries broader terms.
    """
    api_key = os.getenv("PEXELS_API_KEY")
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

