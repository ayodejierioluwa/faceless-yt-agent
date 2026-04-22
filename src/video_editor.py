import os
import PIL.Image

# Monkey-patch PIL for Compatibility with MoviePy 1.0.3 and newer Pillow (10+)
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, concatenate_videoclips, CompositeAudioClip
from moviepy.audio.fx.all import volumex

def create_ken_burns_clip(image_path: str, duration: float, target_size=(1080, 1920)) -> VideoFileClip:
    """
    Creates a Video clip from a static image with a slow zoom (Ken Burns effect).
    """
    # Load the image
    img_clip = ImageClip(image_path).set_duration(duration)
    
    # Simple zoom effect: Start at 100% and go to 115% scale
    def zoom_effect(t):
        return 1.0 + 0.15 * (t / duration)
        
    # Resize to have a dynamic zoom
    animated_clip = img_clip.resize(lambda t: zoom_effect(t))
    
    # Resize height to target height (1920) and keep aspect ratio
    animated_clip = animated_clip.resize(height=target_size[1])
    
    # Center crop to target width (1080)
    if animated_clip.w > target_size[0]:
        animated_clip = animated_clip.crop(x_center=animated_clip.w/2, width=target_size[0])
        
    return animated_clip

def assemble_video(asset_paths: list, audio_paths: list, output_path: str, music_path: str = None) -> bool:
    """
    Takes a list of pre-downloaded video or image assets and a list of generated audio clips.
    Mixes in background music if provided.
    """
    if len(asset_paths) != len(audio_paths):
        print("Error: The number of assets and audio clips must match.")
        return False
        
    try:
        scene_clips = []
        
        for asset_path, aud_path in zip(asset_paths, audio_paths):
            if not os.path.exists(asset_path) or not os.path.exists(aud_path):
                print(f"Warning: Missing file {asset_path} or {aud_path}. Skipping scene.")
                continue
                
            audio_clip = AudioFileClip(aud_path)
            duration = audio_clip.duration
            
            # Check if asset is image or video
            is_image = asset_path.lower().endswith(('.png', '.jpg', '.jpeg'))
            
            if is_image:
                print(f"     [VideoEditor] Animating image scene: {os.path.basename(asset_path)}")
                scene_clip = create_ken_burns_clip(asset_path, duration)
            else:
                print(f"     [VideoEditor] Processing video scene: {os.path.basename(asset_path)}")
                video_clip = VideoFileClip(asset_path)
                
                # Subclip or loop
                if video_clip.duration < duration:
                    # Loop video if shorter than audio
                    scene_clip = video_clip.loop(duration=duration)
                else:
                    scene_clip = video_clip.subclip(0, duration)
                
                # Enforce vertical size 1080x1920
                scene_clip = scene_clip.resize(height=1920, width=1080)
            
            # Set the audio
            scene_clip = scene_clip.set_audio(audio_clip)
            scene_clips.append(scene_clip)
            
        if not scene_clips:
            print("Error: No valid scenes could be assembled.")
            return False
            
        # Concatenate all scenes together
        final_video = concatenate_videoclips(scene_clips, method="compose")
        
        # Add background music if provided
        if music_path and os.path.exists(music_path):
            print(f"     [VideoEditor] Mixing background music: {os.path.basename(music_path)}")
            bg_music = AudioFileClip(music_path).fx(volumex, 0.15) # 15% volume
            # Loop music if shorter than video, or cut if longer
            if bg_music.duration < final_video.duration:
                bg_music = bg_music.loop(duration=final_video.duration)
            else:
                bg_music = bg_music.subclip(0, final_video.duration)
            
            # Composite with original audio
            new_audio = CompositeAudioClip([final_video.audio, bg_music])
            final_video = final_video.set_audio(new_audio)
        
        # Write the final result
        print(f"Rendering final video to {output_path}...")
        final_video.write_videofile(
            output_path, 
            fps=30, 
            codec="libx264", 
            audio_codec="aac",
            preset="ultrafast",
            threads=4
        )
        
        # Free up resources
        final_video.close()
        for clip in scene_clips:
            clip.close()
            
        return True
        
    except Exception as e:
        print(f"Error assembling video: {e}")
        return False
