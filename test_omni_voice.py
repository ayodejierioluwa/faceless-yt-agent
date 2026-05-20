import os
from dotenv import load_dotenv
from src.media import generate_audio

if __name__ == "__main__":
    load_dotenv()
    print("Testing Gemini Omni Native Audio Generation...")
    
    text = "The Dyatlov Pass Incident remains one of the most chilling unexplained mysteries of the 20th century. What really happened to those nine hikers on that frozen mountain?"
    output = "test_omni_audio.wav"
    
    success = generate_audio(text, output)
    
    if success:
        print(f"Success! Audio saved to {output}. Please listen to verify the expressive quality.")
    else:
        print("Failed to generate audio. Check your GOOGLE_API_KEY and model access.")
