import streamlit as st
import pandas as pd
import threading
import websocket
import json
import queue

API_KEY = 'PKWSHV3AS4J71TGOQEOC'
SECRET_KEY = 'wffi5PYdLHI2N/6Kfqx6LBTuVlfURGgOp9u5mXo5'
file_path = 'alpaca_news.csv'
news_queue = queue.Queue()

def on_message(ws, message):
    data = json.loads(message)
    if 'news' in data:
        news_item = data['news']
        news_queue.put(news_item)

def on_error(ws, error):
    print(f"Error: {error}")

def on_open(ws):
    auth_data = {"action": "auth", "key": API_KEY, "secret": SECRET_KEY}
    ws.send(json.dumps(auth_data))
    ws.send(json.dumps({"action": "subscribe", "news": ["*"]}))

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def run_websocket():
    ws = websocket.WebSocketApp(
        "wss://stream.data.alpaca.markets/v1beta1/news",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()

def main():
    st.title("News Streamer")

    if st.button('Start Fetching News'):
        threading.Thread(target=run_websocket, daemon=True).start()

    st.button('Stop Fetching News')  # To implement stopping, additional logic is needed

    news_df = pd.DataFrame(columns=['headline', 'timestamp'])

    # Update the dataframe with new news
    while not news_queue.empty():
        news_item = news_queue.get()
        news_df = news_df.append(news_item, ignore_index=True)

    st.dataframe(news_df)

if __name__ == "__main__":
    main()
