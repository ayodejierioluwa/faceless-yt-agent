import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def generate_video_script(topic: str, feedback_context: str = "") -> dict:
    """
    Calls the Google Gemini API to generate a video script, title, description, and scene descriptions.
    Includes feedback_context to adapt based on historic channel performance.
    Returns a dictionary structured as follows:
    {
      "title": "...",
      "description": "...",
      "scenes": [
        {
          "narration": "...",
          "search_term": "..."
        }
      ]
    }
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("Warning: GOOGLE_API_KEY not set. Returning a mock script.")
        return get_mock_script(topic)
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an elite, highly viral YouTube Shorts creator. Your task is to generate a fast-paced, highly engaging video script about: {topic}.
    The video MUST strictly follow this Shorts retention architecture:
    1. Scene 1 MUST be a powerful, disruptive "Hook" that immediately grabs attention.
    2. Scenes 2-4 MUST build extreme value and keep the pace fast.
    3. The final scene MUST contain a strong Call to Action.
    
    {feedback_context}
    
    The video should be under 60 seconds (about 120-140 words max total).
    
    Return the result strictly as a JSON object with the following schema:
    {{
      "title": "An engaging, clickbaity Title that builds curiosity",
      "description": "A brief description with 3 relevant hashtags",
      "scenes": [
        {{
          "narration": "The spoken voiceover text for this scene. Each scene narration MUST be 3 to 4 sentences (approx 35-45 words) to ensure the total video is 50-60 seconds long.",
          "search_term": "A detailed, cinematic prompt for an AI image generator (e.g. 'cinematic close up of a robot working in a dark lab, 4k, realistic')"
        }}
      ]
    }}
    
    Ensure there are exactly 6 scenes. The narration MUST be engaging, directly spoken, and instantly gripping.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.8
            )
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        print(f"Error calling Google Gemini API: {type(e).__name__}: {e}")
        return get_mock_script(topic)

def get_mock_script(topic: str) -> dict:
    """Fallback script generation for tests without an API key."""
    return {
        "title": "The Impact of AI!",
        "description": "A quick look at how AI is shaping the future. #AI #Future #Tech",
        "scenes": [
            {
                "narration": f"Did you know {topic} is changing the world right now?",
                "search_term": "futuristic technology city skyline"
            },
            {
                "narration": "Millions of jobs are being transformed every single day.",
                "search_term": "office workers with futuristic holographic displays"
            },
            {
                "narration": "But this isn't something to fear, it's a massive opportunity.",
                "status": "A person standing on a mountain peak looking at a digital sunrise"
            },
            {
                "narration": "Learn how to adapt and thrive in this new era.",
                "search_term": "student wearing VR headset in a library"
            },
            {
                "narration": "Like and subscribe for more tech updates!",
                "search_term": "futuristic subscribe button animation"
            }
        ]
    }

if __name__ == "__main__":
    script_data = generate_video_script("Artificial Intelligence replacing fast food workers")
    print(json.dumps(script_data, indent=2))
