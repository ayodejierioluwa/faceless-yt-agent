import time
import schedule
import os
import sys

# Append parent dir so 'from src...' imports work correctly if run from anywhere
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the main workflow from main.py
# We will wrap it in a try-except so an error doesn't kill the infinite loop
from main import main as execute_workflow

def job():
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Automatic YouTube Workflow Triggered!")
    try:
        execute_workflow()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Workflow finished successfully.")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error running workflow: {e}")

def run_scheduler():
    print("YouTube Agent Scheduler initialized.")
    print("Optimal Shorts posting times (12:00 PM and 6:00 PM) have been loaded.")
    
    # Schedule the jobs at Peak Optimal Times for YouTube Shorts
    schedule.every().day.at("12:00").do(job)
    schedule.every().day.at("18:00").do(job)
    
    print("Scheduler is actively running. Press Ctrl+C to stop.")
    
    # Keep the script running forever
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # Also run it once immediately on startup so the user can test the pipeline
    print("Running initial execution just for testing...")
    job()
    
    run_scheduler()
