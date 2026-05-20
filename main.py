import os
import shutil
import time
from dotenv import load_dotenv

from src.trends import get_trending_topic
from src.script_writer import generate_video_script
from src.media import generate_audio, fetch_background_music, generate_veo_video
from src.video_editor import assemble_video
from src.youtube_uploader import upload_video

from src.feedback import get_channel_feedback
from src.notifier import send_upload_notification

def main():
    print("Starting Faceless Video Agent Workflow (Google AI Edition)...")
    
    # 1. Setup workspace
    output_dir = "output"
    if os.path.exists(output_dir):
        print(f"Cleaning up old {output_dir} directory...")
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # NEW: AI Quality Feedback Loop
    print("\n[Step 0] Analyzing past YouTube performance to improve quality...")
    try:
        feedback_context = get_channel_feedback()
    except Exception as e:
        print(f"Warning: Could not get YouTube feedback (likely auth issue): {e}")
        feedback_context = ""
    
    # 2. Get Topic
    topic = get_trending_topic()
    print(f"\n[Step 1] Selected Topic: {topic}")
    
    # 3. Generate Script
    print("\n[Step 2] Generating Script with Gemini 1.5 Flash...")
    script_data = generate_video_script(topic, feedback_context)
    
    title = script_data.get("title", 'Trending AI Shorts')
    description = script_data.get("description", '#AI #Shorts')
    scenes = script_data.get("scenes", [])
    
    print(f"Title: {title}")
    print(f"Number of Scenes: {len(scenes)}")
    
    # 4. Gather Assets
    print("\n[Step 3] Gathering Media Assets (Flux -> Pexels)...")
    asset_paths = []
    audio_paths = []
    narrations = []
    
    for idx, scene in enumerate(scenes):
        narration = scene.get('narration')
        prompt = scene.get('search_term') # This is our AI prompt
        print(f"  -> Scene {idx+1}: {narration[:40]}...")
        
        # Audio
        audio_path = os.path.join(output_dir, f"scene_{idx}_audio.mp3")
        a_success = generate_audio(narration, audio_path)
        
        # Asset Selection: Strictly Google Veo / Omni Video Generation
        asset_path = None
        success = False
        
        temp_path = os.path.join(output_dir, f"scene_{idx}_veo.mp4")
        
        # Retry mechanism for strict video generation to ensure we NEVER fall back to static images
        for attempt in range(3):
            if generate_veo_video(prompt, temp_path):
                asset_path = temp_path
                success = True
                print(f"     [Success] Google Omni Premium Video generated on attempt {attempt+1}.")
                break
            else:
                print(f"     [Warning] Video generation failed on attempt {attempt+1}. Retrying in 10s...")
                time.sleep(10)
                
        if not success:
            print(f"     [Critical Error] Failed to generate True Video for scene {idx+1}. Agent cannot proceed without moving video.")

        
        if a_success and success:
             asset_paths.append(asset_path)
             audio_paths.append(audio_path)
             narrations.append(narration)
        else:
             print(f"     [Failed] Could not acquire assets for Scene {idx+1}. Skipping.")
    
    # 5. Assemble Video
    print("\n[Step 4] Assembling Final Video with Background Music...")
    final_output_path = os.path.join(output_dir, "final_video.mp4")
    music_path = os.path.join(output_dir, "background_music.mp3")
    
    # Download background music
    fetch_background_music(music_path)
    
    if len(asset_paths) == 0:
        print("Error: No assets downloaded. Workflow failed.")
        return
        
    v_success = assemble_video(asset_paths, audio_paths, final_output_path, music_path, narrations=narrations)
    if not v_success:
        print("Error during video assembly.")
        return
        
    print(f"\nVideo successfully saved to: {final_output_path}")
    
    # 6. Upload
    print("\n[Step 5] Uploading to YouTube...")
    load_dotenv()
    if os.getenv("UPLOAD_ENABLED", "False").lower() == "true":
        success = upload_video(final_output_path, title, description)
        if success:
            print("Upload Complete.")
            youtube_fake_url = f"https://studio.youtube.com/channel/"
            
            # Send Email Notification
            full_script_text = "\n".join([f"Scene {i+1}: {s.get('narration', '')}" for i, s in enumerate(scenes)])
            send_upload_notification(title, youtube_fake_url, full_script_text)
            print("Workflow Complete!")
    else:
        print("Upload skipped. Set UPLOAD_ENABLED=True in .env to enable auto-uploading.")

if __name__ == "__main__":
    main()
