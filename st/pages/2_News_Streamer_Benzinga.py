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

@st.cache_data(ttl=60)
def get_news(ticker, start_date, end_date):
    rest_client = REST(API_KEY, API_SECRET)
    news_items = rest_client.get_news(ticker, start_date, end_date)
    news_df = pd.DataFrame([item._raw for item in news_items])

    # Add ticker column with hyperlink
    news_df['ticker'] = '<a href="https://www.marketwatch.com/investing/stock/' + ticker + '" target="_blank">' + ticker + '</a>'

    # Check if 'created_at' exists and convert to EST
    if 'created_at' in news_df.columns:
        est = pytz.timezone('US/Eastern')
        news_df['created_at'] = pd.to_datetime(news_df['created_at']).dt.tz_convert(est)
        news_df.rename(columns={'created_at': 'created_est'}, inplace=True)
    else:
        news_df['created_est'] = 'N/A'  # Placeholder if 'created_at' does not exist

    # Drop unnecessary columns
    columns_to_drop = ['author', 'content', 'id', 'images', 'summary', 'updated_at']
    news_df.drop(columns=columns_to_drop, inplace=True, errors='ignore')

    # Create 'title' column if 'url' exists
    if 'url' in news_df.columns and 'headline' in news_df.columns:
        news_df['title'] = '<a href="' + news_df['url'] + '" target="_blank">' + news_df['headline'] + '</a>'
        news_df.drop(columns=['headline', 'url'], inplace=True)
    else:
        news_df['title'] = 'N/A'  # Placeholder if 'url' or 'headline' does not exist

    # column_order = ['ticker', 'title', 'created_est', 'source', 'symbols']
    # news_df = news_df[column_order]
    return news_df

def main():
    st.title("Stock News Fetcher")

    # Setting up dates
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=5)

    if st.button('Get News') or st.session_state.get('auto_fetch', False):
        with st.spinner('Fetching news...'):
            all_news = pd.DataFrame()
            for ticker in keys_list:
                news_df = get_news(ticker, start_date, end_date)
                all_news = pd.concat([all_news, news_df], ignore_index=True)

            # Convert DataFrame to HTML and then use st.markdown to render it
            html = all_news.to_html(escape=False, index=False)
            st.markdown(html, unsafe_allow_html=True)

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
