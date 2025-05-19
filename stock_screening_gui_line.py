pip uninstall numpy -y
pip install numpy --no-cache-dir
pip uninstall pandas-ta -y
pip install pandas-ta --no-cache-dir
import pandas as pd
import yfinance as yf
import datetime
import pandas_ta as ta
import requests
import numpy as np
npNaN = np.nan

def load_stock_list(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df['コード'] = df['コード'].astype(str).str.zfill(4)
    df['Symbol'] = df['コード'] + ".T"
    return df


def calculate_indicators(df):
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['RSI'] = ta.rsi(df['Close'], length=14)
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    df['MACD'] = macd['MACD_12_26_9']
    df['MACD_signal'] = macd['MACDs_12_26_9']
    return df.dropna()


def is_breakout(df):
    recent_high = df['High'].iloc[-11:-1].max()
    breakout_today = df['Close'].iloc[-1] > recent_high
    volume_spike = df['Volume'].iloc[-1] > 1.5 * df['Volume'].iloc[-6:-1].mean()
    return breakout_today and volume_spike


def is_pullback(df):
    current_close = df['Close'].iloc[-1]
    recent_high = df['Close'].max()
    rsi = df['RSI'].iloc[-1]
    above_ma = current_close > df['MA20'].iloc[-1]
    down_10 = current_close < 0.9 * recent_high
    macd_cross = (
        df['MACD'].iloc[-2] < df['MACD_signal'].iloc[-2] and
        df['MACD'].iloc[-1] > df['MACD_signal'].iloc[-1]
    )
    return down_10 and 30 <= rsi <= 50 and above_ma and macd_cross


def send_line_notify(token, message):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": message}
    try:
        requests.post(url, headers=headers, data=data)
    except Exception as e:
        print(f"LINE通知エラー: {e}")


def screen_stocks(input_file, output_file, sheet_name="Sheet1", days_back=60, line_token=None):
    stock_list = load_stock_list(input_file, sheet_name)
    breakout_list = []
    pullback_list = []

    end_date = datetime.datetime.today()
    start_date = end_date - datetime.timedelta(days=days_back)

    for _, row in stock_list.iterrows():
        symbol = row['Symbol']
        name = row['銘柄名']
        try:
            df = yf.download(symbol, start=start_date, end=end_date)
            if df.empty or len(df) < 30:
                continue

            df = calculate_indicators(df)

            if is_breakout(df):
                breakout_list.append([symbol, name])
            if is_pullback(df):
                pullback_list.append([symbol, name])

        except Exception as e:
            print(f"{symbol} の処理中にエラー: {e}")

    with pd.ExcelWriter(output_file) as writer:
        pd.DataFrame(breakout_list, columns=["Code", "Name"]).to_excel(writer, sheet_name="Breakout", index=False)
        pd.DataFrame(pullback_list, columns=["Code", "Name"]).to_excel(writer, sheet_name="Pullback", index=False)

    if line_token:
        message = f"📈ブレイクアウト: {len(breakout_list)}銘柄\n📉押し目買い: {len(pullback_list)}銘柄"
        send_line_notify(line_token, message)
