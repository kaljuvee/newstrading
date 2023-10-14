import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.express as px

st.title('News Event Analysis Tool - NEAT')

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

def adjust_dates_for_weekends(today_date):
    """Adjusts the date for weekends."""
    if today_date.weekday() == 5:  # Saturday
        yesterday_date = today_date - timedelta(days=1)
        tomorrow_date = today_date + timedelta(days=2)
    elif today_date.weekday() == 6:  # Sunday
        yesterday_date = today_date - timedelta(days=2)
        tomorrow_date = today_date + timedelta(days=1)
    else:
        yesterday_date = today_date - timedelta(days=1)
        tomorrow_date = today_date + timedelta(days=1)
    
    return yesterday_date, tomorrow_date

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    
    # Display table
    st.write(data.head(10).to_html(escape=False, render_links=True), unsafe_allow_html=True)
    
    # Ask user to select a symbol
    selected_symbol = st.selectbox('Select a symbol to fetch data:', data['symbol'].unique())
    if st.button(f"Fetch data for {selected_symbol}"):
        row = data[data['symbol'] == selected_symbol].iloc[0]
        
        # Determine the 'today' date based on the 'published' column
        if isinstance(row['published_est'], pd.Timestamp):
            today_date = row['published_est'].to_pydatetime()
        else:
            today_date = datetime.strptime(row['published_est'], '%Y-%m-%d %H:%M:%S%z')
        
        # Adjust dates
        start_date = today_date - timedelta(days=2)
        end_date = today_date + timedelta(days=2)
        
        # Convert dates to the yfinance format
        yf_start_date = start_date.strftime('%Y-%m-%d')
        yf_end_date = end_date.strftime('%Y-%m-%d')

        try:
            # Fetch stock data for 5 consecutive days
            stock_data = yf.download(selected_symbol, interval='1d', start=yf_start_date, end=yf_end_date)
            fig = px.area(stock_data, x=stock_data.index, y='Close', title=f'Stock Prices for {selected_symbol}')
            st.plotly_chart(fig)
        except Exception as e:
            st.write(f"Error fetching data: {e}")
