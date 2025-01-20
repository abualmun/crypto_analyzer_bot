import datapane as dp
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import emoji
import re
import plotly.graph_objects as go
import plotly.io as pio
import os
from playwright.async_api import async_playwright
def validate_dataframe(df):
    """Ensure the DataFrame is valid for plotting."""
    required_columns = {'open', 'high', 'low', 'close', 'volume'}
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"DataFrame must contain columns: {required_columns}")
    if df.empty:
        raise ValueError("DataFrame is empty. Ensure data is properly fetched.")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be a DateTimeIndex.")

def create_plot_style(grid=True, volume=True, color_up='green', color_down='red', bgcolor='white'):
    """Create a custom style for plots."""
    return {
        'grid': grid,
        'volume': volume,
        'color_up': color_up,
        'color_down': color_down,
        'bgcolor': bgcolor
    }

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
    
    intro_text = str(intro_text)
    
    def is_valid_char(char):
        return (
            char.isalnum() or
            char.isspace() or
            char in '.,;:!?()[]{}"-' or
            '\U0001F600' <= char <= '\U0001F64F' or
            '\U0001F300' <= char <= '\U0001F5FF' or
            '\U0001F680' <= char <= '\U0001F6FF' or
            '\U0001F1E0' <= char <= '\U0001F1FF'
        )
    
    cleaned_text = ''.join(char for char in intro_text if is_valid_char(char))
    cleaned_text = emoji.emojize(cleaned_text, language='alias')
    
    return cleaned_text

def create_candlestick_chart(df, style):
    """Create a candlestick chart using plotly."""
    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            increasing_line_color=style['color_up'],
            decreasing_line_color=style['color_down']
        )
    ])
    fig.update_layout(
        title='Price Chart',
        yaxis_title='Price',
        template='plotly_white' if style['bgcolor'] == 'white' else 'plotly_dark'
    )
    return fig

def create_volume_chart(df, style):
    """Create a volume chart using plotly."""
    colors = [style['color_up'] if row['close'] >= row['open'] else style['color_down']
              for _, row in df.iterrows()]
    
    fig = go.Figure(data=[
        go.Bar(
            x=df.index,
            y=df['volume'],
            marker_color=colors
        )
    ])
    fig.update_layout(
        title='Volume',
        yaxis_title='Volume',
        template='plotly_white' if style['bgcolor'] == 'white' else 'plotly_dark'
    )
    return fig

def create_ma_chart(df, ma_data, style):
    """Create a moving averages chart using plotly."""
    fig = go.Figure()
    
    # Add candlesticks
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price'
        )
    )
    
    # Add moving averages
    fig.add_trace(go.Scatter(x=df.index, y=ma_data['ma20'], name='20-Day MA', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=df.index, y=ma_data['ma50'], name='50-Day MA', line=dict(color='orange')))
    
    fig.update_layout(
        title='Moving Averages',
        yaxis_title='Price',
        template='plotly_white' if style['bgcolor'] == 'white' else 'plotly_dark'
    )
    return fig

def create_macd_chart(df, macd_data, style):
    """Create a MACD chart using plotly."""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                       vertical_spacing=0.1,
                       subplot_titles=('Price', 'MACD'))
    
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close']
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df.index, y=macd_data['macd'], name='MACD',
                  line=dict(color='blue')),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df.index, y=macd_data['signal'], name='Signal',
                  line=dict(color='red')),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Bar(x=df.index, y=macd_data['histogram'], name='Histogram',
               marker_color='gray'),
        row=2, col=1
    )
    
    fig.update_layout(
        title='MACD Indicator',
        template='plotly_white' if style['bgcolor'] == 'white' else 'plotly_dark'
    )
    return fig

def create_rsi_chart(df, rsi_data, style):
    """Create an RSI chart using plotly."""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                       vertical_spacing=0.1,
                       subplot_titles=('Price', 'RSI'))
    
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close']
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df.index, y=rsi_data, name='RSI',
                  line=dict(color='purple')),
        row=2, col=1
    )
    
    # Add overbought/oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    fig.update_layout(
        title='RSI Indicator',
        template='plotly_white' if style['bgcolor'] == 'white' else 'plotly_dark'
    )
    return fig

def create_support_resistance_chart(df, support_levels, resistance_levels, style):
    """Create a support and resistance chart using plotly."""
    fig = go.Figure()
    
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close']
        )
    )
    
    # Add support levels
    for level in support_levels:
        fig.add_hline(y=level, line_dash="dash", line_color="green")
    
    # Add resistance levels
    for level in resistance_levels:
        fig.add_hline(y=level, line_dash="dash", line_color="red")
    
    fig.update_layout(
        title='Support & Resistance',
        yaxis_title='Price',
        template='plotly_white' if style['bgcolor'] == 'white' else 'plotly_dark'
    )
    return fig

