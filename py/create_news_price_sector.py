import pandas as pd
import time
from sqlalchemy import create_engine
from datetime import timedelta
import datetime
import holidays
import yfinance as yf
from datetime import datetime

db_params = {
    'dbname': 'altsignals-beta',
    'user': 'julian',
    'password': 'AltData2$2',
    'host': '34.88.153.82',
    'port': '5432',  # default is 5432 for PostgreSQL
}
    # Create a connection to the PostgreSQL database
engine = create_engine(f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}")

index_symbol = 'SPY'

def read_db():
    # Define the SQL query
    sql_query = '''
    select * from news_item_sector
    '''
    # Fetch data into a pandas DataFrame using the engine
    news_df = pd.read_sql_query(sql_query, engine)
    return news_df


def adjust_dates_for_weekends_and_holidays(today_date):
    us_holidays = holidays.US(years=today_date.year)
    
    # Calculate initial yesterday and tomorrow dates
    yesterday_date = today_date - timedelta(days=1)
    tomorrow_date = today_date + timedelta(days=1)

    # Adjust for weekends and holidays for 'yesterday'
    while yesterday_date.weekday() >= 5 or yesterday_date in us_holidays:
        yesterday_date -= timedelta(days=1)

    # Adjust for weekends and holidays for 'tomorrow'
    while tomorrow_date.weekday() >= 5 or tomorrow_date in us_holidays:
        tomorrow_date += timedelta(days=1)
    
    return yesterday_date, tomorrow_date


def adjust_dates_for_weekends(today_date):
    """
    Adjusts the provided date to ensure that the calculated 'yesterday' and 'tomorrow' dates 
    do not fall on a weekend.
    
    Args:
    - today_date (datetime.datetime): The reference date.

    Returns:
    - tuple: (yesterday_date, tomorrow_date) where neither date falls on a weekend.
    """
    
    # Calculate yesterday and tomorrow dates
    yesterday_date = today_date - timedelta(days=1)
    tomorrow_date = today_date + timedelta(days=1)

    # Adjust for weekends
    # If today is Monday, set yesterday to the previous Friday
    if today_date.weekday() == 0:
        yesterday_date = today_date - timedelta(days=3)
    # If today is Friday, set tomorrow to the following Monday
    elif today_date.weekday() == 4:
        tomorrow_date = today_date + timedelta(days=3)
    # If today is Saturday, adjust both yesterday and tomorrow
    elif today_date.weekday() == 5:
        yesterday_date = today_date - timedelta(days=2)
        tomorrow_date = today_date + timedelta(days=2)
    # If today is Sunday, adjust both yesterday and tomorrow
    elif today_date.weekday() == 6:
        yesterday_date = today_date - timedelta(days=3)
        tomorrow_date = today_date + timedelta(days=1)
    
    return yesterday_date, tomorrow_date


def set_prices(row):
    symbol = row['ticker']

    # Determine the 'today' date based on the 'published' column
    if isinstance(row['published_est'], pd.Timestamp):
        today_date = row['published_est'].to_pydatetime()
    else:
        today_date = datetime.strptime(row['published_est'], '%Y-%m-%d %H:%M:%S%z')

    # Calculate yesterday and tomorrow dates
    yesterday_date, tomorrow_date = adjust_dates_for_weekends(today_date)
    
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

def write_db(df):
    try:
        if not df.empty:
            df.to_sql('news_price_sector', engine, if_exists='replace', index=False)
    except Exception as e:
        print(f"An error occurred: {e}")
        # Optionally, you can also print the traceback for more detailed error information
        import traceback
        print(traceback.format_exc())

def create_returns(news_df):
    news_df = news_df.apply(lambda row: set_prices(row), axis=1)
    news_df = news_df[news_df['begin_price'].notna() & news_df['end_price'].notna()]
    news_df = news_df[news_df['index_begin_price'].notna() & news_df['index_end_price'].notna()]
    news_df['return'] = (news_df['end_price'] - news_df['begin_price'])/news_df['begin_price']
    news_df['index_return'] = (news_df['index_end_price'] - news_df['index_begin_price'])/news_df['index_begin_price']
    news_df['alpha'] = news_df['return'] - news_df['index_return']    
    return news_df


def main():
    news_df = read_db()
    news_df = create_returns(news_df)
    # Print the processed DataFrame
    print('Writing to db')
    write_db(news_df)

if __name__ == "__main__":
    main()

