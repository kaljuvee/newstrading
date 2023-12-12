import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import db_util
import pytz
import date_util
import feedparser
import yaml
from bs4 import BeautifulSoup
from datetime import datetime
import time

st.title("Biotech News Aggregator")

# Hardcoded sector
sector = 'biotech'
RSS_CONFIG = 'st/data/biotech.yaml'
confidence_file = 'st/data/confidence.yaml'

def clean_text(raw_html):
    cleantext = BeautifulSoup(raw_html, "lxml").text
    return cleantext

def fetch_news(rss_dict, confidence_map):
    cols = ['ticker', 'title', 'published_gmt', 'link', 'topic', 'confidence']
    all_news_items = []

    for key, rss_url in rss_dict.items():
        feed = feedparser.parse(rss_url)

        for newsitem in feed['items']:
            last_subject = newsitem['tags'][-1]['term'] if 'tags' in newsitem and newsitem['tags'] else None
            # Lookup the confidence value based on the topic
            confidence = confidence_map.get(last_subject, None)
            all_news_items.append({
                'ticker': key,
                'title': newsitem['title'],
                'published_gmt': newsitem['published'],
                'link': newsitem['link'],
                'topic': last_subject,
                'confidence': confidence
            })

    return pd.DataFrame(all_news_items, columns=cols)

def load_config():
    try:
        with open(RSS_CONFIG, 'r') as file:
            rss_dict = yaml.safe_load(file)
    except Exception as e:
        st.error(f"Error loading {RSS_CONFIG}: {e}")
        return None
    return rss_dict

def load_confidence_map():
    try:
        with open(confidence_file, 'r') as file:
            confidence_map = yaml.safe_load(file)
            if not isinstance(confidence_map, dict):
                st.error(f"Loaded data is not a dictionary. It's a {type(confidence_map)}.")
                return None
            return confidence_map
    except Exception as e:
        st.error(f"Error loading {confidence_file}: {e}")
        return None

def main():
    # Load config only once
    if 'rss_dict' not in st.session_state:
        st.session_state.rss_dict = load_config()

    if 'confidence_map' not in st.session_state:
        st.session_state.confidence_map = load_confidence_map()
        st.write(st.session_state.confidence_map)
    
    if st.session_state.rss_dict is None or st.session_state.confidence_map is None:
        st.error("Failed to load configuration.")
        return

    # Update Button
    if st.button('Update'):
        st.session_state.news_df = fetch_news(st.session_state.rss_dict)

    # Initial fetch or fetch every 5 minutes
    if 'last_updated' not in st.session_state or time.time() - st.session_state.last_updated > 300:
        news_df = fetch_news(st.session_state.rss_dict, st.session_state.confidence_map)
        st.session_state.last_updated = time.time()

    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"Last updated: {last_updated}")

    # Display specific columns from the DataFrame
    if 'news_df' in st.session_state:
        st.dataframe(st.session_state.news_df[['ticker', 'title', 'topic', 'published_gmt']])

if __name__ == "__main__":
    main()

