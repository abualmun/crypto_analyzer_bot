import talib
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from ..data.processor import DataProcessor

class TechnicalAnalyzer:
    def __init__(self):
        self.data_processor = DataProcessor()

    def analyze_coin(self, coin_id: str, vs_currency: str = 'usd', days: int = 30) -> Dict:
        """Perform enhanced technical analysis"""
        df = self.data_processor.get_ohlcv_data(coin_id, vs_currency, days)
        if df is None:
            return {"error": "Failed to fetch data"}

        analysis = {
            "basic_info": self._get_basic_info(df),
            "trend_indicators": self._analyze_trend(df),
            "momentum_indicators": self._analyze_momentum(df),
            "volume_indicators": self._analyze_volume(df),
            "volatility_indicators": self._analyze_volatility(df),
            "support_resistance": self._find_support_resistance(df),
            "patterns": self._identify_patterns(df),
            "summary": {}
        }

        analysis["summary"] = self._generate_enhanced_summary(analysis)
        return analysis
    
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

    def _analyze_momentum(self, df: pd.DataFrame) -> Dict:
        """Enhanced momentum analysis"""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        volume = df['volume'].values

        try:
            # RSI
            rsi = talib.RSI(close, timeperiod=14)
            
            # Stochastic
            slowk, slowd = talib.STOCH(high, low, close, 
                                     fastk_period=14, 
                                     slowk_period=3, 
                                     slowd_period=3)
            
            # Williams %R
            willr = talib.WILLR(high, low, close, timeperiod=14)
            
            # Money Flow Index
            mfi = talib.MFI(high, low, close, volume, timeperiod=14)
            
            # Commodity Channel Index
            cci = talib.CCI(high, low, close, timeperiod=20)
            
            # Rate of Change
            roc = talib.ROC(close, timeperiod=10)

            return {
                "rsi": {
                    "value": rsi[-1],
                    "signal": self._interpret_rsi(rsi[-1]),
                    "previous": rsi[-2]
                },
                "stochastic": {
                    "k": slowk[-1],
                    "d": slowd[-1],
                    "signal": self._interpret_stochastic(slowk[-1], slowd[-1])
                },
                "williams_r": {
                    "value": willr[-1],
                    "signal": self._interpret_williams_r(willr[-1])
                },
                "mfi": {
                    "value": mfi[-1],
                    "signal": self._interpret_mfi(mfi[-1])
                },
                "cci": {
                    "value": cci[-1],
                    "signal": self._interpret_cci(cci[-1])
                },
                "roc": {
                    "value": roc[-1],
                    "signal": self._interpret_roc(roc[-1])
                }
            }
        except Exception as e:
            return {"error": f"Momentum analysis failed: {str(e)}"}

    def _interpret_roc(self, value: float) -> Dict:
        """Interpret Rate of Change (ROC) values"""
        if value > 5:
            return {
                "signal": "Bullish",
                "strength": min(100, value * 10),
                "condition": "Strong Momentum"
            }
        elif value < -5:
            return {
                "signal": "Bearish",
                "strength": min(100, abs(value * 10)),
                "condition": "Strong Negative Momentum"
            }
        return {
            "signal": "Neutral",
            "strength": 0,
            "condition": "Weak Momentum"
        }

    def _analyze_trend(self, df: pd.DataFrame) -> Dict:
        """Enhanced trend analysis"""
        try:
            close = df['close'].values
            high = df['high'].values
            low = df['low'].values

            # Adjust minimum data requirement
            min_period = 50  # Changed from 200 to allow shorter timeframes
            if len(close) < min_period:
                ma_period = len(close) - 1
                if ma_period < 10:  # Absolute minimum requirement
                    return {"error": "Not enough data for trend analysis"}
            else:
                ma_period = min_period

            # Moving Averages
            ma20 = talib.SMA(close, timeperiod=min(20, ma_period))
            ma50 = talib.SMA(close, timeperiod=min(50, ma_period))
            ema20 = talib.EMA(close, timeperiod=min(20, ma_period))
            
            # MACD (requires at least 33 periods)
            if len(close) >= 33:
                macd, macd_signal, macd_hist = talib.MACD(close)
            else:
                macd = macd_signal = macd_hist = np.array([0])
            
            # ADX (requires 14 periods)
            if len(close) >= 14:
                adx = talib.ADX(high, low, close, timeperiod=14)
            else:
                adx = np.array([0])
            
            # Parabolic SAR
            sar = talib.SAR(high, low)

            # Get last valid index
            last_valid_index = -1
            while last_valid_index >= -len(close) and (
                np.isnan(ma20[last_valid_index]) or 
                np.isnan(ma50[last_valid_index])
            ):
                last_valid_index -= 1

            if last_valid_index < -len(close):
                return {"error": "Invalid data in trend analysis"}

            return {
                "moving_averages": {
                    "ma20": float(ma20[last_valid_index]),
                    "ma50": float(ma50[last_valid_index]),
                    "ema20": float(ema20[last_valid_index]),
                    "signal": self._interpret_mas(
                        float(close[last_valid_index]), 
                        float(ma20[last_valid_index]), 
                        float(ma50[last_valid_index]), 
                        float(ma50[last_valid_index])  # Using MA50 as long-term reference
                    )
                },
                "macd": {
                    "macd": float(macd[last_valid_index]),
                    "signal": float(macd_signal[last_valid_index]),
                    "histogram": float(macd_hist[last_valid_index]),
                    "interpretation": self._interpret_macd(
                        float(macd[last_valid_index]),
                        float(macd_signal[last_valid_index]),
                        float(macd_hist[last_valid_index])
                    )
                },
                "adx": {
                    "value": float(adx[last_valid_index]),
                    "strength": self._interpret_adx(float(adx[last_valid_index]))
                }
            }

        except Exception as e:
            return {"error": f"Trend analysis failed: {str(e)}"}

    def _get_signal_from_dict(self, data: Dict, key: str = 'signal') -> str:
        """Safely extract signal string from potentially nested dictionary"""
        if isinstance(data, dict):
            signal = data.get(key, 'Neutral')
            if isinstance(signal, dict):
                return signal.get(key, 'Neutral')
            return str(signal)
        return 'Neutral'

    def _generate_enhanced_summary(self, analysis: Dict) -> Dict:
        """Generate enhanced analysis summary with cross-validation"""
        signals = {
            "Bullish": 0,
            "Bearish": 0,
            "Neutral": 0
        }
        signal_strengths = []
        
        try:
            # Trend Analysis
            trend = analysis.get("trend_indicators", {})
            if isinstance(trend, dict) and "error" not in trend:
                # MACD Analysis
                macd_data = trend.get("macd", {}).get("interpretation", {})
                macd_signal = self._get_signal_from_dict(macd_data, 'crossover')
                if macd_signal in signals:
                    signals[macd_signal] += 1
                
                # Moving Averages
                ma_signal = trend.get("moving_averages", {}).get("signal", "Neutral")
                if ma_signal in signals:
                    signals[ma_signal] += 1

            # Momentum Analysis
            momentum = analysis.get("momentum_indicators", {})
            if isinstance(momentum, dict) and "error" not in momentum:
                # RSI
                rsi_data = momentum.get("rsi", {})
                rsi_signal = self._get_signal_from_dict(rsi_data)
                if rsi_signal in signals:
                    signals[rsi_signal] += 1
                    if isinstance(rsi_data, dict):
                        strength = rsi_data.get('strength', 0)
                        if isinstance(strength, (int, float)):
                            signal_strengths.append(strength)

                # Stochastic
                stoch_data = momentum.get("stochastic", {})
                stoch_signal = self._get_signal_from_dict(stoch_data)
                if stoch_signal in signals:
                    signals[stoch_signal] += 1
                    if isinstance(stoch_data, dict):
                        strength = stoch_data.get('strength', 0)
                        if isinstance(strength, (int, float)):
                            signal_strengths.append(strength)

            # Volume Analysis
            volume = analysis.get("volume_indicators", {})
            if isinstance(volume, dict):
                # OBV
                obv_signal = volume.get("obv", {}).get("signal", "Neutral")
                if obv_signal in signals:
                    signals[obv_signal] += 1

                # VWAP
                vwap_signal = volume.get("vwap", {}).get("signal", "Neutral")
                if vwap_signal in signals:
                    signals[vwap_signal] += 1

            # Calculate Overall Sentiment
            total_signals = sum(signals.values())
            if total_signals > 0:
                bullish_percentage = (signals["Bullish"] / total_signals) * 100
                bearish_percentage = (signals["Bearish"] / total_signals) * 100
                
                if bullish_percentage > 60:
                    overall_sentiment = "Bullish"
                elif bearish_percentage > 60:
                    overall_sentiment = "Bearish"
                else:
                    overall_sentiment = "Neutral"
                    
                signal_strength = np.mean(signal_strengths) if signal_strengths else 50
                confidence = min(100, (max(bullish_percentage, bearish_percentage) + signal_strength) / 2)
            else:
                overall_sentiment = "Neutral"
                confidence = 0

            # Generate key signals
            key_signals = []
            
            # Add significant signals
            if signals["Bullish"] > signals["Bearish"]:
                key_signals.append(("Bullish", f"Majority of indicators ({signals['Bullish']}/{total_signals}) showing bullish signals"))
            elif signals["Bearish"] > signals["Bullish"]:
                key_signals.append(("Bearish", f"Majority of indicators ({signals['Bearish']}/{total_signals}) showing bearish signals"))
            
            # Add volume signal if significant
            if volume.get("obv", {}).get("signal") != "Neutral":
                key_signals.append((
                    volume["obv"]["signal"],
                    f"Volume analysis shows {volume['obv']['signal'].lower()} trend"
                ))

            # Add momentum signal if significant
            if momentum.get("rsi", {}).get("value", 50) > 70:
                key_signals.append(("Bearish", "RSI indicates overbought conditions"))
            elif momentum.get("rsi", {}).get("value", 50) < 30:
                key_signals.append(("Bullish", "RSI indicates oversold conditions"))

            if not key_signals:
                key_signals.append(("Neutral", "No strong signals detected"))

            return {
                "overall_sentiment": overall_sentiment,
                "confidence": confidence,
                "signal_distribution": signals,
                "key_signals": key_signals,
                "risk_level": self._calculate_risk_level(analysis)
            }

        except Exception as e:
            print(f"Error in _generate_enhanced_summary: {str(e)}")
            return {
                "overall_sentiment": "Neutral",
                "confidence": 0,
                "signal_distribution": {"Bullish": 0, "Bearish": 0, "Neutral": 1},
                "key_signals": [("Neutral", "Analysis inconclusive")],
                "risk_level": {"level": 50, "category": "Medium", "factors": 0}
            }

    

    def _interpret_mas(self, close: float, ma20: float, ma50: float, ma200: float) -> str:
        """Interpret Moving Averages"""
        if close > ma20 and ma20 > ma50 and ma50 > ma200:
            return "Bullish"
        elif close < ma20 and ma20 < ma50 and ma50 < ma200:
            return "Bearish"
        elif close > ma200:
            return "Moderately Bullish"
        elif close < ma200:
            return "Moderately Bearish"
        else :
            return "Neutral"

    def _analyze_volume(self, df: pd.DataFrame) -> Dict:
        """Enhanced volume analysis"""
        close = df['close'].values
        volume = df['volume'].values
        high = df['high'].values
        low = df['low'].values

        try:
            # On Balance Volume
            obv = talib.OBV(close, volume)
            
            # Money Flow Index (already calculated in momentum)
            mfi = talib.MFI(high, low, close, volume, timeperiod=14)
            
            # Volume SMA
            vol_sma = talib.SMA(volume, timeperiod=20)
            
            # Calculate VWAP
            vwap = self._calculate_vwap(df)
            
            # Accumulation/Distribution Line
            ad = talib.AD(high, low, close, volume)
            
            # Chaikin Money Flow
            cmf = talib.ADOSC(high, low, close, volume, fastperiod=3, slowperiod=10)

            return {
                "obv": {
                    "value": obv[-1],
                    "change": ((obv[-1] - obv[-2]) / obv[-2] * 100) if obv[-2] != 0 else 0,
                    "signal": self._interpret_obv(obv[-3:])
                },
                "volume_sma": {
                    "current_volume": volume[-1],
                    "sma": vol_sma[-1],
                    "ratio": volume[-1] / vol_sma[-1] if vol_sma[-1] != 0 else 0
                },
                "vwap": {
                    "value": vwap[-1] if not pd.isna(vwap[-1]) else None,
                    "signal": self._interpret_vwap(close[-1], vwap[-1]) if not pd.isna(vwap[-1]) else None
                },
                "accumulation_distribution": {
                    "value": ad[-1],
                    "signal": self._interpret_ad(ad[-3:], close[-3:])
                },
                "chaikin_money_flow": {
                    "value": cmf[-1],
                    "signal": self._interpret_cmf(cmf[-1])
                }
            }
        except Exception as e:
            return {"error": f"Volume analysis failed: {str(e)}"}

    def _analyze_volatility(self, df: pd.DataFrame) -> Dict:
        """Enhanced volatility analysis"""
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values

        try:
            # Bollinger Bands
            upper, middle, lower = talib.BBANDS(close, timeperiod=20)
            
            # ATR
            atr = talib.ATR(high, low, close, timeperiod=14)
            
            # Standard Deviation
            stddev = talib.STDDEV(close, timeperiod=20)
            
            # Calculate Historical Volatility
            returns = np.log(close[1:] / close[:-1])
            hist_vol = np.std(returns) * np.sqrt(252) * 100  # Annualized

            return {
                "bollinger_bands": {
                    "upper": upper[-1],
                    "middle": middle[-1],
                    "lower": lower[-1],
                    "bandwidth": (upper[-1] - lower[-1]) / middle[-1] * 100,
                    "signal": self._interpret_bbands(close[-1], upper[-1], lower[-1])
                },
                "atr": {
                    "value": atr[-1],
                    "percentage": (atr[-1] / close[-1]) * 100,
                    "interpretation": self._interpret_atr(atr[-1], close[-1])
                },
                "historical_volatility": {
                    "value": hist_vol,
                    "interpretation": self._interpret_volatility(hist_vol)
                },
                "standard_deviation": {
                    "value": stddev[-1],
                    "relative": (stddev[-1] / close[-1]) * 100
                }
            }
        except Exception as e:
            return {"error": f"Volatility analysis failed: {str(e)}"}

    # Helper methods for calculations and interpretations...
    def _calculate_vwap(self, df: pd.DataFrame) -> np.ndarray:
        """Calculate VWAP"""
        df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
        df['vwap'] = (df['typical_price'] * df['volume']).cumsum() / df['volume'].cumsum()
        return df['vwap'].values

    def _calculate_ichimoku_line(self, high: np.ndarray, low: np.ndarray, period: int) -> np.ndarray:
        """Calculate Ichimoku lines"""
        period_high = pd.Series(high).rolling(window=period).max()
        period_low = pd.Series(low).rolling(window=period).min()
        return (period_high + period_low) / 2

    # Interpretation methods will be implemented in the next part...
    # ... Previous code remains the same until interpretation methods ...

    def _interpret_rsi(self, value: float) -> Dict:
        """Interpret RSI values"""
        if value > 70:
            return {
                "condition": "Overbought",
                "signal": "Bearish",
                "strength": min(100, (value - 70) * 3.33)  # Scale 0-100
            }
        elif value < 30:
            return {
                "condition": "Oversold",
                "signal": "Bullish",
                "strength": min(100, (30 - value) * 3.33)
            }
        return {
            "condition": "Neutral",
            "signal": "Neutral",
            "strength": 0
        }

    def _interpret_stochastic(self, k: float, d: float) -> Dict:
        """Interpret Stochastic oscillator"""
        signal = "Neutral"
        strength = 0
        
        if k > 80 and d > 80:
            signal = "Bearish"
            strength = min(100, (k - 80) * 5)
        elif k < 20 and d < 20:
            signal = "Bullish"
            strength = min(100, (20 - k) * 5)
        elif k > d:
            signal = "Bullish"
            strength = min(100, (k - d) * 2)
        elif d > k:
            signal = "Bearish"
            strength = min(100, (d - k) * 2)
            
        return {
            "signal": signal,
            "strength": strength,
            "crossover": "Bullish" if k > d else "Bearish"
        }

    def _interpret_williams_r(self, value: float) -> Dict:
        """Interpret Williams %R"""
        if value > -20:
            return {
                "condition": "Overbought",
                "signal": "Bearish",
                "strength": min(100, (-value + 20) * 5)
            }
        elif value < -80:
            return {
                "condition": "Oversold",
                "signal": "Bullish",
                "strength": min(100, (-80 - value) * 5)
            }
        return {
            "condition": "Neutral",
            "signal": "Neutral",
            "strength": 0
        }

    def _interpret_macd(self, macd: float, signal: float, hist: float) -> Dict:
        """Interpret MACD signals"""
        crossover = "None"
        if (macd > signal and hist > 0):
            crossover = "Bullish"
        elif (macd < signal and hist < 0):
            crossover = "Bearish"
            
        strength = min(100, abs(hist) * 100)
            
        return {
            "crossover": crossover,
            "strength": strength,
            "histogram_direction": "Up" if hist > 0 else "Down"
        }

    def _interpret_adx(self, value: float) -> Dict:
        """Interpret ADX strength"""
        if value >= 50:
            strength = "Very Strong"
            signal_strength = 100
        elif value >= 25:
            strength = "Strong"
            signal_strength = 75
        elif value >= 20:
            strength = "Moderate"
            signal_strength = 50
        else:
            strength = "Weak"
            signal_strength = 25
            
        return {
            "trend_strength": strength,
            "signal_strength": signal_strength
        }

    def _interpret_bbands(self, price: float, upper: float, lower: float) -> Dict:
        """Interpret Bollinger Bands"""
        bandwidth = (upper - lower) / ((upper + lower) / 2) * 100
        
        if price >= upper:
            return {
                "condition": "Overbought",
                "signal": "Bearish",
                "volatility": "High" if bandwidth > 20 else "Normal",
                "strength": min(100, ((price - upper) / upper) * 100)
            }
        elif price <= lower:
            return {
                "condition": "Oversold",
                "signal": "Bullish",
                "volatility": "High" if bandwidth > 20 else "Normal",
                "strength": min(100, ((lower - price) / lower) * 100)
            }
        return {
            "condition": "Neutral",
            "signal": "Neutral",
            "volatility": "High" if bandwidth > 20 else "Normal",
            "strength": 0
        }

    def _interpret_volume(self, current_volume: float, avg_volume: float) -> Dict:
        """Interpret volume signals"""
        vol_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        if vol_ratio >= 2:
            strength = "Very High"
            signal_strength = 100
        elif vol_ratio >= 1.5:
            strength = "High"
            signal_strength = 75
        elif vol_ratio >= 1:
            strength = "Normal"
            signal_strength = 50
        else:
            strength = "Low"
            signal_strength = 25
            
        return {
            "volume_strength": strength,
            "signal_strength": signal_strength,
            "ratio": vol_ratio
        }

    def _interpret_ichimoku(self, price: float, tenkan: float, kijun: float) -> Dict:
        """Interpret Ichimoku signals"""
        if price > tenkan and tenkan > kijun:
            return {
                "signal": "Bullish",
                "strength": min(100, ((price - kijun) / kijun) * 100),
                "condition": "Strong Uptrend"
            }
        elif price < tenkan and tenkan < kijun:
            return {
                "signal": "Bearish",
                "strength": min(100, ((kijun - price) / kijun) * 100),
                "condition": "Strong Downtrend"
            }
        return {
            "signal": "Neutral",
            "strength": 0,
            "condition": "Ranging"
        }

    

    def _get_key_signals(self, analysis: Dict) -> List[Tuple[str, str]]:
        """Extract key signals from analysis"""
        signals = []
        
        try:
            # Trend Signals
            trend_data = analysis.get("trend_indicators", {})
            if isinstance(trend_data, dict) and "macd" in trend_data:
                macd_data = trend_data["macd"]
                if macd_data.get("interpretation", {}).get("crossover") != "None":
                    signals.append((
                        macd_data["interpretation"]["crossover"],
                        f"MACD showing {macd_data['interpretation']['crossover'].lower()} crossover"
                    ))

            # Momentum Signals
            momentum_data = analysis.get("momentum_indicators", {})
            if isinstance(momentum_data, dict) and "rsi" in momentum_data:
                rsi_data = momentum_data["rsi"]
                if rsi_data.get("signal") != "Neutral":
                    signals.append((
                        rsi_data["signal"],
                        f"RSI indicates {rsi_data.get('condition', '').lower()} conditions"
                    ))

            # Volume Signals (since they're working)
            volume_data = analysis.get("volume_indicators", {})
            if isinstance(volume_data, dict):
                if volume_data.get("obv", {}).get("signal") != "Neutral":
                    signals.append((
                        volume_data["obv"]["signal"],
                        f"Volume analysis shows {volume_data['obv']['signal'].lower()} trend"
                    ))
            
                if volume_data.get("vwap", {}).get("signal") != "Neutral":
                    signals.append((
                        volume_data["vwap"]["signal"],
                        f"VWAP indicates {volume_data['vwap']['signal'].lower()} trend"
                    ))

            # Volatility Signals
            volatility_data = analysis.get("volatility_indicators", {})
            if isinstance(volatility_data, dict) and "bollinger_bands" in volatility_data:
                bb_data = volatility_data["bollinger_bands"]
                if bb_data.get("signal") != "Neutral":
                    signals.append((
                        bb_data["signal"],
                        f"Bollinger Bands indicate {bb_data.get('condition', '').lower()} conditions"
                    ))

        except Exception as e:
            print(f"Error in _get_key_signals: {str(e)}")
            # Add a default signal if there's an error
            signals.append(("Neutral", "Unable to generate detailed signals"))

        return signals

    def _calculate_risk_level(self, analysis: Dict) -> Dict:
        """Calculate overall risk level"""
        risk_factors = []
        
        # Volatility risk
        volatility = analysis["volatility_indicators"]
        if "error" not in volatility:
            bb_width = volatility["bollinger_bands"]["bandwidth"]
            risk_factors.append(min(100, bb_width))
            
        # Trend strength risk (inverse of ADX)
        trend = analysis["trend_indicators"]
        if "error" not in trend:
            adx_value = trend["adx"]["value"]
            risk_factors.append(100 - min(100, adx_value))
            
        # Volume risk
        volume = analysis["volume_indicators"]
        if "error" not in volume:
            vol_ratio = volume["volume_sma"]["ratio"]
            risk_factors.append(min(100, vol_ratio * 50))
            
        # Calculate overall risk
        risk_level = np.mean(risk_factors) if risk_factors else 50
        
        return {
            "level": risk_level,
            "category": "High" if risk_level > 70 else "Medium" if risk_level > 30 else "Low",
            "factors": len(risk_factors)
        }
        
    def _interpret_mas(self, current_price: float, ma20: float, ma50: float, ma200: float) -> str:
        """Interpret Moving Averages"""
        if current_price > ma20 and ma20 > ma50 and ma50 > ma200:
            return "Bullish"
        elif current_price < ma20 and ma20 < ma50 and ma50 < ma200:
            return "Bearish"
        elif current_price > ma50 and ma50 > ma200:
            return "Moderately Bullish"
        elif current_price < ma50 and ma50 < ma200:
            return "Moderately Bearish"
        return "Neutral"

    def _interpret_mfi(self, value: float) -> Dict:
        """Interpret Money Flow Index"""
        if value > 80:
            return {
                "condition": "Overbought",
                "signal": "Bearish",
                "strength": min(100, (value - 80) * 5)
            }
        elif value < 20:
            return {
                "condition": "Oversold",
                "signal": "Bullish",
                "strength": min(100, (20 - value) * 5)
            }
        return {
            "condition": "Neutral",
            "signal": "Neutral",
            "strength": 0
        }

    def _interpret_obv(self, obv_values: np.ndarray) -> str:
        """Interpret On Balance Volume"""
        if len(obv_values) < 2:
            return "Neutral"
        
        obv_change = obv_values[-1] - obv_values[0]
        
        if obv_change > 0:
            return "Bullish"
        elif obv_change < 0:
            return "Bearish"
        return "Neutral"

    def _interpret_ad(self, ad_values: np.ndarray, price_values: np.ndarray) -> str:
        """Interpret Accumulation/Distribution"""
        if len(ad_values) < 2 or len(price_values) < 2:
            return "Neutral"
            
        ad_change = ad_values[-1] - ad_values[0]
        price_change = price_values[-1] - price_values[0]
        
        if ad_change > 0 and price_change < 0:
            return "Bullish"  # Accumulation
        elif ad_change < 0 and price_change > 0:
            return "Bearish"  # Distribution
        return "Neutral"

    def _interpret_cmf(self, value: float) -> str:
        """Interpret Chaikin Money Flow"""
        if value > 0.25:
            return "Bullish"
        elif value < -0.25:
            return "Bearish"
        return "Neutral"

    def _interpret_atr(self, atr_value: float, current_price: float) -> Dict:
        """Interpret Average True Range"""
        atr_percentage = (atr_value / current_price) * 100
        
        if atr_percentage > 5:
            volatility = "Very High"
            risk = "High"
        elif atr_percentage > 3:
            volatility = "High"
            risk = "Moderate to High"
        elif atr_percentage > 1:
            volatility = "Moderate"
            risk = "Moderate"
        else:
            volatility = "Low"
            risk = "Low"
            
        return {
            "volatility": volatility,
            "risk": risk,
            "atr_percentage": atr_percentage
        }

    def _interpret_vwap(self, current_price: float, vwap: float) -> str:
        """Interpret VWAP"""
        if current_price > vwap:
            return "Bullish"
        elif current_price < vwap:
            return "Bearish"
        return "Neutral"

    def _interpret_volatility(self, volatility: float) -> str:
        """Interpret Historical Volatility"""
        if volatility > 100:
            return "Extremely High"
        elif volatility > 50:
            return "Very High"
        elif volatility > 30:
            return "High"
        elif volatility > 20:
            return "Moderate"
        return "Low"
    
    def _interpret_cci(self, value: float) -> Dict:
        """Interpret CCI values"""
        if value > 100:
            return {
                "condition": "Overbought",
                "signal": "Bearish",
                "strength": min(100, (value - 100))
            }
        elif value < -100:
            return {
                "condition": "Oversold",
                "signal": "Bullish",
                "strength": min(100, abs(value + 100))
            }
        return {
            "condition": "Neutral",
            "signal": "Neutral",
            "strength": 0
        }
    
  