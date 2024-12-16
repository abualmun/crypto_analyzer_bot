import mplfinance as mpf
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

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
        """
        Dynamically create an intro page that adjusts to text length and fits comfortably.
        
        Args:
            intro_text (str): Multi-line text to be added to the intro page
            pdf (PdfPages): PDF pages object to save the figure
        """
        # Split the text into lines
        text_lines = intro_text.split("\n")
        
        # Calculate appropriate figure size based on text length
        num_lines = len(text_lines)
        
        # Base page height with extra padding
        base_height = max(11, num_lines * 0.5)  # Minimum 11 inches, scales with line count
        
        # Create figure with dynamic height
        fig, ax = plt.subplots(figsize=(8.5, base_height))
        ax.axis('off')  # Remove axes
        
        # Calculate starting y position to center the text vertically
        start_y = 1.0 - (1.0 - num_lines * 0.05) / 2
        
        # Render text with adaptive sizing
        font_size = min(12, max(8, 16 - num_lines * 0.5))  # Dynamically adjust font size
        
        for i, line in enumerate(text_lines):
            y_pos = start_y - (i * 0.05)
            ax.text(
                0.05,  # Left margin
                y_pos, 
                line, 
                fontsize=font_size, 
                ha='left', 
                wrap=True
            )
        
        # Add some padding
        plt.tight_layout(pad=1.0)
        
        # Save the figure
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

    validate_dataframe(df)
    style = style or create_plot_style()
    charts_to_include = charts_to_include or ["price", "moving_averages", "macd", "rsi", "volume", "support_resistance"]
    labels = labels or [None] * len(charts_to_include)

    if len(charts_to_include) != len(labels):
        raise ValueError("The number of labels must match the number of charts to include.")

    with PdfPages(filename) as pdf:
        # Add the intro text as the first page
        if intro_text:
            create_intro_page(intro_text, pdf)

        for chart, label in zip(charts_to_include, labels):
            if chart == "price":
                # Plot Price Chart
                fig, ax = mpf.plot(df, type='candle', title='Price Chart (OHLC)', ylabel='Price', style=style, returnfig=True)
                if label:
                    fig.suptitle(label, fontsize=8, fontweight='bold', y=0.98)
                ax[0].legend(["Candlestick: OHLC prices"], loc="upper left")
                pdf.savefig(fig)
                plt.close(fig)

            if chart == "moving_averages" and ma_data:
                # Plot Moving Averages
                additional_plots = [
                    mpf.make_addplot(ma_data['ma20'], color='green', width=1.5, label='20-Day MA'),
                    mpf.make_addplot(ma_data['ma50'], color='orange', width=1.5, label='50-Day MA'),
                    # mpf.make_addplot(ma_data['ma200'], color='red', width=1.5, label='200-Day MA')
                ]
                fig, ax = mpf.plot(df, type='candle', addplot=additional_plots, title='Moving Averages', ylabel='Price', style=style, returnfig=True)
                if label:
                    fig.suptitle(label, fontsize=8, fontweight='bold', y=0.98)
                ax[0].legend(["Green: 20-Day MA", "Orange: 50-Day MA"], loc="upper left")
                pdf.savefig(fig)
                plt.close(fig)

            if chart == "macd" and macd_data:
                # Plot MACD
                additional_plots = [
                    mpf.make_addplot(macd_data['macd'], color='blue', panel=1, ylabel='MACD'),
                    mpf.make_addplot(macd_data['signal'], color='red', panel=1),
                    mpf.make_addplot(macd_data['histogram'], type='bar', color='gray', panel=1)
                ]
                fig, ax = mpf.plot(df, type='candle', addplot=additional_plots, title='MACD (Moving Average Convergence Divergence)', style=style, returnfig=True)
                if label:
                    fig.suptitle(label, fontsize=8, fontweight='bold', y=0.98)
                ax[0].legend(["Blue: MACD Line", "Red: Signal Line", "Gray: Histogram"], loc="upper left")
                pdf.savefig(fig)
                plt.close(fig)

            if chart == "rsi" and len(rsi_data) > 0:
                # Plot RSI
                additional_plots = [
                    mpf.make_addplot(rsi_data, color='purple', panel=1, ylabel='RSI'),
                    mpf.make_addplot([70] * len(df), color='red', linestyle='--', panel=1, label='Overbought'),
                    mpf.make_addplot([30] * len(df), color='green', linestyle='--', panel=1, label='Oversold')
                ]
                fig, ax = mpf.plot(df, type='candle', addplot=additional_plots, title='Relative Strength Index (RSI)', style=style, panel_ratios=(2, 1), returnfig=True)
                if label:
                    fig.suptitle(label, fontsize=8, fontweight='bold', y=0.98)
                ax[0].legend(["Purple: RSI", "Red Dashed: Overbought (70)", "Green Dashed: Oversold (30)"], loc="upper left")
                pdf.savefig(fig)
                plt.close(fig)

            if chart == "volume":
                # Plot Volume
                fig, ax = mpf.plot(df, type='candle', volume=True, title='Trading Volume', ylabel='Price', ylabel_lower='Volume', style=style, returnfig=True)
                if label:
                    fig.suptitle(label, fontsize=8, fontweight='bold', y=0.98)
                ax[0].legend(["Candlestick: OHLC", "Bar: Volume"], loc="upper left")
                pdf.savefig(fig)
                plt.close(fig)

            if chart == "support_resistance" and support_levels and resistance_levels:
                # Plot Support and Resistance
                additional_plots = [
                    *[mpf.make_addplot([level] * len(df), color='green', linestyle='--', label=f'Support: {level}') for level in support_levels],
                    *[mpf.make_addplot([level] * len(df), color='red', linestyle='--', label=f'Resistance: {level}') for level in resistance_levels]
                ]
                fig, ax = mpf.plot(df, type='candle', addplot=additional_plots, title='Support and Resistance Levels', ylabel='Price', style=style, returnfig=True)
                if label:
                    fig.suptitle(label, fontsize=8, fontweight='bold', y=0.98)
                ax[0].legend(["Green Dashed: Support Levels", "Red Dashed: Resistance Levels"], loc="upper left")
                pdf.savefig(fig)
                plt.close(fig)

        print(f"Selected charts have been saved to {filename}")