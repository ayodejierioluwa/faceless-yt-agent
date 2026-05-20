import random

def get_trending_topic() -> str:
    """
    Returns a highly viral, high-retention topic from the 'Dark History / Unexplained Mysteries' niche.
    This niche typically performs significantly better on YouTube Shorts than tech news.
    """
    viral_topics = [
        "The Dyatlov Pass Incident: What really happened to the 9 hikers?",
        "The Roanoke Colony: The entire village that vanished without a trace.",
        "The Dancing Plague of 1518: When hundreds danced themselves to death.",
        "The mysterious disappearance of the Flannan Isles Lighthouse keepers.",
        "The Voynich Manuscript: The book nobody can read.",
        "The horrifying truth behind the real Dracula: Vlad the Impaler.",
        "The unsettling mystery of the Mary Celeste ghost ship.",
        "The Tunguska Event: The massive explosion that flattened a forest with no crater.",
        "The grim reality of Victorian-era post-mortem photography.",
        "The baffling case of the Somerton Man."
    ]
    
    chosen = random.choice(viral_topics)
    return f"DARK HISTORY / MYSTERY: {chosen}"

if __name__ == "__main__":
    print(get_trending_topic())
