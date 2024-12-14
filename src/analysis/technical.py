import talib
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from ..data.processor import DataProcessor

class TechnicalAnalyzer:
    def __init__(self):
        self.data_processor = DataProcessor()

    def analyze_coin(self, coin_id: str, vs_currency: str = 'usd', days: int = 30) -> Dict:
        """
        Perform comprehensive technical analysis on a coin.
        """
        # Get OHLCV data
        df = self.data_processor.get_ohlcv_data(coin_id, vs_currency, days)
        if df is None:
            return {"error": "Failed to fetch data"}

        # Perform analysis
        analysis = {
            "basic_info": self._get_basic_info(df),
            "trend_indicators": self._analyze_trend(df),
            "momentum_indicators": self._analyze_momentum(df),
            "volume_analysis": self._analyze_volume(df),
            "support_resistance": self._find_support_resistance(df),
            "patterns": self._identify_patterns(df),
            "summary": {}  # Will be filled with analysis summary
        }

        # Generate summary
        analysis["summary"] = self._generate_summary(analysis)
        
        return analysis

    def _get_basic_info(self, df: pd.DataFrame) -> Dict:
        """Calculate basic price information"""
        current_price = df['close'].iloc[-1]
        price_change = ((current_price - df['close'].iloc[-2]) / df['close'].iloc[-2]) * 100
        
        return {
            "current_price": current_price,
            "price_change_24h": price_change,
            "high_24h": df['high'].iloc[-1],
            "low_24h": df['low'].iloc[-1],
            "volume_24h": df['volume'].iloc[-1]
        }

    def _analyze_trend(self, df: pd.DataFrame) -> Dict:
        """Analyze trend indicators"""
        close = df['close'].values
        
        # Calculate moving averages
        ma20 = talib.SMA(close, timeperiod=20)
        ma50 = talib.SMA(close, timeperiod=50)
        ma200 = talib.SMA(close, timeperiod=200)
        
        # Calculate MACD
        macd, macd_signal, macd_hist = talib.MACD(close)
        
        # Determine trend
        current_price = close[-1]
        trend = "Neutral"
        if current_price > ma50[-1] and ma50[-1] > ma200[-1]:
            trend = "Bullish"
        elif current_price < ma50[-1] and ma50[-1] < ma200[-1]:
            trend = "Bearish"

        return {
            "trend": trend,
            "ma20": ma20[-1],
            "ma50": ma50[-1],
            "ma200": ma200[-1],
            "macd": {
                "macd": macd[-1],
                "signal": macd_signal[-1],
                "histogram": macd_hist[-1]
            }
        }

    def _analyze_momentum(self, df: pd.DataFrame) -> Dict:
        """Analyze momentum indicators"""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        
        # Calculate RSI
        rsi = talib.RSI(close)
        
        # Calculate Stochastic
        slowk, slowd = talib.STOCH(high, low, close)
        
        # Calculate ATR
        atr = talib.ATR(high, low, close)
        
        return {
            "rsi": rsi[-1],
            "stochastic": {
                "k": slowk[-1],
                "d": slowd[-1]
            },
            "atr": atr[-1]
        }

    def _analyze_volume(self, df: pd.DataFrame) -> Dict:
        """Analyze volume indicators"""
        close = df['close'].values
        volume = df['volume'].values
        
        # Calculate OBV
        obv = talib.OBV(close, volume)
        
        # Calculate average volume
        avg_volume = np.mean(volume[-20:])  # 20-day average
        current_volume = volume[-1]
        
        return {
            "current_volume": current_volume,
            "average_volume": avg_volume,
            "volume_change": ((current_volume - avg_volume) / avg_volume) * 100,
            "obv": obv[-1],
            "is_volume_high": current_volume > avg_volume * 1.5  # 50% above average
        }

    def _find_support_resistance(self, df: pd.DataFrame, window: int = 20) -> Dict:
        """Find potential support and resistance levels"""
        highs = df['high'].rolling(window=window, center=True).max()
        lows = df['low'].rolling(window=window, center=True).min()
        
        current_price = df['close'].iloc[-1]
        
        # Find nearest levels
        resistance_levels = sorted([x for x in highs.unique() if x > current_price][:3])
        support_levels = sorted([x for x in lows.unique() if x < current_price][-3:])
        
        return {
            "support_levels": support_levels,
            "resistance_levels": resistance_levels
        }

    def _identify_patterns(self, df: pd.DataFrame) -> Dict:
        """Identify common candlestick patterns"""
        open = df['open'].values
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        patterns = {}
        
        # Bullish patterns
        patterns['hammer'] = talib.CDLHAMMER(open, high, low, close)[-1]
        patterns['morning_star'] = talib.CDLMORNINGSTAR(open, high, low, close)[-1]
        patterns['bullish_engulfing'] = talib.CDLENGULFING(open, high, low, close)[-1]
        
        # Bearish patterns
        patterns['shooting_star'] = talib.CDLSHOOTINGSTAR(open, high, low, close)[-1]
        patterns['evening_star'] = talib.CDLEVENINGSTAR(open, high, low, close)[-1]
        patterns['hanging_man'] = talib.CDLHANGINGMAN(open, high, low, close)[-1]
        
        return {
            "patterns": {k: bool(v) for k, v in patterns.items() if v != 0}
        }

    def _generate_summary(self, analysis: Dict) -> Dict:
        """Generate a summary of the analysis"""
        trend = analysis['trend_indicators']['trend']
        rsi = analysis['momentum_indicators']['rsi']
        macd = analysis['trend_indicators']['macd']
        volume = analysis['volume_analysis']
        
        # Determine overall signal
        signals = []
        
        # Trend analysis
        if trend == "Bullish":
            signals.append(("Bullish", "Overall trend is bullish"))
        elif trend == "Bearish":
            signals.append(("Bearish", "Overall trend is bearish"))
            
        # RSI analysis
        if rsi > 70:
            signals.append(("Bearish", "RSI indicates overbought conditions"))
        elif rsi < 30:
            signals.append(("Bullish", "RSI indicates oversold conditions"))
            
        # MACD analysis
        if macd['macd'] > macd['signal']:
            signals.append(("Bullish", "MACD is above signal line"))
        elif macd['macd'] < macd['signal']:
            signals.append(("Bearish", "MACD is below signal line"))
            
        # Volume analysis
        if volume['is_volume_high']:
            signals.append(("Neutral", "High volume indicates strong market activity"))
            
        # Overall sentiment
        bullish_signals = sum(1 for signal in signals if signal[0] == "Bullish")
        bearish_signals = sum(1 for signal in signals if signal[0] == "Bearish")
        
        if bullish_signals > bearish_signals:
            overall_sentiment = "Bullish"
        elif bearish_signals > bullish_signals:
            overall_sentiment = "Bearish"
        else:
            overall_sentiment = "Neutral"
            
        return {
            "overall_sentiment": overall_sentiment,
            "signals": signals,
            "confidence": min(max(abs(bullish_signals - bearish_signals) * 20, 25), 100)  # Scale from 25-100
        }

    def get_quick_analysis(self, coin_id: str, vs_currency: str = 'usd') -> Dict:
        """
        Perform a quick analysis with basic indicators
        """
        df = self.data_processor.get_ohlcv_data(coin_id, vs_currency, days=7)
        if df is None:
            return {"error": "Failed to fetch data"}

        close = df['close'].values
        
        analysis = {
            "current_price": close[-1],
            "price_change": ((close[-1] - close[-2]) / close[-2]) * 100,
            "rsi": talib.RSI(close)[-1],
            "trend": "Bullish" if close[-1] > talib.SMA(close, 20)[-1] else "Bearish"
        }
        
        return analysis