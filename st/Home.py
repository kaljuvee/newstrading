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

st.title("Biotech News Aggregator")

# Hardcoded sector
sector = 'biotech'
RSS_CONFIG = 'st/biotech.yaml'


def clean_text(raw_html):
    cleantext = BeautifulSoup(raw_html, "lxml").text
    return cleantext

def fetch_news(rss_dict):
    cols = ['ticker', 'title', 'summary', 'published_gmt', 'description', 'link', 'language', 'topic', 'sector']
    all_news_items = []

    for key, rss_url in rss_dict.items():
        feed = feedparser.parse(rss_url)

        for newsitem in feed['items']:
            last_subject = newsitem['tags'][-1]['term'] if 'tags' in newsitem and newsitem['tags'] else None
            all_news_items.append({
                'ticker': key,
                'title': newsitem['title'],
                'summary': clean_text(newsitem['summary']),
                'published_gmt': newsitem['published'],
                'description': clean_text(newsitem['description']),
                'link': newsitem['link'],
                'language': newsitem.get('dc_language', None),
                'topic': last_subject,
                'sector': sector
            })

    df = pd.DataFrame(all_news_items, columns=cols)
    df['published_gmt'] = pd.to_datetime(df['published_gmt'])
    return df.sort_values(by='published_gmt', ascending=False)

def load_config():
    config_file = "biotech.yaml"
    try:
        with open(config_file, 'r') as file:
            rss_dict = yaml.safe_load(file)
    except Exception as e:
        st.error(f"Error loading {config_file}: {e}")
        return None
    return rss_dict

def main():
    # Load config only once
    if 'rss_dict' not in st.session_state:
        st.session_state.rss_dict = load_config()

    if st.session_state.rss_dict is None:
        st.error("Failed to load RSS feed configuration.")
        return

    # Update Button
    if st.button('Update'):
        st.session_state.news_df = fetch_news(st.session_state.rss_dict)

    # Initial fetch or fetch every 5 minutes
    if 'last_updated' not in st.session_state or time.time() - st.session_state.last_updated > 300:
        st.session_state.news_df = fetch_news(st.session_state.rss_dict)
        st.session_state.last_updated = time.time()

    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"Last updated: {last_updated}")

    # Display specific columns from the DataFrame
    if 'news_df' in st.session_state:
        st.dataframe(st.session_state.news_df[['ticker', 'title', 'topic', 'published_gmt']])

if __name__ == "__main__":
    main()

