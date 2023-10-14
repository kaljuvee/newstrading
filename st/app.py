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
    
    # Create a hyperlink for the 'title' column
    data['title'] = '<a href="' + data['link'] + '" target="_blank">' + data['title'] + '</a>'
    
    # Display a text box for ticker input
    selected_ticker = st.text_input("Enter the ticker:")
    
    # Display only the specified columns
    columns_to_display = ['ticker', 'title', 'market', 'published_est', 'subject', 'alpha']
    st.write(data[columns_to_display].head(10).to_html(escape=False, render_links=True), unsafe_allow_html=True)
    
    if st.button(f"Fetch data for {selected_ticker}"):
        row = data[data['ticker'] == selected_ticker].iloc[0]
        
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
            stock_data = yf.download(selected_ticker, interval='1d', start=yf_start_date, end=yf_end_date)
            fig = px.area(stock_data, x=stock_data.index, y='Close', title=f'Stock Prices for {selected_ticker}')
            st.plotly_chart(fig)
        except Exception as e:
            st.write(f"Error fetching data: {e}")
