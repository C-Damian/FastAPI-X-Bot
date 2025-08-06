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
from postTweet import post_tweet_to_twitter

def daily_posting_routine():
    """
    Main function to be called by cron job
    """
    print(f"Starting daily posting routine at {datetime.utcnow()}")
    
    try:
        # Get database session
        db = next(get_db())
        
        # Get a tip for posting (this includes marking it as posted and generating a new one)
        tip_data = get_tip_for_posting(db)
        
        if not tip_data:
            print("No tips available for posting today")
            return
        
        # Format the tweet content
        tweet_content = f"{tip_data['title']}\n\n{tip_data['content']}"
        
        if tip_data['code']:
            tweet_content += f"\n\n{tip_data['code']}"
        
        tweet_content += f"\n\n{tip_data['hashtags']}"
        
        print(f"Preparing to post: {tweet_content[:100]}...")
        
        # Post to Twitter
        success, tweet_id = post_tweet_to_twitter(tweet_content)
        
        if success:
            print(f"Successfully posted tip to Twitter! Tweet ID: {tweet_id}")
            print(f"Tip category: {tip_data['category_id']}")
        else:
            print("Failed to post to Twitter")
            
    except Exception as e:
        print(f"Error in daily posting routine: {str(e)}")
    finally:
        db.close()
        print(f"Daily posting routine completed at {datetime.utcnow()}")

if __name__ == "__main__":
    # This allows the script to be run directly
    daily_posting_routine() 