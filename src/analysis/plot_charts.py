import mplfinance as mpf
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import emoji

# Font Configuration for UTF-8 and Emoji Support
plt.rcParams['font.family'] = 'DejaVu Sans'  # Ensures emojis and UTF-8 text are supported

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

def save_charts_to_pdf(filename, df, ma_data=None, macd_data=None, rsi_data=None, support_levels=None, resistance_levels=None, style=None, charts_to_include=None, labels=None, intro_text=None):
    """Save selected charts into a single PDF with optional labels, legends, and an introductory text page."""
    def create_intro_page(intro_text, pdf):
        """Dynamically create an intro page with UTF-8 and emoji support."""
        # Process emojis in the text
        text_lines = [emoji.emojize(line, language='alias') for line in intro_text.split("\n")]
        
        # Calculate figure height dynamically
        num_lines = len(text_lines)
        base_height = max(11, num_lines * 0.4)  # Scale height with text lines

        # Create the figure
        fig, ax = plt.subplots(figsize=(8.5, base_height), facecolor='white')
        ax.axis('off')  # Hide axes
        
        # Position and render the text
        start_y = 0.95  # Start closer to the top of the page
        font_size = min(14, max(10, 18 - num_lines * 0.3))  # Adjust font size based on line count
        line_spacing = 0.04  # Reduced line spacing for tighter layout
        
        for i, line in enumerate(text_lines):
            y_pos = start_y - (i * line_spacing)
            ax.text(0.05, y_pos, line, fontsize=font_size, ha='left', va='center', wrap=True, color='black')
        
        # Save the page to PDF
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
    validate_dataframe(df)
    style = style or create_plot_style()
    charts_to_include = charts_to_include or ["price", "moving_averages", "macd", "rsi", "volume", "support_resistance"]
    labels = labels or [None] * len(charts_to_include)

    if len(charts_to_include) != len(labels):
        raise ValueError("The number of labels must match the number of charts to include.")

    with PdfPages(filename) as pdf:
        # Add the intro text page
        if intro_text:
            create_intro_page(intro_text, pdf)

        # Generate charts
        for chart, label in zip(charts_to_include, labels):
            if chart == "price":
                fig, ax = mpf.plot(df, type='candle', title='Price Chart', ylabel='Price', style=style, returnfig=True)
                pdf.savefig(fig)
                plt.close(fig)

            if chart == "moving_averages" and ma_data:
                additional_plots = [
                    mpf.make_addplot(ma_data['ma20'], color='green', width=1.5, label='20-Day MA'),
                    mpf.make_addplot(ma_data['ma50'], color='orange', width=1.5, label='50-Day MA')
                ]
                fig, ax = mpf.plot(df, type='candle', addplot=additional_plots, title='Moving Averages', ylabel='Price', style=style, returnfig=True)
                pdf.savefig(fig)
                plt.close(fig)

            if chart == "macd" and macd_data:
                additional_plots = [
                    mpf.make_addplot(macd_data['macd'], color='blue', panel=1, ylabel='MACD'),
                    mpf.make_addplot(macd_data['signal'], color='red', panel=1),
                    mpf.make_addplot(macd_data['histogram'], type='bar', color='gray', panel=1)
                ]
                fig, ax = mpf.plot(df, type='candle', addplot=additional_plots, title='MACD Indicator', style=style, returnfig=True)
                pdf.savefig(fig)
                plt.close(fig)

            if chart == "rsi" and len(rsi_data) > 0:
                additional_plots = [
                    mpf.make_addplot(rsi_data, color='purple', panel=1, ylabel='RSI'),
                    mpf.make_addplot([70] * len(df), color='red', linestyle='--', panel=1),
                    mpf.make_addplot([30] * len(df), color='green', linestyle='--', panel=1)
                ]
                fig, ax = mpf.plot(df, type='candle', addplot=additional_plots, title='RSI Indicator', style=style, returnfig=True)
                pdf.savefig(fig)
                plt.close(fig)

            if chart == "volume":
                fig, ax = mpf.plot(df, type='candle', volume=True, title='Volume', ylabel='Price', ylabel_lower='Volume', style=style, returnfig=True)
                pdf.savefig(fig)
                plt.close(fig)

            if chart == "support_resistance" and support_levels and resistance_levels:
                additional_plots = [
                    *[mpf.make_addplot([level] * len(df), color='green', linestyle='--') for level in support_levels],
                    *[mpf.make_addplot([level] * len(df), color='red', linestyle='--') for level in resistance_levels]
                ]
                fig, ax = mpf.plot(df, type='candle', addplot=additional_plots, title='Support & Resistance', ylabel='Price', style=style, returnfig=True)
                pdf.savefig(fig)
                plt.close(fig)

        print(f"Charts saved to {filename}")
