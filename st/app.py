import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import db_util

st.title('News Event Analysis Tool - NEAT')

def load_data():
    """Load data from CSV file."""
    return db_util.get_news_price()

def process_data(df):
    """Process the dataframe for hyperlinks."""
    df['symbol'] = '<a href="https://finance.yahoo.com/quote/' + df['ticker'] + '" target="_blank">' + df['ticker'] + '</a>'
    df['title'] = '<a href="' + df['link'] + '" target="_blank">' + df['title'] + '</a>'
    return df

def fetch_stock_data(ticker, start_date, end_date):
    """Fetch stock data using yfinance."""
    try:
        return yf.download(ticker, interval='1h', start=start_date, end=end_date)
    except Exception as e:
        st.error(f"Error fetching data from yfinance: {e}")
        return pd.DataFrame()

def plot_stock_data(stock_data, today_date, ticker):
    """Plot stock data using Plotly."""
    fig = px.area(stock_data, x=stock_data.index, y='Close', title=f'Stock Prices for {ticker}')
    
    # Ensure stock_data.index is in datetime format
    stock_data.index = pd.to_datetime(stock_data.index)
    
    # Find the closest date in stock_data.index to yf_today_date
    time_diff = abs(stock_data.index - today_date)
    closest_date_idx = pd.Series(time_diff).idxmin()
    closest_date = stock_data.index[closest_date_idx]
  
    price_at_closest_date = stock_data.loc[closest_date, 'Close']
    fig.add_trace(go.Scatter(x=[closest_date], y=[price_at_closest_date], 
                             mode='markers', marker=dict(color='red', size=10), 
                             name='Published Time'))
    st.plotly_chart(fig)

def main():
    # Load and process data
    data = load_data()
    data = process_data(data)

    # Dropdown for ticker selection
    data['selection_key'] = data['ticker'] + ' - ' + data['subject'] + ' - ' + str(data['published_est']) 
    selected_ticker = st.selectbox('Select a ticker:', data['selection_key'].head(10).tolist())
    row = data.loc[data['selection_key'] == selected_ticker].iloc[0]

    # Extract 'today' date
    try:
        if isinstance(row['published_est'], pd.Timestamp):
            today_date = row['published_est'].to_pydatetime()
        else:
            today_date = datetime.strptime(row['published_est'], '%Y-%m-%d %H:%M:%S.%f %z')
    except Exception as e:
        st.error(f"Error extracting date: {e}")
        return
    
    # Adjust date range for yfinance
    start_date = today_date - timedelta(days=2)
    end_date = today_date + timedelta(days=2)
    yf_start_date = start_date.strftime('%Y-%m-%d')
    yf_end_date = end_date.strftime('%Y-%m-%d')
    
    # Fetch stock data and plot
    stock_data = fetch_stock_data(row['ticker'], yf_start_date, yf_end_date)
    if not stock_data.empty:
        plot_stock_data(stock_data, today_date, row['ticker'])
    
    # Display table
    # Format the 'published_est' column
    #data['published_est'] = pd.to_datetime(data['published_est'])
    #data['published_est'] = data['published_est'].dt.strftime('%Y-%m-%d %H:%M')
    columns_to_display = ['symbol', 'title', 'published_est', 'subject', 'daily_alpha(%)']
    st.write(data[columns_to_display].head(10).to_html(escape=False, render_links=True, index=False), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
