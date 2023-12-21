import pandas as pd
import time
from datetime import timedelta
import datetime
import holidays
from datetime import datetime
import date_util
import numpy as np
import yfinance as yf

index_symbol = 'SPY'

def set_prices(row):
    symbol = row['ticker']

    # Determine the 'today' date based on the 'published' column
    if isinstance(row['published_est'], pd.Timestamp):
        today_date = row['published_est'].to_pydatetime()
    else:
        today_date = datetime.strptime(row['published_est'], '%Y-%m-%d %H:%M:%S%z')

    # Calculate yesterday and tomorrow dates
    yesterday_date, tomorrow_date = date_util.adjust_dates_for_weekends(today_date)
    
        # Convert dates to the yfinance format
    yf_today_date = today_date.strftime('%Y-%m-%d')
    yf_yesterday_date = yesterday_date.strftime('%Y-%m-%d')
    yf_tomorrow_date = tomorrow_date.strftime('%Y-%m-%d')

    try:
        # Fetch stock data for 3 consecutive days
        data = yf.download(symbol, interval='1d', start=yf_yesterday_date, end=yf_tomorrow_date)
        index_data = yf.download(index_symbol, interval='1d', start=yf_yesterday_date, end=yf_tomorrow_date)
        
        # Determine prices based on the 'market' column value
        if row['market'] == 'market_open':
            row['begin_price'] = data.loc[yf_today_date]['Open']
            row['end_price'] = data.loc[yf_today_date]['Close']
            row['index_begin_price'] = index_data.loc[yf_today_date]['Open']
            row['index_end_price'] = index_data.loc[yf_today_date]['Close']
        elif row['market'] == 'pre_market':
            row['begin_price'] = data.loc[yf_yesterday_date]['Close']
            row['end_price'] = data.loc[yf_today_date]['Open']
            row['index_begin_price'] = index_data.loc[yf_yesterday_date]['Close']
            row['index_end_price'] = index_data.loc[yf_today_date]['Open']
        elif row['market'] == 'after_market':
            row['begin_price'] = data.loc[yf_today_date]['Close']
            row['end_price'] = data.loc[yf_tomorrow_date]['Open']
            row['index_begin_price'] = index_data.loc[yf_today_date]['Close']
            row['index_end_price'] = index_data.loc[yf_tomorrow_date]['Open']
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
    return row

def create_returns(news_df):
    news_df = news_df.apply(lambda row: set_prices(row), axis=1)

    # Check if the required columns exist before filtering
    required_price_columns = ['begin_price', 'end_price', 'index_begin_price', 'index_end_price']
    missing_columns = [col for col in required_price_columns if col not in news_df.columns]
    if missing_columns:
        print(f"Warning: Missing columns in the DataFrame: {missing_columns}")

    # Ensure that all required columns have no NaN values
    for col in required_price_columns:
        if col in news_df.columns:
            news_df = news_df[news_df[col].notna()]

    # Calculate returns and other metrics only if all required data is available
    if all(column in news_df.columns for column in required_price_columns):
        try:
            news_df['return'] = (news_df['end_price'] - news_df['begin_price']) / news_df['begin_price']
            news_df['index_return'] = (news_df['index_end_price'] - news_df['index_begin_price']) / news_df['index_begin_price']
            news_df['daily_alpha'] = news_df['return'] - news_df['index_return']
            news_df['action'] = np.where(news_df['daily_alpha'] >= 0, 'long', 'short')
        except Exception as e:
            print(f"Error in calculating returns: {e}")
    else:
        print("Required price data not available for some rows.")

    return news_df
