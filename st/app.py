import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def load_data():
    """Load data from CSV file."""
    return pd.read_csv("st/data/biotech_news_demo.csv")

def process_data(df):
    """Process the dataframe for hyperlinks."""
    df['hyperlinked_ticker'] = '<a href="https://finance.yahoo.com/quote/' + df['ticker'] + '" target="_blank">' + df['ticker'] + '</a>'
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
    yf_today_date = today_date.strftime('%Y-%m-%d %H:%M')
    if yf_today_date in stock_data.index:
        price_at_today_date = stock_data.loc[yf_today_date, 'Close']
        fig.add_trace(go.Scatter(x=[yf_today_date], y=[price_at_today_date], 
                                 mode='markers', marker=dict(color='red', size=10), 
                                 name='Published Time'))
    st.plotly_chart(fig)

def main():
    st.title('Biotech News Processor')
    
    # Load and process data
    data = load_data()
    data = process_data(data)
    
    # Dropdown for ticker selection
    selected_ticker = st.selectbox('Select a ticker:', data['ticker'].head(10).tolist())
    row = data[data['ticker'] == selected_ticker].iloc[0]

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
    stock_data = fetch_stock_data(selected_ticker, yf_start_date, yf_end_date)
    if not stock_data.empty:
        plot_stock_data(stock_data, today_date, selected_ticker)
    
    # Display table
    columns_to_display = ['hyperlinked_ticker', 'title', 'published_est', 'subject', 'alpha']
    st.write(data[columns_to_display].head(10).to_html(escape=False, render_links=True), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
