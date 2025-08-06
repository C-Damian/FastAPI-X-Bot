import http.client
import json
import os
import ssl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def post_tweet(tweet_content: str):
    """
    Post a tweet to Twitter/X using the API
    
    Args:
        tweet_content (str): The content of the tweet to post
        
    Returns:
        tuple: (success: bool, tweet_id: str or None)
    """
    # Create SSL context that doesn't verify certificates (for development)
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    conn = http.client.HTTPSConnection("api.x.com", context=context)
    
    payload = json.dumps({
        "text": tweet_content
    })
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': os.getenv('TWITTER_AUTH_HEADER'),
        'Cookie': os.getenv('TWITTER_COOKIE')
    }
    
    try:
        conn.request("POST", "/2/tweets", payload, headers)
        res = conn.getresponse()
        data = res.read()
        
        if res.status == 201:  # Success
            response_data = json.loads(data.decode("utf-8"))
            tweet_id = response_data.get('data', {}).get('id')
            print(f"Tweet posted successfully! Tweet ID: {tweet_id}")
            return True, tweet_id
        else:
            print(f"Failed to post tweet. Status: {res.status}")
            print(f"Response: {data.decode('utf-8')}")
            return False, None
            
    except Exception as e:
        print(f"Error posting tweet: {str(e)}")
        return False, None
    finally:
        conn.close()

# For testing purposes
if __name__ == "__main__":
    test_tweet = "Hello from FastAPI X Bot! 🤖 #TechTip #Coding"
    success, tweet_id = post_tweet(test_tweet)
    if success:
        print(f"Test tweet posted with ID: {tweet_id}")
    else:
        print("Test tweet failed")