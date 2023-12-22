import streamlit as st
import tweepy
import pandas as pd
from datetime import datetime, timedelta
import time

# Twitter API credentials
API_KEY = '0XcG2YV6k9bNeFJhQ0ipWXBeY'
API_SECRET_KEY = 'X2jqSTAni2dgYOTKiKkhawEsQY7iKM7r33uJIVDLmyA9GD3VHc'
ACCESS_TOKEN = '16938181-BrOM6V1LTZL9nvJDPyCZhYkEmQwvXrYj2eeCr9elk'
ACCESS_TOKEN_SECRET = 'n6VD4NOrn3ACvkWRYy9YsREsNQSsJDAQTdF5zakpZOIwQ'

# Twitter handles to monitor
TWITTER_HANDLES = ["BiotechWorld", "Biotechnology"]

# Initialize Tweepy
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

def get_latest_tweets(twitter_handles):
    tweets_data = []

    for handle in twitter_handles:
        # Fetch latest tweets from the handle
        tweets = api.user_timeline(screen_name=handle, tweet_mode="extended", count=5, exclude_replies=True)
        for tweet in tweets:
            tweets_data.append({
                "Time": tweet.created_at,
                "User": handle,
                "Tweet": tweet.full_text
            })

    return pd.DataFrame(tweets_data)

def main():
    st.title("Twitter Feed Aggregator")

    # Fetch and display tweets
    if st.button('Fetch Latest Tweets'):
        with st.spinner('Fetching tweets...'):
            tweets_df = get_latest_tweets(TWITTER_HANDLES)
            st.write(tweets_df)

    # Auto-update tweets every minute
    if st.checkbox('Auto Fetch Tweets Every Minute'):
        while True:
            time.sleep(60)
            tweets_df = get_latest_tweets(TWITTER_HANDLES)
            st.write(tweets_df)

if __name__ == "__main__":
    main()
