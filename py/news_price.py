import pandas as pd
from db_util import engine
import db_util
import date_util
import price_util

def main():
    news_df = db_util.read_news_item()
    news_df = price_util.create_returns(news_df)
    # Print the processed DataFrame
    print('Writing to db')
    db_util.write_news_price(news_df)

if __name__ == "__main__":
    main()

