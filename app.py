import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- Page config ---
st.set_page_config(page_title="📈 Financial Dashboard", layout="wide")

# --- Title ---
st.title("📈 Stock Price Dashboard")

# --- Sidebar controls ---
st.sidebar.header("⚙️ Dashboard Controls")

tickers = ["AAPL", "GOOG", "MSFT", "TSLA", "AMZN", "NVDA", "META"]
selected_ticker = st.sidebar.selectbox("Choose a stock ticker", tickers)

start_date = st.sidebar.date_input("Start date", pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End date", pd.to_datetime("today"))

# --- Fetch data ---
data = yf.download(selected_ticker, start=start_date, end=end_date)

# --- Flatten column names if needed ---
if isinstance(data.columns, pd.MultiIndex):
    data.columns = ['_'.join(col).strip() for col in data.columns.values]

# --- Dynamically access column names ---
close_col = f"Close_{selected_ticker}" if f"Close_{selected_ticker}" in data.columns else "Close"
volume_col = f"Volume_{selected_ticker}" if f"Volume_{selected_ticker}" in data.columns else "Volume"

# --- Technical indicators ---

# SMA (20-day)
data["SMA_20"] = data[close_col].rolling(window=20).mean()

# Bollinger Bands
rolling_std = data[close_col].rolling(window=20).std()
data["BB_upper"] = data["SMA_20"] + (rolling_std * 2)
data["BB_lower"] = data["SMA_20"] - (rolling_std * 2)

# RSI (14-day)
delta = data[close_col].diff()
gain = np.where(delta > 0, delta, 0)
loss = np.where(delta < 0, -delta, 0)
avg_gain = pd.Series(gain).rolling(window=14).mean()
avg_loss = pd.Series(loss).rolling(window=14).mean()
rs = avg_gain / avg_loss
rsi = 100 - (100 / (1 + rs))
data["RSI_14"] = rsi.values

# --- Tabs layout ---
tab1, tab2, tab3 = st.tabs(["📉 Price Chart", "📊 Volume", "📐 RSI"])

with tab1:
    st.subheader(f"{selected_ticker} Closing Price with 20-Day SMA and Bollinger Bands")
    st.line_chart(data[[close_col, "SMA_20", "BB_upper", "BB_lower"]])

with tab2:
    st.subheader(f"{selected_ticker} Volume")
    st.bar_chart(data[volume_col])

with tab3:
    st.subheader(f"{selected_ticker} RSI (14-Day)")
    st.line_chart(data["RSI_14"])

# --- Raw data toggle ---
with st.expander("🔎 Show Raw Data"):
    st.dataframe(data.tail())