import datapane as dp
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import emoji
import re

# Previous helper functions remain the same...

def format_numeric_value(value):
    """
    Safely format numeric values, handling numpy arrays and other numeric types.
    
    Args:
        value: Number or numpy array to format
        
    Returns:
        str: Formatted string representation
    """
    if isinstance(value, (np.ndarray, pd.Series)):
        # If it's an array/series, take the last value
        value = value[-1] if len(value) > 0 else 0
    
    if isinstance(value, (int, np.integer)):
        return f"{value:,}"
    elif isinstance(value, (float, np.floating)):
        return f"{value:.2f}"
    else:
        return str(value)

def create_summary_cards(df):
    """Create summary statistics cards with safe value formatting."""
    try:
        latest_close = df['close'].iloc[-1]
        prev_close = df['close'].iloc[-2]
        price_change = latest_close - prev_close
        price_change_pct = (price_change / prev_close) * 100
        
        total_volume = df['volume'].iloc[-1]
        avg_volume = df['volume'].mean()
        volume_change_pct = ((total_volume - avg_volume) / avg_volume) * 100
        
        return dp.Group(
            dp.BigNumber(
                heading="Current Price",
                value=f"${format_numeric_value(latest_close)}",
                change=format_numeric_value(price_change),
                is_upward_change=price_change > 0
            ),
            dp.BigNumber(
                heading="24h Change",
                value=f"{format_numeric_value(price_change_pct)}%",
                change=format_numeric_value(abs(price_change)),
                is_upward_change=price_change > 0
            ),
            dp.BigNumber(
                heading="Volume",
                value=format_numeric_value(total_volume),
                change=f"{format_numeric_value(volume_change_pct)}%",
                is_upward_change=volume_change_pct > 0
            ),
            columns=3
        )
    except Exception as e:
        print(f"Debug: Error in create_summary_cards: {str(e)}")
        return dp.Text("Error creating summary cards")

def create_price_range_cards(df):
    """Create price range statistics cards with safe value formatting."""
    try:
        return dp.Group(
            dp.BigNumber(
                heading="All-Time High",
                value=f"${format_numeric_value(df['high'].max())}"
            ),
            dp.BigNumber(
                heading="All-Time Low",
                value=f"${format_numeric_value(df['low'].min())}"
            ),
            dp.BigNumber(
                heading="Average Price",
                value=f"${format_numeric_value(df['close'].mean())}"
            ),
            columns=3
        )
    except Exception as e:
        print(f"Debug: Error in create_price_range_cards: {str(e)}")
        return dp.Text("Error creating price range cards")

def create_technical_cards(df, ma_data=None, rsi_data=None):
    """Create technical analysis summary cards with safe value formatting."""
    try:
        cards = []
        
        if ma_data is not None:
            latest_ma20 = ma_data['ma20'].iloc[-1]
            latest_ma50 = ma_data['ma50'].iloc[-1]
            latest_price = df['close'].iloc[-1]
            
            ma20_signal = "ABOVE" if latest_price > latest_ma20 else "BELOW"
            ma50_signal = "ABOVE" if latest_price > latest_ma50 else "BELOW"
            
            cards.extend([
                dp.BigNumber(
                    heading="MA20 Signal",
                    value=ma20_signal,
                    change=format_numeric_value(latest_ma20),
                    is_upward_change=latest_price > latest_ma20
                ),
                dp.BigNumber(
                    heading="MA50 Signal",
                    value=ma50_signal,
                    change=format_numeric_value(latest_ma50),
                    is_upward_change=latest_price > latest_ma50
                )
            ])
        
        if rsi_data is not None and len(rsi_data) > 0:
            latest_rsi = rsi_data.iloc[-1] if isinstance(rsi_data, pd.Series) else rsi_data[-1]
            rsi_signal = "OVERBOUGHT" if latest_rsi > 70 else "OVERSOLD" if latest_rsi < 30 else "NEUTRAL"
            
            cards.append(
                dp.BigNumber(
                    heading="RSI Signal",
                    value=format_numeric_value(latest_rsi),
                    change=rsi_signal,
                    is_upward_change=latest_rsi > 50
                )
            )
        
        return dp.Group(*cards, columns=len(cards)) if cards else None
    except Exception as e:
        print(f"Debug: Error in create_technical_cards: {str(e)}")
        return dp.Text("Error creating technical cards")

