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

def process_data(df):
    """Process the dataframe for hyperlinks."""
    df['symbol'] = '<a href="https://finance.yahoo.com/quote/' + df['ticker'] + '" target="_blank">' + df['ticker'] + '</a>'
    df['title'] = '<a href="' + df['link'] + '" target="_blank">' + df['title'] + '</a>'
    return df
    
@st.cache_data(ttl=60, show_spinner=False)
def fetch_news(rss_dict, confidence_df):
    if 'news_item_cache' not in st.session_state:
        st.session_state.news_item_cache = {}

    cols = ['ticker', 'title', 'published_gmt', 'topic', 'link', 'confidence']
    new_news_items = []

    for key, rss_url in rss_dict.items():
        feed = feedparser.parse(rss_url)

        for newsitem in feed['items']:
            if newsitem['link'] not in st.session_state.news_item_cache:
                last_subject = newsitem['tags'][-1]['term'] if 'tags' in newsitem and newsitem['tags'] else None
                confidence = confidence_df[confidence_df['topic'] == last_subject]['confidence'].iloc[0] if any(confidence_df['topic'] == last_subject) else None

                news_data = {
                    'ticker': key,
                    'title': newsitem['title'],
                    'published_gmt': newsitem['published'],
                    'topic': last_subject,
                    'link': newsitem['link'],
                    'confidence': confidence
                }

                new_news_items.append(news_data)
                st.session_state.news_item_cache[newsitem['link']] = news_data

    # Check if there are new items to add
    if new_news_items:
        new_df = pd.DataFrame(new_news_items, columns=cols)
        if 'news_df' in st.session_state and not st.session_state.news_df.empty:
            # Combine with existing DataFrame
            combined_df = pd.concat([st.session_state.news_df, new_df], ignore_index=True)
            st.session_state.news_df = combined_df
        else:
            st.session_state.news_df = new_df
    # Return either the updated or the existing DataFrame
    return st.session_state.news_df if 'news_df' in st.session_state else pd.DataFrame(columns=cols)



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
    # Load configuration
    if 'rss_dict' not in st.session_state:
        st.session_state.rss_dict = load_config()

    if 'confidence_df' not in st.session_state:
        st.session_state.confidence_df = load_conf_df()

    if st.session_state.rss_dict is None or st.session_state.confidence_df is None:
        st.error("Failed to load configuration.")
        return

    # Manual update button
    if st.button('Update'):
        with st.spinner('Fetching news...'):
            st.session_state.news_df = fetch_news(st.session_state.rss_dict, st.session_state.confidence_df)
            st.session_state.news_df = process_data(st.session_state.news_df)

    # Toggle for automatic fetching
    if st.checkbox('Auto Fetch News Every Minute', value=st.session_state.get('auto_fetch', False)):
        st.session_state['auto_fetch'] = True
        while st.session_state['auto_fetch']:
            with st.spinner('Fetching news...'):
                st.session_state.news_df = fetch_news(st.session_state.rss_dict, st.session_state.confidence_df)
                st.session_state.news_df = process_data(st.session_state.news_df)
            time.sleep(180)
            st.rerun()
    else:
        st.session_state['auto_fetch'] = False

    # Display news
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"Last updated (GMT): {last_updated}")
    if 'news_df' in st.session_state:
        display_df = st.session_state.news_df.copy()
        display_df['published_gmt'] = pd.to_datetime(display_df['published_gmt'])
        display_df = display_df.sort_values(by='published_gmt', ascending=False)
        html = display_df.to_html(escape=False, index=False)
        st.markdown(html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()


