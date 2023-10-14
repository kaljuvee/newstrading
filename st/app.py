import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.express as px

st.title('Biotech News Processor')

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    
    # Create a new column for hyperlinked tickers
    data['hyperlinked_ticker'] = '<a href="https://finance.yahoo.com/quote/' + data['ticker'] + '" target="_blank">' + data['ticker'] + '</a>'
    
    # Create hyperlink for the 'title' column
    data['title'] = '<a href="' + data['link'] + '" target="_blank">' + data['title'] + '</a>'
    
    # Dropdown for user to select a ticker (using original tickers)
    selected_ticker = st.selectbox('Select a ticker:', data['ticker'].head(10).tolist())
    
    row = data[data['ticker'] == selected_ticker].iloc[0]  # Fetching row using original ticker

    # Determine the 'today' date based on the 'published' column
    try:
        if isinstance(row['published_est'], pd.Timestamp):
            today_date = row['published_est'].to_pydatetime()
        else:
            today_date = datetime.strptime(row['published_est'], '%Y-%m-%d %H:%M:%S.%f %z')
        
        st.write(f"Today's Date: {today_date}")  # Debugging Print
    except Exception as e:
        st.write(f"Error extracting date: {e}")

    # Adjust dates
    try:
        start_date = today_date - timedelta(days=2)
        end_date = today_date + timedelta(days=2)
        
        st.write(f"Start Date: {start_date}, End Date: {end_date}")  # Debugging Print
    except Exception as e:
        st.write(f"Error adjusting dates: {e}")

    # Convert dates to the yfinance format
    try:
        yf_start_date = start_date.strftime('%Y-%m-%d')
        yf_end_date = end_date.strftime('%Y-%m-%d')
        st.write(f"yf_start_date: {yf_start_date}")
        st.write(f"yf_end_date: {yf_end_date}")
        st.write(f"yfinance Start Date: {yf_start_date}, yfinance End Date: {yf_end_date}")  # Debugging Print
    except Exception as e:
        st.write(f"Error converting dates for yfinance: {e}")

    # Fetch stock data for 5 consecutive days
    try:
        st.write(f"selected tickter: {selected_ticker}")
        stock_data = yf.download(selected_ticker, interval='1d', start=yf_start_date, end=yf_end_date)
        st.write(stock_data.head())
        # Create the area chart
        fig = px.area(stock_data, x=stock_data.index, y='Close', title=f'Stock Prices for {selected_ticker}')        
        # Add a vertical line for the 'published_est' timestamp
        fig.add_vline(x=today_date, line_dash="dash", line_color="red", annotation_text="Published Date", annotation_position="top left")    
        st.plotly_chart(fig)
    except Exception as e:
        st.write(f"Error fetching data from yfinance: {e}")
    
    # Display only the specified columns
    columns_to_display = ['hyperlinked_ticker', 'title', 'published_est', 'subject', 'alpha']
    st.write(data[columns_to_display].head(10).to_html(escape=False, render_links=True), unsafe_allow_html=True)