async def save_charts_to_pdf(directory,filename, df, ma_data=None, macd_data=None, rsi_data=None, 
                      support_levels=None, resistance_levels=None, style=None, 
                      charts_to_include=None, labels=None, intro_text=None, 
                      max_lines_per_page=7):
    """
    Save selected charts into a single PDF using datapane with enhanced design and error handling.
    """
    try:
        validate_dataframe(df)
        style = style or create_plot_style()
        charts_to_include = charts_to_include or ["price", "moving_averages", "macd", "rsi", "volume", "support_resistance"]
        labels = labels or [None] * len(charts_to_include)

        if len(charts_to_include) != len(labels):
            raise ValueError("The number of labels must match the number of charts to include.")

        blocks = []
        
        # Add title and intro text
        blocks.append(dp.Text("# Financial Market Analysis Report"))
        if intro_text:
            cleaned_text = clean_intro_text(intro_text)
            blocks.append(dp.Text(cleaned_text))
        
        # Add summary section
        print("Debug: Creating summary section")
        blocks.append(dp.Text("## Market Summary"))
        summary_cards = create_summary_cards(df)
        
        if summary_cards:
            blocks.append(summary_cards)
        
        # Add price range section
        print("Debug: Creating price range section")
        blocks.append(dp.Text("## Price Statistics"))
        price_cards = create_price_range_cards(df)
        if price_cards:
            blocks.append(price_cards)
        
        # Add technical analysis cards
        if ma_data is not None or rsi_data is not None:
            print("Debug: Creating technical section")
            blocks.append(dp.Text("## Technical Indicators"))
            tech_cards = create_technical_cards(df, ma_data, rsi_data)
            if tech_cards:
                blocks.append(tech_cards)
        
        # Generate charts
        print("Debug: Creating charts")
        blocks.append(dp.Text("## Technical Analysis Charts"))
        for chart, label in zip(charts_to_include, labels):
            try:
                if label:
                    blocks.append(dp.Text(f"### {label}"))
                
                if chart == "price":
                    fig = create_candlestick_chart(df, style)
                    image_path =  f"{directory}/plot_image.png"
                    pio.write_image(fig, image_path, format="png", width=800, height=600)
                    blocks.append(dp.Media(file=image_path))
                elif chart == "moving_averages" and ma_data:
                    fig = create_ma_chart(df, ma_data, style)
                    image_path =  f"{directory}/plot_image.png"
                    pio.write_image(fig, image_path, format="png", width=800, height=600)
                    blocks.append(dp.Media(file=image_path))
                elif chart == "macd" and macd_data:
                    fig = create_macd_chart(df, macd_data, style)
                    image_path =  f"{directory}/plot_image.png"
                    pio.write_image(fig, image_path, format="png", width=800, height=600)
                    blocks.append(dp.Media(file=image_path))
                elif chart == "rsi" and len(rsi_data) > 0:
                    fig = create_rsi_chart(df, rsi_data, style)
                    image_path =  f"{directory}/plot_image.png"
                    pio.write_image(fig, image_path, format="png", width=800, height=600)
                    blocks.append(dp.Media(file=image_path))
                elif chart == "volume":
                    fig = create_volume_chart(df, style)
                    image_path =  f"{directory}/plot_image.png"
                    pio.write_image(fig, image_path, format="png", width=800, height=600)
                    blocks.append(dp.Media(file=image_path))
                elif chart == "support_resistance" and support_levels and resistance_levels:
                    fig = create_support_resistance_chart(df, support_levels, resistance_levels, style)
                    image_path =  f"{directory}/plot_image.png"
                    pio.write_image(fig, image_path, format="png", width=800, height=600)
                    blocks.append(dp.Media(file=image_path))
            except Exception as e:
                print(f"Debug: Error creating chart {chart}: {str(e)}")
                blocks.append(dp.Text(f"Error creating {chart} chart"))
        
        # Add data table
        print("Debug: Adding data table")
        blocks.append(dp.Text("## Historical Data"))
        blocks.append(dp.DataTable(df))
                
        # Example Plotly figure
        
        # Create and save report
        report = dp.Report(*blocks)
        report.save(f"{filename}.html")
        await html_to_pdf(f"{filename}.html",f'{filename}.pdf')

        
        print(f"Enhanced report saved to {filename}")
        
    except Exception as e:
        print(f"Debug: Error in save_charts_to_pdf: {str(e)}")
        # Create a minimal error report
        error_report = dp.Report(
            dp.Text("# Error in Report Generation"),
            dp.Text(f"An error occurred while generating the report: {str(e)}")
        )
        error_report.save(filename)
async def html_to_pdf(input_html, output_pdf):
        # Get absolute path of the HTML file
        abs_path = os.path.abspath(input_html)
        file_url = f"file://{abs_path}"  # Create the file:// URL

        async with async_playwright() as p:  # Correct usage of async context manager
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(file_url)
            await page.pdf(path=output_pdf, format="A4")
            await browser.close()
