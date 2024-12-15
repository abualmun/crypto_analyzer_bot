import mplfinance as mpf
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

def validate_dataframe(df):
    """Ensure the DataFrame is valid for mplfinance."""
    required_columns = {'open', 'high', 'low', 'close', 'volume'}
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")
    if df.empty:
        raise ValueError("DataFrame is empty. Ensure data is properly fetched.")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be a DateTimeIndex.")

def create_plot_style(grid=True, volume=True, color_up='green', color_down='red', bgcolor='white'):
    """Create a custom style for mplfinance plots."""
    return mpf.make_mpf_style(
        base_mpf_style='charles',
        gridstyle='-' if grid else '',
        marketcolors=mpf.make_marketcolors(
            up=color_up,
            down=color_down,
            edge='inherit',
            wick='inherit',
            volume='in',
            ohlc='inherit',
            alpha=0.8
        ),
        facecolor=bgcolor
    )

def save_charts_to_pdf(filename, df, ma_data=None, macd_data=None, rsi_data=None, support_levels=None, resistance_levels=None, style=None, charts_to_include=None):
    """Save selected charts into a single PDF."""
    validate_dataframe(df)
    style = style or create_plot_style()
    charts_to_include = charts_to_include or ["price", "moving_averages", "macd", "rsi", "volume", "support_resistance"]

    with PdfPages(filename) as pdf:
        if "price" in charts_to_include:
            # Plot Price Chart
            fig, ax = mpf.plot(df, type='candle', title='Price Chart (OHLC)', ylabel='Price', style=style, returnfig=True)
            pdf.savefig(fig)
            # plt.close(fig)

        if "moving_averages" in charts_to_include and ma_data:
            # Plot Moving Averages
            additional_plots = [
                mpf.make_addplot(ma_data['ma20'], color='green', width=1.5, label='20-Day MA'),
                mpf.make_addplot(ma_data['ma50'], color='orange', width=1.5, label='50-Day MA'),
                # mpf.make_addplot(ma_data['ma200'], color='red', width=1.5, label='200-Day MA')
            ]
            fig, ax = mpf.plot(df, type='candle', addplot=additional_plots, title='Moving Averages', ylabel='Price', style=style, returnfig=True)
            pdf.savefig(fig)
            # plt.close(fig)

        if "macd" in charts_to_include and macd_data:
            # Plot MACD
            additional_plots = [
                mpf.make_addplot(macd_data['macd'], color='blue', panel=1, ylabel='MACD'),
                mpf.make_addplot(macd_data['signal'], color='red', panel=1),
                mpf.make_addplot(macd_data['histogram'], type='bar', color='gray', panel=1)
            ]
            fig, ax = mpf.plot(df, type='candle', addplot=additional_plots, title='MACD (Moving Average Convergence Divergence)', style=style, returnfig=True)
            pdf.savefig(fig)
            # plt.close(fig)

        if "rsi" in charts_to_include and len(rsi_data)>0:
            # Plot RSI
            additional_plots = [
                mpf.make_addplot(rsi_data, color='purple', panel=1, ylabel='RSI'),
                mpf.make_addplot([70] * len(df), color='red', linestyle='--', panel=1, label='Overbought'),
                mpf.make_addplot([30] * len(df), color='green', linestyle='--', panel=1, label='Oversold')
            ]
            fig, ax = mpf.plot(df, type='candle', addplot=additional_plots, title='Relative Strength Index (RSI)', style=style, panel_ratios=(2, 1), returnfig=True)
            pdf.savefig(fig)
            # plt.close(fig)

        if "volume" in charts_to_include:
            # Plot Volume
            fig, ax = mpf.plot(df, type='candle', volume=True, title='Trading Volume', ylabel='Price', ylabel_lower='Volume', style=style, returnfig=True)
            pdf.savefig(fig)
            # plt.close(fig)

        if "support_resistance" in charts_to_include and support_levels and resistance_levels:
            # Plot Support and Resistance
            additional_plots = [
                *[mpf.make_addplot([level] * len(df), color='green', linestyle='--', label=f'Support: {level}') for level in support_levels],
                *[mpf.make_addplot([level] * len(df), color='red', linestyle='--', label=f'Resistance: {level}') for level in resistance_levels]
            ]
            fig, ax = mpf.plot(df, type='candle', addplot=additional_plots, title='Support and Resistance Levels', ylabel='Price', style=style, returnfig=True)
            pdf.savefig(fig)
            # plt.close(fig)

        print(f"Selected charts have been saved to {filename}")
