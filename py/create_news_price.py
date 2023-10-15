import pandas as pd
import time
from sqlalchemy import create_engine
from datetime import timedelta
import datetime
import holidays
import yfinance as yf
from datetime import datetime
from db_util import engine
import date_util
import numpy as np
import price_util

def main():
    news_df = db_util.read_new_item()
    news_df = price_util.create_returns(news_df)
    # Print the processed DataFrame
    print('Writing to db')
    db_util.write_news_price(news_df)

if __name__ == "__main__":
    main()
