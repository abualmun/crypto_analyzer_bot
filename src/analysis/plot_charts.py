import mplfinance as mpf
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import emoji
import re

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

import re
import emoji

def clean_intro_text(intro_text):
    """
    Clean intro text by removing unrecognized characters and non-printable characters.
    
    Args:
        intro_text (str): Original input text
    
    Returns:
        str: Cleaned text with only recognized characters
    """
    if not intro_text:
        return ""
    
    # Convert to string and handle potential non-string inputs
    intro_text = str(intro_text)
    
    # Remove any characters that are not:
    # - Alphanumeric (ASCII and Unicode)
    # - Basic punctuation
    # - Whitespace
    # - Emojis
    def is_valid_char(char):
        return (
            char.isalnum() or  # Alphanumeric characters
            char.isspace() or  # Whitespace
            char in '.,;:!?()[]{}"-' or  # Basic punctuation
            '\U0001F600' <= char <= '\U0001F64F' or  # Emoticons
            '\U0001F300' <= char <= '\U0001F5FF' or  # Misc Symbols and Pictographs
            '\U0001F680' <= char <= '\U0001F6FF' or  # Transport and Map Symbols
            '\U0001F1E0' <= char <= '\U0001F1FF'     # Flags
        )
    
    # Filter out invalid characters
    cleaned_text = ''.join(char for char in intro_text if is_valid_char(char))
    
    # Process emojis
    cleaned_text = emoji.emojize(cleaned_text, language='alias')
    
    return cleaned_text

def create_intro_page(intro_text, pdf, max_lines_per_page=7, font_size=14):
    """
    Dynamically create intro pages with UTF-8 and emoji support, 
    splitting text across multiple pages if needed.
    
    Args:
        intro_text (str): Text to display
        pdf (PdfPages): PDF file to save pages to
        max_lines_per_page (int): Maximum number of lines per page
        font_size (float): Font size for text
    """
    # Clean the text first
    cleaned_text = clean_intro_text(intro_text)
    
    # Process emojis in the text
    text_lines = [emoji.emojize(line, language='alias') for line in cleaned_text.split("\n")]
    
    # Split text into pages if it exceeds max_lines_per_page
    for page_start in range(0, len(text_lines), max_lines_per_page):
        page_lines = text_lines[page_start:page_start+max_lines_per_page]
        
        # Calculate figure height dynamically
        base_height = 9  # Standard height
        
        # Create the figure
        fig, ax = plt.subplots(figsize=(8.5, base_height), facecolor='white')
        ax.axis('off')  # Hide axes
        
        # Position and render the text
        start_y = 0.95  # Start closer to the top of the page
        line_spacing = 0.04  # Reduced line spacing for tighter layout
        
        for i, line in enumerate(page_lines):
            y_pos = start_y - (i * line_spacing)
            ax.text(0.05, y_pos, line, fontsize=font_size, ha='left', va='center', wrap=True, color='black')
        
        # Add page number if multiple pages
        if len(text_lines) > max_lines_per_page:
            ax.text(0.95, 0.05, f'Page {page_start//max_lines_per_page + 1}', 
                    fontsize=10, ha='right', va='bottom', color='gray')
        
        # Save the page to PDF
        pdf.savefig(fig, bbox_inches='tight')        
        plt.close(fig)

def save_charts_to_pdf(filename, df, ma_data=None, macd_data=None, rsi_data=None, support_levels=None, resistance_levels=None, style=None, charts_to_include=None, labels=None, intro_text=None, max_lines_per_page=7):
    """
    Save selected charts into a single PDF with optional labels, legends, and an introductory text page.

    Args:
        filename (str): Output PDF filename
        df (pd.DataFrame): Financial data DataFrame
        ma_data (dict, optional): Moving average data
        macd_data (dict, optional): MACD indicator data
        rsi_data (array, optional): RSI indicator data
        support_levels (list, optional): Support price levels
        resistance_levels (list, optional): Resistance price levels
        style (mpf.style, optional): Custom plot style
        charts_to_include (list, optional): List of charts to generate
        labels (list, optional): Labels for each chart
        intro_text (str, optional): Introductory text for the first page
        max_lines_per_page (int, optional): Maximum lines per intro page
    """
    validate_dataframe(df)
    style = style or create_plot_style()
    charts_to_include = charts_to_include or ["price", "moving_averages", "macd", "rsi", "volume", "support_resistance"]
    labels = labels or [None] * len(charts_to_include)

    if len(charts_to_include) != len(labels):
        raise ValueError("The number of labels must match the number of charts to include.")

    with PdfPages(filename) as pdf:
        # Add the intro text page
        if intro_text:
            create_intro_page(intro_text, pdf, max_lines_per_page=max_lines_per_page)

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