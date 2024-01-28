import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Database connection parameters
db_params = {
    'dbname': 'pddeswvh',
    'user': 'pddeswvh',
    'password': 'uRN_JtBBpy6BAHTgkAiZKKNW05LB_U_z',
    'host': 'trumpet.db.elephantsql.com',
    'port': '5432',  # default is 5432 for PostgreSQL
}

# Create a connection to the PostgreSQL database
engine = create_engine(f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}")

def get_engine():
    return engine

def read_news_item():
    # Define the SQL query
    sql_query = '''
    select distinct
    ticker,
    title,
    summary as topic,
    published_gmt,
    description,
    link,
    sector,
    topic,
    published_est,
    market,
    hour_of_day 
    from news_item limit 100
    '''
    # Fetch data into a pandas DataFrame using the engine
    news_df = pd.read_sql_query(sql_query, engine)
    return news_df

# Streamlit app
st.title('Historical News Items')

# Button to fetch and show news items
if st.button('Show News'):
    try:
        news_df = read_news_item()
        st.write(news_df)
    except Exception as e:
        st.error(f"Failed to read news items: {e}")
