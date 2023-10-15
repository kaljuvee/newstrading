import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text

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
