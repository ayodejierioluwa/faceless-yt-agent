import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

def send_upload_notification(video_title: str, video_url: str, script_text: str):
    """
    Sends an email notification via Gmail to alert the user of a new upload.
    """
    load_dotenv()
    
    sender_email = os.getenv("EMAIL_SENDER")
    app_password = os.getenv("EMAIL_APP_PASSWORD")
    receiver_email = os.getenv("EMAIL_RECEIVER", sender_email) # Defaults to sending it to themselves
    
    if not sender_email or not app_password:
        print("Warning: Email credentials not found in .env. Skipping notification.")
        return False
        
    try:
        # Construct the email body
        msg = MIMEMultipart()
        msg['From'] = f"YouTube Agent <{sender_email}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"New YouTube Upload! '{video_title}'"
        
        body = f"""
<h2>Your Bot just uploaded a new video!</h2>
<p><strong>Title:</strong> {video_title}</p>
<p><strong>YouTube Link:</strong> <a href="{video_url}">{video_url}</a> <i>(It may take a few minutes for YouTube processing to finish)</i></p>

<hr>
<h3>Script Used:</h3>
<p style="white-space: pre-wrap;">{script_text}</p>
"""
        
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, app_password)
        
        # Send and gracefully close
        server.send_message(msg)
        server.quit()
        
        print(f"Notification email successfully sent to {receiver_email}!")
        return True
        
    except Exception as e:
        print(f"Failed to send email notification: {e}")
        return False
