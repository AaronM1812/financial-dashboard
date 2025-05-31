import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- Page config ---
st.set_page_config(page_title="📈 Financial Dashboard", layout="wide")

# --- Title ---
st.title("📈 Stock Price Dashboard")

# --- Sidebar controls ---
st.sidebar.header("📌 Customize Dashboard")

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

# MACD (12/26 EMA and 9 EMA Signal)
ema_12 = data[close_col].ewm(span=12, adjust=False).mean()
ema_26 = data[close_col].ewm(span=26, adjust=False).mean()
data["MACD"] = ema_12 - ema_26
data["Signal_Line"] = data["MACD"].ewm(span=9, adjust=False).mean()

# --- Tabs layout ---
tab1, tab2, tab3, tab4 = st.tabs(["📉 Price Chart", "📊 Volume", "📐 RSI", "📈 MACD"])

# --- Price Chart ---
with tab1:
    st.subheader(f"{selected_ticker} Closing Price with 20-Day SMA and Bollinger Bands")
    st.line_chart(data[[close_col, "SMA_20", "BB_upper", "BB_lower"]])

# --- Volume ---
with tab2:
    st.subheader(f"{selected_ticker} Volume")
    st.bar_chart(data[volume_col])

# --- RSI ---
with tab3:
    st.subheader(f"{selected_ticker} RSI (14-Day)")
    st.line_chart(data["RSI_14"])

    # RSI Insight
    latest_rsi = data["RSI_14"].dropna().iloc[-1]

    if latest_rsi > 70:
        rsi_status = "🔺 Overbought - Potential price pullback"
        color = "red"
    elif latest_rsi < 30:
        rsi_status = "🔻 Oversold - Potential rebound"
        color = "green"
    else:
        rsi_status = "⚖️ Neutral"
        color = "gray"

    with st.expander("💡 RSI Insight"):
        st.markdown(f"**RSI Insight:** <span style='color:{color}'>{rsi_status}</span>", unsafe_allow_html=True)

# --- MACD ---
with tab4:
    st.subheader(f"{selected_ticker} MACD & Signal Line")
    st.line_chart(data[["MACD", "Signal_Line"]])

# --- Divider ---
st.markdown("---")

# --- CSV Download ---
csv = data.to_csv(index=True)
st.download_button(
    label="📥 Download data as CSV",
    data=csv,
    file_name=f"{selected_ticker}_data.csv",
    mime="text/csv",
)

# --- Raw data toggle ---
with st.expander("🔎 Show Raw Data"):
    st.dataframe(data.tail())
