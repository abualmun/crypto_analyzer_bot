# src/analysis/technical.py

import talib
import pandas as pd
import logging
import numpy as np
from typing import Dict, Optional, Tuple

class TechnicalAnalyzer:
    def __init__(self):
        """Initialize the Technical Analyzer."""
        pass  # No need for initialization dictionaries

    def analyze_trend(self, df: pd.DataFrame) -> Dict:
        """Analyze price trend using multiple indicators."""
        try:
            close_prices = df['close'].values
            
            # Calculate trend indicators
            sma_20 = talib.SMA(close_prices, timeperiod=20)
            sma_50 = talib.SMA(close_prices, timeperiod=50)
            ema_20 = talib.EMA(close_prices, timeperiod=20)
            
            # Determine trend
            current_price = close_prices[-1]
            trend = "Neutral"
            if current_price > sma_20[-1] and sma_20[-1] > sma_50[-1]:
                trend = "Bullish"
            elif current_price < sma_20[-1] and sma_20[-1] < sma_50[-1]:
                trend = "Bearish"

            return {
                'trend': trend,
                'sma_20': sma_20[-1],
                'sma_50': sma_50[-1],
                'ema_20': ema_20[-1],
                'price_vs_sma20': f"{((current_price / sma_20[-1] - 1) * 100):.2f}%",
                'price_vs_sma50': f"{((current_price / sma_50[-1] - 1) * 100):.2f}%"
            }
        except Exception as e:
            raise Exception(f"Error in trend analysis: {e}")

    def analyze_momentum(self, df: pd.DataFrame) -> Dict:
        """Analyze price momentum."""
        try:
            close_prices = df['close'].values
            high_prices = df['high'].values
            low_prices = df['low'].values
            volume = df['volume'].values

            # Calculate momentum indicators
            rsi = talib.RSI(close_prices)
            slowk, slowd = talib.STOCH(high_prices, low_prices, close_prices)
            macd, macd_signal, macd_hist = talib.MACD(close_prices)

            momentum = "Neutral"
            if rsi[-1] > 70 and slowk[-1] > 80:
                momentum = "Overbought"
            elif rsi[-1] < 30 and slowk[-1] < 20:
                momentum = "Oversold"

            return {
                'momentum': momentum,
                'rsi': rsi[-1],
                'stoch_k': slowk[-1],
                'stoch_d': slowd[-1],
                'macd': macd[-1],
                'macd_signal': macd_signal[-1],
                'macd_hist': macd_hist[-1]
            }
        except Exception as e:
            raise Exception(f"Error in momentum analysis: {e}")

    def analyze_volatility(self, df: pd.DataFrame) -> Dict:
        """Analyze price volatility."""
        try:
            close_prices = df['close'].values
            high_prices = df['high'].values
            low_prices = df['low'].values

            # Calculate Bollinger Bands
            upper, middle, lower = talib.BBANDS(close_prices)
            atr = talib.ATR(high_prices, low_prices, close_prices)

            current_price = close_prices[-1]
            volatility = "Normal"
            if current_price > upper[-1]:
                volatility = "High (Above Upper Band)"
            elif current_price < lower[-1]:
                volatility = "High (Below Lower Band)"

            return {
                'volatility': volatility,
                'bb_upper': upper[-1],
                'bb_middle': middle[-1],
                'bb_lower': lower[-1],
                'atr': atr[-1]
            }
        except Exception as e:
            raise Exception(f"Error in volatility analysis: {e}")

    def get_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict:
        """Calculate support and resistance levels."""
        try:
            highs = df['high'].rolling(window=window).max()
            lows = df['low'].rolling(window=window).min()
            
            current_price = df['close'].iloc[-1]
            resistance = highs.iloc[-1]
            support = lows.iloc[-1]

            return {
                'support': support,
                'resistance': resistance,
                'price_to_support': f"{((current_price / support - 1) * 100):.2f}%",
                'price_to_resistance': f"{((resistance / current_price - 1) * 100):.2f}%"
            }
        except Exception as e:
            raise Exception(f"Error calculating support/resistance: {e}")

    async def generate_analysis_report(self, df: pd.DataFrame) -> Dict:
        """Generate comprehensive analysis report."""
        try:
            trend_analysis = self.analyze_trend(df)
            momentum_analysis = self.analyze_momentum(df)
            volatility_analysis = self.analyze_volatility(df)
            support_resistance = self.get_support_resistance(df)

            return {
                'trend': trend_analysis,
                'momentum': momentum_analysis,
                'volatility': volatility_analysis,
                'support_resistance': support_resistance,
                'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            raise Exception(f"Error generating analysis report: {e}")