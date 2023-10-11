
import pandas as pd
import feedparser
import yaml
from bs4 import BeautifulSoup
import time
from datetime import timedelta
import os
import pandas_gbq

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="fedoraltdata-bq.json"
project_id = 'fedoraltdata'
table_id = 'news.news_item'

# Initialize added_links as an empty list
global added_links
added_links = []

# Load the YAML file into a dictionary
with open("altsignals-company-news-rss.yaml", 'r') as file:
    rss_dict = yaml.safe_load(file)

def clean_text(raw_html):
    cleantext = BeautifulSoup(raw_html, "lxml").text
    return cleantext

def fetch_news():
    cols = ['ticker', 'title', 'summary', 'published', 'description', 'link', 'subject']
    all_news_items = []

    print("Starting new iteration...")
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
                'subject': last_subject
            })

    return pd.DataFrame(all_news_items, columns=cols)

def process_news(df):
    df = df[~df['link'].isin(added_links)]
    df['ticker'] = df['ticker'].astype(str)
    df['title'] = df['title'].astype(str)
    df['summary'] = df['summary'].astype(str)
    df['description'] = df['description'].astype(str)
    df['link'] = df['link'].astype(str)
    df['subject'] = df['subject'].astype(str)
    df['market'] = df['market'].astype(str)
    if not df.empty:
        pandas_gbq.to_gbq(df, table_id, project_id=project_id, if_exists='append')
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

def main():
    news_df = fetch_news()
    news_df = add_published_est(news_df)
    news_df = add_market(news_df)
    process_news(news_df)


if __name__ == "__main__":
    while True:
        main()
        print("Waiting for 5 minutes before the next iteration...")
        time.sleep(300)