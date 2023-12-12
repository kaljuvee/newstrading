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
CONF_CONFIG = 'st/data/confidence.csv'

def clean_text(raw_html):
    cleantext = BeautifulSoup(raw_html, "lxml").text
    return cleantext

def fetch_news(rss_dict, confidence_df):
    cols = ['ticker', 'title', 'published_gmt', 'link', 'topic', 'confidence']
    all_news_items = []

    for key, rss_url in rss_dict.items():
        feed = feedparser.parse(rss_url)

        for newsitem in feed['items']:
            last_subject = newsitem['tags'][-1]['term'] if 'tags' in newsitem and newsitem['tags'] else None
            # Lookup the confidence value based on the topic
            confidence = confidence_df[confidence_df['topic'] == last_subject]['confidence'].iloc[0] if any(confidence_df['topic'] == last_subject) else None
            all_news_items.append({
                'ticker': key,
                # Creating a hyperlink for the title
                'title': f"<a href='{newsitem['link']}' target='_blank'>{newsitem['title']}</a>",
                'published_gmt': newsitem['published'],
                'link': newsitem['link'],
                'topic': last_subject,
                'confidence': confidence
            })

    df = pd.DataFrame(all_news_items, columns=cols)
    return df


def load_config():
    try:
        with open(RSS_CONFIG, 'r') as file:
            rss_dict = yaml.safe_load(file)
    except Exception as e:
        st.error(f"Error loading {RSS_CONFIG}: {e}")
        return None
    return rss_dict

def load_conf_df():
    try:
        confidence_df = pd.read_csv(CONF_CONFIG)
    except Exception as e:
        st.error(f"Error loading {CONF_CONFIG}: {e}")
        return None
    return confidence_df

def main():
    # Load config only once
    if 'rss_dict' not in st.session_state:
        st.session_state.rss_dict = load_config()

    if 'confidence_df' not in st.session_state:
        st.session_state.confidence_df = load_conf_df()
    
    if st.session_state.rss_dict is None or st.session_state.confidence_df is None:
        st.error("Failed to load configuration.")
        return

    # Update Button
    if st.button('Update'):
        st.session_state.news_df = fetch_news(st.session_state.rss_dict, st.session_state.confidence_df)

    # Initial fetch or fetch every 5 minutes
    if 'last_updated' not in st.session_state or time.time() - st.session_state.last_updated > 300:
        news_df = fetch_news(st.session_state.rss_dict, st.session_state.confidence_df)
        st.session_state.last_updated = time.time()

    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"Last updated (GMT): {last_updated}")

    # Display specific columns from the DataFrame
    if 'news_df' in st.session_state:
    # Convert DataFrame to HTML and then use st.markdown to render it
        html = st.session_state.news_df.to_html(escape=False, index=False)
        st.markdown(html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

