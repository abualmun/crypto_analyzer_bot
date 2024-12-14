# Create an instance of TechnicalAnalyzer
from src.analysis.plot_charts import *
from src.analysis.technical import TechnicalAnalyzer
import talib

analyzer = TechnicalAnalyzer()

# Perform analysis on a specific coin
coin_id = "bitcoin"
vs_currency = "usd"
days = 30

analysis_result = analyzer.analyze_coin(coin_id, vs_currency, days)

# Ensure you have data to work with
if "error" not in analysis_result:
    # Example 1: Plot price chart
    df = analyzer.data_processor.get_ohlcv_data(coin_id, vs_currency, days)
    plot_price_chart(df)

    # Example 2: Plot moving averages
    trend_data = analysis_result['trend_indicators']
    ma_data = {
        "ma20": talib.SMA(df['close'].values, timeperiod=20),
        "ma50": talib.SMA(df['close'].values, timeperiod=50),
        "ma200": talib.SMA(df['close'].values, timeperiod=200)
    }
    plot_moving_averages(df, ma_data)

    # Example 3: Plot MACD
    macd_data = trend_data['macd']
    plot_macd(macd_data, df)

    # Example 4: Plot RSI
    rsi_data = analysis_result['momentum_indicators']['rsi']
    plot_rsi([rsi_data] * len(df), df)  # Duplicate the RSI for consistent plotting

    # Example 5: Plot volume
    plot_volume(df)

    # Example 6: Plot support and resistance levels
    support_resistance_data = analysis_result['support_resistance']
    plot_support_resistance(
        df, 
        support_resistance_data['support_levels'], 
        support_resistance_data['resistance_levels']
    )
else:
    print("Error in analysis:", analysis_result["error"])
