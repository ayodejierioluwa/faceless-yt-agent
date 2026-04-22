import json
from .youtube_uploader import authenticate_youtube

def get_channel_feedback() -> str:
    """
    Fetches the 5 most recent videos from the user's channel and constructs
    a feedback summary string regarding their view counts.
    Returns empty string if it fails or there are no videos.
    """
    youtube = authenticate_youtube()
    if not youtube:
        return ""
        
    try:
        # First get the user's own channel's 'uploads' playlist ID
        channel_response = youtube.channels().list(
            part='contentDetails',
            mine=True
        ).execute()
        
        if not channel_response.get('items'):
            # The channel might not be fully initialized or something went wrong
            return ""
            
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Get the latest 5 videos uploaded to the channel
        playlist_response = youtube.playlistItems().list(
            part='contentDetails,snippet',
            playlistId=uploads_playlist_id,
            maxResults=5
        ).execute()
        
        video_ids = [item['contentDetails']['videoId'] for item in playlist_response.get('items', [])]
        
        if not video_ids:
            return ""
            
        # Get statistics for those specific video IDs
        stats_response = youtube.videos().list(
            part='snippet,statistics',
            id=','.join(video_ids)
        ).execute()
        
        feedback_lines = ["\n[CHANNEL PERFORMANCE HISTORY FOR CONTEXT]"]
        feedback_lines.append("Here is the performance of the latest videos on this channel:")
        
        for item in stats_response.get('items', []):
            title = item['snippet']['title']
            views = item['statistics'].get('viewCount', 0)
            likes = item['statistics'].get('likeCount', 0)
            feedback_lines.append(f" - Title: '{title}' | Views: {views} | Likes: {likes}")
            
        feedback_lines.append("\nUSE THIS DATA DIRECTLY IN YOUR SCRIPT: Analyze which titles or themes above got the most views.")
        feedback_lines.append("Try to mimic the energy or phrasing of successful videos, and explicitly pivot away from topics that got lower views.")
        
        return "\n".join(feedback_lines)
        
    except Exception as e:
        print(f"Warning: Could not fetch channel feedback: {e}")
        return ""
