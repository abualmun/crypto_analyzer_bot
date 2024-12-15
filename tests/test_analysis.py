# Create an instance of TechnicalAnalyzer
from src.analysis.plot_charts import *
from src.analysis.technical import TechnicalAnalyzer
import talib

analyzer = TechnicalAnalyzer()
custom_style = create_plot_style(
    grid=True,
    volume=True,
    color_up='green',
    color_down='red',
    bgcolor='lightgray'
)
# Perform analysis on a specific coin
coin_id = "bitcoin"
vs_currency = "usd"
days = 30

analysis_result = analyzer.analyze_coin(coin_id, vs_currency, days)

# # Ensure you have data to work with
if "error" not in analysis_result:
    df = analyzer.data_processor.get_ohlcv_data(coin_id, vs_currency, days)
    trend_data = analysis_result['trend_indicators']
    ma_data = {
        "ma20": talib.SMA(df['close'].values, timeperiod=20),
        "ma50": talib.SMA(df['close'].values, timeperiod=50),
        "ma200": talib.SMA(df['close'].values, timeperiod=200)
    }
    macd_data = trend_data['macd']
    rsi_data = analysis_result['momentum_indicators']['rsi']["all"]
    support_resistance_data = analysis_result['support_resistance']
    
    save_charts_to_pdf(
    filename='outputs/selected_charts.pdf',
    df=df,  # DataFrame with OHLCV data
    ma_data=ma_data,  # Moving averages data
    macd_data=macd_data,  # MACD data
    rsi_data=rsi_data,  # RSI data
    support_levels=[100, 105],  # Example support levels
    resistance_levels=[110, 115],  # Example resistance levels
    style=create_plot_style(color_up='blue', color_down='orange', bgcolor='lightgray'),  # Custom style
    charts_to_include=['price', 'rsi', 'macd'],
    # labels are connected with charts_to_include respectively
    labels=['This is the Price Chart', 'RSI Analysis: Overbought and Oversold Zones', 'MACD: Momentum Analysis']
)

else:
    print("Error in analysis:", analysis_result["error"])
