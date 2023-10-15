import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text
import traceback

# Database connection parameters (you'll need to fill these in)
#db_params = {
#    'dbname': 'altsignals-beta',
#    'user': 'julian',
#    'password': 'AltData2$2',
#    'host': '34.88.153.82',
#    'port': '5432',  # default is 5432 for PostgreSQL
#}
db_params = {
    'dbname': 'pddeswvh',
    'user': 'pddeswvh',
    'password': 'uRN_JtBBpy6BAHTgkAiZKKNW05LB_U_z',
    'host': 'trumpet.db.elephantsql.com',
    'port': '5432',  # default is 5432 for PostgreSQL
}
# postgres://pddeswvh:uRN_JtBBpy6BAHTgkAiZKKNW05LB_U_z@trumpet.db.elephantsql.com/pddeswvh


# Create a connection to the PostgreSQL database
engine = create_engine(f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}")

def get_engine():
    return engine

def read_news_item():
    # Define the SQL query
    sql_query = '''
    select * from news_item
    '''
    # Fetch data into a pandas DataFrame using the engine
    news_df = pd.read_sql_query(sql_query, engine)
    return news_df

def read_news_price():
    # Define the SQL query
    sql_query = '''
    select * from news_price
    '''
    # Fetch data into a pandas DataFrame using the engine
    news_df = pd.read_sql_query(sql_query, engine)

def write_news_price(df):
    try:
        if not df.empty:
            df.to_sql('news_price', engine, if_exists='replace', index=False)
    except Exception as e:
        print(f"An error occurred: {e}")
        print(traceback.format_exc())