import streamlit as st
import pandas as pd
from alpaca_trade_api import REST
from datetime import datetime, timedelta
import time
import pytz

API_KEY = 'PKWSHV3AS4J71TGOQEOC'
API_SECRET = 'wffi5PYdLHI2N/6Kfqx6LBTuVlfURGgOp9u5mXo5'

# List of tickers
keys_list = [
    "FBIO", "KA", "QGEN", "DYAI", "JSPR", "ANAB", "ECOR", "ELOX", "MDWD", "RAD.AX",
    "EYEN", "PYPD", "SCLX", "TALS", "SNCE", "ORIC", "TTOO", "ADXN", "SPRY", "IMNN",
    "ADTX", "OCUP", "ARQT", "IMCR", "ORPHA.CO", "VIR", "DBVT", "ICCC", "ONCT", "ALVO",
    "EVAX", "CHRS", "MYNZ", "SCPH", "MDAI", "BIOR", "MLYS", "LGVN", "BMRA", "KRON",
    "CDTX", "NTLA", "ARQT", "TLSA", "PCIB.OL", "SANN.SW"
]

@st.cache(ttl=60)
def get_news(ticker, start_date, end_date):
    rest_client = REST(API_KEY, API_SECRET)
    news_items = rest_client.get_news(ticker, start_date, end_date)
    processed_news = []

    for item in news_items:
        news = item._raw
        news['ticker'] = ticker
        news['created_est'] = pd.to_datetime(news.get('created_at')).dt.tz_convert('US/Eastern') if news.get('created_at') else 'N/A'
        news['title'] = f'<a href="{news.get("url", "#")}" target="_blank">{news.get("headline", "No Headline")}</a>'
        processed_news.append(news)

    news_df = pd.DataFrame(processed_news)
    news_df['ticker_link'] = '<a href="https://www.marketwatch.com/investing/stock/' + news_df['ticker'] + '" target="_blank">' + news_df['ticker'] + '</a>'
    
    # Drop unnecessary columns
    columns_to_drop = ['author', 'content', 'id', 'images', 'summary', 'updated_at', 'url', 'headline', 'created_at', 'ticker']
    news_df.drop(columns=columns_to_drop, inplace=True, errors='ignore')

    return news_df


def main():
    st.title("Stock News Fetcher")

    # Setting up dates
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=5)

    # Button to fetch news
    if st.button('Get News') or st.session_state.get('auto_fetch', False):
        with st.spinner('Fetching news...'):
            all_news = pd.DataFrame()
            for ticker in keys_list:
                news_df = get_news(ticker, start_date, end_date)
                all_news = pd.concat([all_news, news_df], ignore_index=True)
            st.dataframe(all_news)

    # Toggle for automatic fetching
    if st.checkbox('Auto Fetch News Every Minute', value=st.session_state.get('auto_fetch', False)):
        st.session_state['auto_fetch'] = True
        while st.session_state['auto_fetch']:
            time.sleep(60)
            st.experimental_rerun()
    else:
        st.session_state['auto_fetch'] = False

if __name__ == "__main__":
    if 'auto_fetch' not in st.session_state:
        st.session_state['auto_fetch'] = False
    main()
