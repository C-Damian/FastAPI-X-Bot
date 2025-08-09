#!/usr/bin/env python3
"""
Automated poster script for FastAPI X Bot
This script can be called by cron jobs to automatically post tips to Twitter
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path so we can import from main
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import get_tip_for_posting
from db import get_db

def daily_posting_routine():
    """
    Main function to be called by cron job
    """
    print(f"Starting daily posting routine at {datetime.utcnow()}")
    
    try:
        # Get database session
        db = next(get_db())

        # This function already posts to Twitter and updates the DB
        tip_data = get_tip_for_posting(db)

        if not tip_data:
            print("No tips available for posting today")
            return

        # Log the outcome (avoid re-posting here)
        if tip_data.get("tweet_posted"):
            print(
                f"Successfully posted. Tweet ID: {tip_data.get('tweet_id')}, "
                f"Category: {tip_data.get('category_id')}"
            )
        else:
            print("Tweeting was attempted but reported as not posted.")

    except Exception as e:
        print(f"Error in daily posting routine: {str(e)}")
    finally:
        try:
            if 'db' in locals() and db is not None:
                db.close()
        finally:
            print(f"Daily posting routine completed at {datetime.utcnow()}")

if __name__ == "__main__":
    # This allows the script to be run directly
    daily_posting_routine() 