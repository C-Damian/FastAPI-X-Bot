import os
import json
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def post_tweet(tweet_content: str):
    """
    Post a tweet to Twitter/X using Tweepy
    
    Args:
        tweet_content (str): The content of the tweet to post
        
    Returns:
        tuple: (success: bool, tweet_id: str or None)
    """
    try:
        # Simulate your old payload step
        #payload = json.dumps({
        #    "text": tweet_content
        #})

        # Load payload back to dict so Tweepy can use it
        #payload_data = json.loads(payload)

        # Authenticate with Tweepy
        client = tweepy.Client(
            bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )

        # Post the tweet
        response = client.create_tweet(text=tweet_content)

        # Convert Tweepy response to dict
        response_data = json.loads(json.dumps(response.data))

        tweet_id = response_data.get("id")
        print(f"Tweet posted successfully! Tweet ID: {tweet_id}")
        return True, tweet_id

    except Exception as e:
        print(f"Error posting tweet: {str(e)}")
        return False, None


# Test run
if __name__ == "__main__":
    test_tweet = "Hello from FastAPI X Bot! 🤖 #TechTip #Coding"
    success, tweet_id = post_tweet(test_tweet)
    if success:
        print(f"Test tweet posted with ID: {tweet_id}")
    else:
        print("Test tweet failed")