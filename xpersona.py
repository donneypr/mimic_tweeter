import requests
import json
import os
from dotenv import load_dotenv

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

load_dotenv()

tweets = get_all_tweets("playboicarti")

tweets_array = [tweet for tweet in tweets]

print(tweets_array)


