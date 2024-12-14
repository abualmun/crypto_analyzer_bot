import mplfinance as mpf
import numpy as np
import pandas as pd

def validate_dataframe(df):
    """Ensure the DataFrame is valid for mplfinance."""
    required_columns = {'open', 'high', 'low', 'close', 'volume'}
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")
    if df.empty:
        raise ValueError("DataFrame is empty. Ensure data is properly fetched.")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be a DateTimeIndex.")

def plot_price_chart(df):
    """Plot the price chart with OHLC data using mplfinance."""
    validate_dataframe(df)
    mpf.plot(df, type='candle', title='Price Chart (OHLC)', ylabel='Price', style='charles')

def plot_moving_averages(df, ma_data):
    """Plot the price chart with moving averages using mplfinance."""
    validate_dataframe(df)
    additional_plots = [
        mpf.make_addplot(ma_data['ma20'], color='green', width=1.5, label='20-Day MA'),
        mpf.make_addplot(ma_data['ma50'], color='orange', width=1.5, label='50-Day MA'),
        mpf.make_addplot(ma_data['ma200'], color='red', width=1.5, label='200-Day MA')
    ]
    mpf.plot(df, type='candle', addplot=additional_plots, title='Moving Averages', ylabel='Price', style='charles')

def plot_macd(macd_data, df):
    """Plot the MACD and signal line using mplfinance."""
    validate_dataframe(df)
    additional_plots = [
        mpf.make_addplot(macd_data['macd'], color='blue', panel=1, ylabel='MACD'),
        mpf.make_addplot(macd_data['signal'], color='red', panel=1),
        mpf.make_addplot(macd_data['histogram'], type='bar', color='gray', panel=1)
    ]
    mpf.plot(df, type='candle', addplot=additional_plots, title='MACD (Moving Average Convergence Divergence)', style='charles')

def plot_rsi(rsi_data, df):
    """Plot the RSI using mplfinance."""
    validate_dataframe(df)
    additional_plots = [
        mpf.make_addplot(rsi_data, color='purple', panel=2, ylabel='RSI'),
        mpf.make_addplot([70]*len(df), color='red', linestyle='--', panel=2, label='Overbought'),
        mpf.make_addplot([30]*len(df), color='green', linestyle='--', panel=2, label='Oversold')
    ]
    mpf.plot(df, type='candle', addplot=additional_plots, title='Relative Strength Index (RSI)', style='charles')

def plot_volume(df):
    """Plot the trading volume using mplfinance."""
    validate_dataframe(df)
    mpf.plot(df, type='candle', volume=True, title='Trading Volume', ylabel='Price', ylabel_lower='Volume', style='charles')

def plot_support_resistance(df, support_levels, resistance_levels):
    """Plot the support and resistance levels on the price chart using mplfinance."""
    validate_dataframe(df)
    additional_plots = [
        *[mpf.make_addplot([level] * len(df), color='green', linestyle='--', label=f'Support: {level}') for level in support_levels],
        *[mpf.make_addplot([level] * len(df), color='red', linestyle='--', label=f'Resistance: {level}') for level in resistance_levels]
    ]
    mpf.plot(df, type='candle', addplot=additional_plots, title='Support and Resistance Levels', ylabel='Price', style='charles')
import mplfinance as mpf
import numpy as np

def validate_dataframe(df):
    """Ensure the DataFrame is valid for mplfinance."""
    required_columns = {'open', 'high', 'low', 'close', 'volume'}
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")
    if df.empty:
        raise ValueError("DataFrame is empty. Ensure data is properly fetched.")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be a DateTimeIndex.")

def plot_price_chart(df):
    """Plot the price chart with OHLC data using mplfinance."""
    validate_dataframe(df)
    mpf.plot(df, type='candle', title='Price Chart (OHLC)', ylabel='Price', style='charles')

def plot_moving_averages(df, ma_data):
    """Plot the price chart with moving averages using mplfinance."""
    validate_dataframe(df)
    additional_plots = [
        mpf.make_addplot(ma_data['ma20'], color='green', width=1.5, label='20-Day MA'),
        mpf.make_addplot(ma_data['ma50'], color='orange', width=1.5, label='50-Day MA'),
        mpf.make_addplot(ma_data['ma200'], color='red', width=1.5, label='200-Day MA')
    ]
    mpf.plot(df, type='candle', addplot=additional_plots, title='Moving Averages', ylabel='Price', style='charles')

def plot_macd(macd_data, df):
    """Plot the MACD and signal line using mplfinance."""
    validate_dataframe(df)
    additional_plots = [
        mpf.make_addplot(macd_data['macd'], color='blue', panel=1, ylabel='MACD'),
        mpf.make_addplot(macd_data['signal'], color='red', panel=1),
        mpf.make_addplot(macd_data['histogram'], type='bar', color='gray', panel=1)
    ]
    mpf.plot(df, type='candle', addplot=additional_plots, title='MACD (Moving Average Convergence Divergence)', style='charles')

def plot_rsi(rsi_data, df):
    """Plot the RSI using mplfinance."""
    validate_dataframe(df)
    additional_plots = [
        mpf.make_addplot(rsi_data, color='purple', panel=2, ylabel='RSI'),
        mpf.make_addplot([70]*len(df), color='red', linestyle='--', panel=2, label='Overbought'),
        mpf.make_addplot([30]*len(df), color='green', linestyle='--', panel=2, label='Oversold')
    ]
    mpf.plot(df, type='candle', addplot=additional_plots, title='Relative Strength Index (RSI)', style='charles')

def plot_volume(df):
    """Plot the trading volume using mplfinance."""
    validate_dataframe(df)
    mpf.plot(df, type='candle', volume=True, title='Trading Volume', ylabel='Price', ylabel_lower='Volume', style='charles')

def plot_support_resistance(df, support_levels, resistance_levels):
    """Plot the support and resistance levels on the price chart using mplfinance."""
    validate_dataframe(df)
    additional_plots = [
        *[mpf.make_addplot([level] * len(df), color='green', linestyle='--', label=f'Support: {level}') for level in support_levels],
        *[mpf.make_addplot([level] * len(df), color='red', linestyle='--', label=f'Resistance: {level}') for level in resistance_levels]
    ]
    mpf.plot(df, type='candle', addplot=additional_plots, title='Support and Resistance Levels', ylabel='Price', style='charles')
