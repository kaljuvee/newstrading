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

st.title('Real-Time Press Release Updates - Biotech')

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

    return pd.DataFrame(all_news_items, columns=cols)

def load_config():
    try:
        with open(RSS_CONFIG, 'r') as file:
            rss_dict = yaml.safe_load(file)
    except Exception as e:
        st.error(f"Error loading {RSS_CONFIG}: {e}")
        return None
    return rss_dict

def main():
    st.title("Biotech News Aggregator")
    rss_dict = load_config()
    
    if rss_dict is None:
        st.error("Failed to load RSS feed configuration.")
        return

    news_df = fetch_news(rss_dict)
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"Last updated: {last_updated}")
    st.dataframe(news_df)

if __name__ == "__main__":
    main()
