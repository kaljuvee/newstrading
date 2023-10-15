
import pandas as pd
import feedparser
import yaml
from bs4 import BeautifulSoup
import time
from datetime import timedelta
import os
import pandas_gbq
from sqlalchemy import create_engine
from sqlalchemy import text
import argparse

# Database connection parameters (you'll need to fill these in)
db_params = {
    'dbname': 'altsignals-beta',
    'user': 'julian',
    'password': 'AltData2$2',
    'host': '34.88.153.82',
    'port': '5432',  # default is 5432 for PostgreSQL
}

sector = 'biotech'
# Initialize rss_dict as a global variable
rss_dict = {}

# Create a connection to the PostgreSQL database
engine = create_engine(f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}")

# Initialize added_links as an empty list
global added_links
added_links = []

def init_links():
    # Fetch distinct links from the database and populate the added_links list
    with engine.connect() as connection:
        result = connection.execute(text("SELECT DISTINCT link FROM news_item_sector"))
        added_links = [row[0] for row in result]

def clean_text(raw_html):
    cleantext = BeautifulSoup(raw_html, "lxml").text
    return cleantext

def fetch_news(rss_dict):
    cols = ['ticker', 'title', 'summary', 'published', 'description', 'link', 'language', 'subject', 'sector']
    all_news_items = []

    print("Starting new iteration...")
    print("Config for sector: ", rss_dict)
    for key, rss_url in rss_dict.items():
        print(f"Fetching news for ticker: {key}")
        feed = feedparser.parse(rss_url)

        for newsitem in feed['items']:
            last_subject = newsitem['tags'][-1]['term'] if 'tags' in newsitem and newsitem['tags'] else None
            all_news_items.append({
                'ticker': key,
                'title': newsitem['title'],
                'summary': clean_text(newsitem['summary']),
                'published': newsitem['published'],
                'description': clean_text(newsitem['description']),
                'link': newsitem['link'],
                'language': newsitem.get('dc_language', None),  # Extracted language from the provided feed
                'subject': last_subject,
                'sector': sector
            })

    return pd.DataFrame(all_news_items, columns=cols)

def process_news(df):
    df = df[~df['link'].isin(added_links)]
    if not df.empty:
        print("Writing new row for: ", df['ticker'])
        df.to_sql('news_item_sector', engine, if_exists='append', index=False)
        added_links.extend(df['link'].tolist())

    return df

def add_published_est(news_df):
    from datetime import timedelta
    import pandas as pd

    # Define the time difference between GMT and EST
    time_difference = timedelta(hours=5)

    # Convert the "published" column to datetime if not already in datetime format
    if news_df['published'].dtype != 'datetime64[ns]':
        news_df['published'] = pd.to_datetime(news_df['published'], format='%a, %d %b %Y %H:%M %Z')

    # Adjust the time to US Eastern Standard Time (EST)
    news_df['published_est'] = news_df['published'] - time_difference

    return news_df

def add_market(news_df):
    # Define the time boundaries for each trading session
    market_open_start = 9 + 30/60  # 9:30 AM in decimal hours
    market_open_end = 16  # 4:00 PM in decimal hours
    after_hours_end = 20  # 8:00 PM in decimal hours
    pre_market_start = 7  # 7:00 AM in decimal hours
    pre_market_end = 9 + 25/60  # 9:25 AM in decimal hours

    # Initialize the "market" column
    news_df['market'] = 'no_market'

    # Populate the "market" column based on the trading session rules
    news_df.loc[(news_df['published_est'].dt.hour + news_df['published_est'].dt.minute/60 >= market_open_start) &
                (news_df['published_est'].dt.hour + news_df['published_est'].dt.minute/60 < market_open_end), 'market'] = 'market_open'
    news_df.loc[(news_df['published_est'].dt.hour + news_df['published_est'].dt.minute/60 >= market_open_end) &
                (news_df['published_est'].dt.hour + news_df['published_est'].dt.minute/60 < after_hours_end), 'market'] = 'after_hours'
    news_df.loc[(news_df['published_est'].dt.hour + news_df['published_est'].dt.minute/60 >= pre_market_start) &
                (news_df['published_est'].dt.hour + news_df['published_est'].dt.minute/60 < pre_market_end), 'market'] = 'pre_market'

    # Extract the hour of the day on a 24-hour basis
    news_df['hour_of_day'] = news_df['published_est'].dt.hour

    return news_df


def load_config(sector):
    config_file = f"{sector}.yaml"
    try:
        with open(config_file, 'r') as file:
            rss_dict = yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading {config_file}: {e}")
        return None
    return rss_dict

def main(sector):
    print(f"Fetching news for sector: {sector}")
    
    rss_dict = load_config(sector)
    
    if rss_dict is None:
        print("Failed to load config.")
        return
        
    init_links()
    news_df = fetch_news(rss_dict)
    news_df = add_published_est(news_df)
    news_df = add_market(news_df)
    process_news(news_df)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch news for a specific sector.")
    parser.add_argument("-s", "--sector", default="biotech", help="Name of the sector. Default is 'biotech'")
    args = parser.parse_args()

    while True:
        main(args.sector)
        print("Waiting for the next iteration...")
        time.sleep(300)  # Adjusted to 5 minutes
