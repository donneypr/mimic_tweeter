import requests
import json
import tweepy
import os
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM

# Initialize the model
model = OllamaLLM(model="llama3")

# Load environment variables from .env file
load_dotenv()

# Twitter API credentials
api_key = os.getenv("TWITTER_API_KEY")
api_secret = os.getenv("TWITTER_API_SECRET")
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# Initialize Tweepy client
client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

def get_all_tweets(username):
    """
    Retrieve all tweets from a given Twitter username.
    
    Parameters:
    username (str): The Twitter handle of the user whose tweets are to be fetched.
    
    Returns:
    list: A list containing the text of each tweet if successful, otherwise an empty list.
    """
    url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}"
    try:
        r = requests.get(url)
        if r.status_code != 200:
            print(f"Error: Received status code {r.status_code}")
            return []
        
        html = r.text
        
        # Define the start and end of the JSON data block within the HTML
        start_str = '<script id="__NEXT_DATA__" type="application/json">'
        end_str = '</script></body></html>'

        if start_str not in html or end_str not in html:
            print("Error: Could not find the expected JSON block in the HTML.")
            return []

        # Extract and parse JSON data
        start_index = html.index(start_str) + len(start_str)
        end_index = html.index(end_str, start_index)
        json_str = html[start_index:end_index]
        data = json.loads(json_str)

        # Extract tweet text content
        entries = data["props"]["pageProps"]["timeline"]["entries"]
        tweets = []
        
        for entry in entries:
            tweet_text = entry["content"]["tweet"]["full_text"]
            tweets.append(tweet_text)

        return tweets

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def generate_tweet_from_style(tweets):
    """
    Generate a tweet imitating the style of a given user's tweet history.
    
    Parameters:
    tweets (list): A list of tweets in text format from which to derive the user's style.
    
    Returns:
    str: A generated tweet in the style of the provided tweets.
    """
    tweet_history = "\n".join(tweets)

    prompt = (
        f"Here are some tweets by Playboi Carti:\n{tweet_history}\n\n"
        "Can you imitate Playboi Carti and give me a tweet he would say\n"
        "- No explanation, no URLs, just the tweet itself."
    )
    
    # Generate tweet using the LLaMA3 model
    result = model.invoke(input=prompt)
    generated_tweet = result.strip()
    print("Generated Tweet:", generated_tweet)
    return generated_tweet

# Main logic to retrieve tweets and post a generated tweet
tweets = get_all_tweets("playboicarti")

if tweets:
    generated_tweet = generate_tweet_from_style(tweets)
    try:
        # Attempt to post the generated tweet
        response = client.create_tweet(text=generated_tweet)
        print("Tweet posted successfully:", response.data)
    except Exception as e:
        print(f"Error posting tweet: {e}")
else:
    print("No tweets found for Playboi Carti.")
