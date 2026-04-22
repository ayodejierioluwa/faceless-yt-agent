import requests
import xml.etree.ElementTree as ET
import random

def get_trending_topic() -> str:
    """
    Fetches the latest news titles from an RSS feed to use as an interesting topic.
    Returns a string detailing the topic for the LLM to generate a script about.
    """
    try:
        # Use TechCrunch AI RSS feed as a sample source for trending AI news
        url = "https://techcrunch.com/category/artificial-intelligence/feed/"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        items = root.findall('.//item')
        
        if items:
            # Pick a recent top news item randomly from the latest 5
            chosen_item = random.choice(items[:5])
            title = chosen_item.find('title')
            # Extract text safely
            title_text = title.text if title is not None else "Unknown Title"
            
            return f"LATEST TRENDING AI NEWS: {title_text}"
            
    except Exception as e:
        print(f"Warning: Could not fetch RSS trends, falling back to a default topic. Error: {e}")
        
    # Fallback topic
    return "The Evolution of Generative AI and its impact on the Future of Work."

if __name__ == "__main__":
    print(get_trending_topic())
