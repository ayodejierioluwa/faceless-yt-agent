import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Scopes needed for uploading
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def authenticate_youtube():
    """
    Authenticates the user using client_secrets.json.
    Returns the YouTube service object.
    """
    creds = None
    # We look for a token file which stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed ({e}). Re-authenticating...")
                flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
                creds = flow.run_local_server(port=0)
        else:
            if not os.path.exists('client_secrets.json'):
                print("Missing 'client_secrets.json' file. Please obtain it from Google Cloud Console.")
                return None
                
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    return build('youtube', 'v3', credentials=creds)

def upload_video(video_path: str, title: str, description: str, category_id="28"):
    """
    Uploads a video to YouTube.
    """
    youtube = authenticate_youtube()
    if not youtube:
        return False
        
    print(f"Uploading {video_path} to YouTube...")
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'categoryId': category_id,
            'tags': ['AI', 'Tech', 'Shorts', 'Innovation'] # Default tags
        },
        'status': {
            'privacyStatus': 'private', # Default to private for review
            'selfDeclaredMadeForKids': False
        }
    }
    
    # Media payload
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype='video/mp4')
    
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )
    
    response = None
    try:
        print("Uploading... This might take a few minutes.")
        response = request.execute()
        print(f"Video id '{response['id']}' was successfully uploaded.")
        return True
    except Exception as e:
        print(f"An HTTP error occurred: {e}")
        return False
        
if __name__ == "__main__":
    print("This script is ready to authenticate. Ensure client_secrets.json is present.")
