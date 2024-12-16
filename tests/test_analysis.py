# Create an instance of TechnicalAnalyzer
from src.analysis.plot_charts import *
from src.analysis.technical import TechnicalAnalyzer
import talib
from src.services.coingecko_api import CoinGeckoAPI

analyzer = TechnicalAnalyzer()

api = CoinGeckoAPI()



custom_style = create_plot_style(
    grid=True,
    volume=True,
    color_up='green',
    color_down='red',
    bgcolor='lightgray'
)
# Perform analysis on a specific coin
coin_id = "btc"
vs_currency = "usd"
days = 30

analysis_result = analyzer.analyze_coin(coin_id, vs_currency, days)

# # Ensure you have data to work with
if "error" not in analysis_result:
    df = analyzer.data_processor.get_ohlcv_data(coin_id, vs_currency, days)
    ma_data = analysis_result['trend_indicators']['moving_averages']
    # print(ma_data)
    # ma_data = {
        # "ma20": talib.SMA(df['close'].values, timeperiod=20),
        # "ma50": talib.SMA(df['close'].values, timeperiod=50),
        # "ma200": talib.SMA(df['close'].values, timeperiod=200)
    # }
    # macd_data = trend_data['macd']
    # rsi_data = analysis_result['momentum_indicators']['rsi']["all"]
    # support_resistance_data = analysis_result['support_resistance']
    
    save_charts_to_pdf(
    filename='outputs/selected_charts.pdf',
    df=df,  # DataFrame with OHLCV data
    ma_data=ma_data,  # Moving averages data
    # macd_data=macd_data,  # MACD data
    # rsi_data=rsi_data,  # RSI data
    support_levels=[100, 105],  # Example support levels
    resistance_levels=[110, 115],  # Example resistance levels
    style=create_plot_style(color_up='blue', color_down='orange', bgcolor='lightgray'),  # Custom style
    charts_to_include=['moving_averages'],
    # labels are connected with charts_to_include respectively
    labels=['This is the Price Chart'],
    intro_text="""This PDF contains an overview of various financial charts generated for demonstration purposes.

The charts included in this PDF are:
1. Price Chart
2. Moving Averages
3. MACD (Moving Average Convergence Divergence)
4. Relative Strength Index (RSI)
5. Volume Chart
6. Support and Resistance Levels

Please note that these are sample data generated randomly for testing purposes.

Each chart is annotated with legends for easy interpretation.

Thank you for reviewing this document. Feel free to reach out for any clarifications or feedback.

"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."

(Additional placeholder text to simulate a long introduction.)

"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
"""


)

else:
    print("Error in analysis:", analysis_result["error"])
