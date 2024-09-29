import requests
import json
import tweepy
import os
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM

model = OllamaLLM(model="llama3")

load_dotenv()

api_key = os.getenv("TWITTER_API_KEY")
api_secret = os.getenv("TWITTER_API_SECRET")
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

client = tweepy.Client(
    bearer_token=bearer_token,
    consumer_key=api_key,
    consumer_secret=api_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

def get_all_tweets(username):
    url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}"
    try:
        r = requests.get(url)
        if r.status_code != 200:
            print(f"Error: Received status code {r.status_code}")
            return []
        
        html = r.text
        
        start_str = '<script id="__NEXT_DATA__" type="application/json">'
        end_str = '</script></body></html>'

        if start_str not in html or end_str not in html:
            print("Error: Could not find the expected JSON block in the HTML.")
            return []

        start_index = html.index(start_str) + len(start_str)
        end_index = html.index(end_str, start_index)
        json_str = html[start_index:end_index]
        data = json.loads(json_str)

        entries = data["props"]["pageProps"]["timeline"]["entries"]
        tweets = []
        
        for entry in entries:
            tweet_text = entry["content"]["tweet"]["full_text"]
            tweets.append(tweet_text)

        return tweets

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

# Function to generate a tweet in Playboi Carti's style
def generate_tweet_from_style(tweets):
    tweet_history = "\n".join(tweets)

    # Describe Playboi Carti's style and prompt the model
    # prompt = (
    #     f"Here are some tweets by Playboi Carti:\n{tweet_history}\n\n"
    #     "Generate 1 new tweet in Playboi Carti's unique style. The tweet should:\n"
    #     "- Be in lowercase\n"
    #     "- Use fragmented sentences\n"
    #     "- Include random capitalizations and eccentric spellings\n"
    #     "- Be casual and spontaneous in tone\n"
    #     "- Incorporate emojis like 🧛🏿‍♂️, 🚀, and ❤️\n"
    #     "- The tweet should not have any URLs\n"
    # )

    prompt = (
     f"Here are some tweets by Playboi Carti:\n{tweet_history}\n\n"
        "Can you imitate Playboi Carti and give me a tweet he would say\n"
        "There must not be any URLs in the tweet\n"
    )
    
    result = model.invoke(input=prompt)
    generated_tweet = result.strip()
    print("Generated Tweet:", generated_tweet)
    return generated_tweet

tweets = get_all_tweets("playboicarti")

if tweets:
    generated_tweet = generate_tweet_from_style(tweets)
    try:
        response = client.create_tweet(text=generated_tweet)
        print("Tweet posted successfully:", response.data)
    except Exception as e:
        print(f"Error posting tweet: {e}")
else:
    print("No tweets found for Playboi Carti.")
