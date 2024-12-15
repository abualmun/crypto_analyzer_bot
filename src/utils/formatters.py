from typing import Dict, List
import json
import os

class TelegramFormatter:
    def __init__(self):
        self.languages = {
            'en': self._load_language('en'),
            'ar': self._load_language('ar')
        }
        self.current_language = 'en'

    def _load_language(self, lang_code: str) -> Dict:
        try:
            file_path = os.path.join('src', 'languages', lang_code, 'messages.json')
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception:
            return {}

    def set_language(self, lang_code: str):
        if lang_code in self.languages:
            self.current_language = lang_code

    def _t(self, key: str) -> str:
        """Get translation for key"""
        return self.languages[self.current_language].get(key, key)

    def format_full_analysis(self, analysis: Dict, coin_id: str) -> str:
        """Format comprehensive analysis results"""
        try:
            if "error" in analysis:
                return f"⚠️ {self._t('error_analysis')}: {analysis['error']}"

            sections = []

            # Header Section
            if 'basic_info' in analysis:
                header = self._format_header(analysis['basic_info'], coin_id)
                sections.append(header)

            # Trend Analysis
            if 'trend_indicators' in analysis:
                trend = self._format_trend_analysis(analysis['trend_indicators'])
                sections.append(trend)

            # Momentum Analysis
            if 'momentum_indicators' in analysis:
                momentum = self._format_momentum_analysis(analysis['momentum_indicators'])
                sections.append(momentum)

            # Volume Analysis
            if 'volume_indicators' in analysis:
                volume = self._format_volume_analysis(analysis['volume_indicators'])
                sections.append(volume)

            # Volatility Analysis
            if 'volatility_indicators' in analysis:
                volatility = self._format_volatility_analysis(analysis['volatility_indicators'])
                sections.append(volatility)

            # Pattern Recognition
            if analysis.get('patterns', {}).get('patterns'):
                patterns = self._format_patterns(analysis['patterns'])
                if patterns:  # Only add if there are patterns
                    sections.append(patterns)

            # Support/Resistance
            if 'support_resistance' in analysis:
                sr_levels = self._format_support_resistance(analysis['support_resistance'])
                sections.append(sr_levels)

            # Risk Assessment
            if 'summary' in analysis:
                risk = self._format_risk_assessment(analysis['summary'])
                sections.append(risk)

                # Final Summary
                summary = self._format_summary(analysis['summary'])
                sections.append(summary)

            return "\n\n".join(filter(None, sections))  # Filter out empty sections

        except Exception as e:
            print(f"Error in format_full_analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"⚠️ Error formatting analysis: {str(e)}"

    def _format_header(self, info: Dict, coin_id: str) -> str:
        """Format basic information header"""
        price_change = info['price_change_24h']
        change_arrow = "🔺" if price_change > 0 else "🔻"
        
        return (
            f"📊 {self._t('analysis_for')} {coin_id.upper()}\n"
            f"{'═' * 32}\n"
            f"💰 {self._t('current_price')}: ${info['current_price']:,.2f}\n"
            f"📈 24h {self._t('change')}: {change_arrow} {abs(price_change):.2f}%\n"
            f"💎 24h {self._t('high')}: ${info['high_24h']:,.2f}\n"
            f"💫 24h {self._t('low')}: ${info['low_24h']:,.2f}\n"
            f"📊 24h {self._t('volume')}: ${info['volume_24h']:,.0f}"
        )

    def _format_trend_analysis(self, trend: Dict) -> str:
        """Format trend indicators"""
        try:
            # Get moving averages data
            ma_data = trend.get('moving_averages', {})
            macd_data = trend.get('macd', {})
            adx_data = trend.get('adx', {})
            
            # Format moving averages section
            ma_section = [
                f"📈 {self._t('trend_analysis')}",
                f"{'─' * 32}",
                f"• MA20: ${ma_data.get('ma20', 0):,.2f}",
                f"• MA50: ${ma_data.get('ma50', 0):,.2f}",
                f"• EMA20: ${ma_data.get('ema20', 0):,.2f}",
                f"• {self._t('trend_signal')}: {self._format_signal(ma_data.get('signal', 'Neutral'))}"
            ]
            
            # Format MACD section
            macd_section = [
                "",
                "• MACD:",
                f"  - Value: {macd_data.get('macd', 0):,.2f}",
                f"  - Signal: {macd_data.get('signal', 0):,.2f}",
                f"  - Histogram: {macd_data.get('histogram', 0):,.2f}",
                f"  - Cross: {macd_data.get('interpretation', {}).get('crossover', 'N/A')}"
            ]
            
            # Format ADX section
            adx_section = [
                "",
                "• ADX:",
                f"  - Value: {adx_data.get('value', 0):,.2f}",
                f"  - Trend Strength: {adx_data.get('strength', {}).get('trend_strength', 'N/A')}"
            ]
            
            # Combine all sections
            return "\n".join(ma_section + macd_section + adx_section)
            
        except Exception as e:
            print(f"Debug: Error in trend formatting: {str(e)}")
            return f"📈 {self._t('trend_analysis')}\n{'─' * 32}\nError formatting trend data: {str(e)}"

    def _get_trend_emoji(self, trend: str) -> str:
        """Get emoji for trend signal"""
        emoji_map = {
            'Strong Bullish': '🟢',
            'Bullish': '🟢',
            'Neutral': '⚪',
            'Bearish': '🔴',
            'Strong Bearish': '🔴'
        }
        return emoji_map.get(trend, '⚪')

    def format_full_analysis(self, analysis: Dict, coin_id: str) -> str:
        """Format comprehensive analysis results"""
        print("\nDebug: Starting format_full_analysis")  # Debug print
        
        try:
            if "error" in analysis:
                return f"⚠️ {self._t('error_analysis')}: {analysis['error']}"

            sections = []

            # Header Section
            print("Debug: Formatting header")  # Debug print
            if 'basic_info' in analysis:
                header = self._format_header(analysis['basic_info'], coin_id)
                sections.append(header)

            # Trend Analysis
            print("Debug: Formatting trend")  # Debug print
            if 'trend_indicators' in analysis:
                trend = self._format_trend_analysis(analysis['trend_indicators'])
                sections.append(trend)

            # Momentum Analysis
            print("Debug: Formatting momentum")  # Debug print
            if 'momentum_indicators' in analysis:
                momentum = self._format_momentum_analysis(analysis['momentum_indicators'])
                sections.append(momentum)

            # Volume Analysis
            print("Debug: Formatting volume")  # Debug print
            if 'volume_indicators' in analysis:
                volume = self._format_volume_analysis(analysis['volume_indicators'])
                sections.append(volume)

            # Volatility Analysis
            print("Debug: Formatting volatility")  # Debug print
            if 'volatility_indicators' in analysis:
                volatility = self._format_volatility_analysis(analysis['volatility_indicators'])
                sections.append(volatility)

            print("Debug: Joining sections")  # Debug print
            return "\n\n".join(sections)

        except Exception as e:
            print(f"Debug: Error in format_full_analysis: {str(e)}")  # Debug print
            import traceback
            print("Debug: Full traceback:", traceback.format_exc())  # Debug print
            return f"Error formatting analysis: {str(e)}"

    

    
    def _format_risk_assessment(self, summary: Dict) -> str:
        """Format risk assessment"""
        risk_level = summary.get('risk_level', 'Medium')
        risk_emoji = {
            'Low': '🟢',
            'Medium': '🟡',
            'High': '🔴',
            'Very High': '⛔'
        }.get(risk_level, '⚪')
        
        return (
            f"⚠️ {self._t('risk_assessment')}\n"
            f"{'─' * 32}\n"
            f"• {self._t('risk_level')}: {risk_emoji} {risk_level}\n"
            f"• {self._t('volatility_level')}: {summary.get('volatility_assessment', 'N/A')}\n"
            f"• {self._t('market_strength')}: {summary.get('market_strength', 'N/A')}"
        )

    def _format_summary(self, summary: Dict) -> str:
        """Format final summary"""
        signals = summary.get('signals', [])
        confidence = summary.get('confidence', 0)
        
        summary_text = [
            f"📝 {self._t('summary')}",
            f"{'─' * 32}",
            f"• {self._t('overall_sentiment')}: {self._get_sentiment_emoji(summary['overall_sentiment'])} {summary['overall_sentiment']}",
            f"• {self._t('confidence')}: {confidence}%",
            "",
            f"🎯 {self._t('key_signals')}:"
        ]
        
        for signal in signals:
            emoji = self._get_sentiment_emoji(signal[0])
            summary_text.append(f"• {emoji} {signal[1]}")
        
        return "\n".join(summary_text)

    # Helper formatting methods
    def _format_rsi(self, rsi_data: Dict) -> str:
        value = rsi_data['value']
        signal = rsi_data['signal']
        return f"{value:.1f} {self._get_rsi_emoji(value)} ({signal})"

    def _format_macd_data(self, macd_data: Dict) -> str:
        return f"{macd_data['macd']:.2f} [{macd_data['interpretation']}]"

    def _get_trend_emoji(self, trend: str) -> str:
        return {
            'Strong Bullish': '🟢',
            'Bullish': '🟢',
            'Neutral': '⚪',
            'Bearish': '🔴',
            'Strong Bearish': '🔴'
        }.get(trend, '⚪')

    def _get_sentiment_emoji(self, sentiment: str) -> str :
        """Get emoji for sentiment"""
        return {
            'Bullish': '📈',
            'Bearish': '📉',
            'Neutral': '↔️',
            'Strong Bullish': '🚀',
            'Strong Bearish': '🔻'
        }.get(sentiment, '↔️')

    def _get_rsi_emoji(self, value: float) -> str:
        if value >= 70: return '🔥'
        if value <= 30: return '❄️'
        return '➖'

    # Error handling
    def format_error_message(self, error: str) -> str:
        """Format error messages"""
        return f"⚠️ {self._t('error')}: {error}"

    def format_loading_message(self) -> str:
        """Format loading message"""
        return f"⏳ {self._t('analyzing')}..."
    
    def _format_stochastic(self, stoch_data: Dict) -> str:
        """Format stochastic oscillator data"""
        k = stoch_data['k']
        d = stoch_data['d']
        signal = stoch_data['signal']
        
        if k > 80 or k < 20:
            emoji = "🔥" if k > 80 else "❄️"
        else:
            emoji = "➖"
            
        return f"K:{k:.1f} D:{d:.1f} {emoji} [{signal}]"

    def _format_cci(self, cci_data: Dict) -> str:
        """Format CCI data"""
        value = cci_data['value']
        signal = cci_data['signal']
        
        if value > 100:
            emoji = "🔥"
        elif value < -100:
            emoji = "❄️"
        else:
            emoji = "➖"
            
        return f"{value:.1f} {emoji} [{signal}]"

    def _format_mfi(self, mfi_data: Dict) -> str:
        """Format Money Flow Index data"""
        value = mfi_data['value']
        signal = mfi_data['signal']
        
        if value > 80:
            emoji = "🔥"
        elif value < 20:
            emoji = "❄️"
        else:
            emoji = "➖"
            
        return f"{value:.1f} {emoji} [{signal}]"

    def _format_roc(self, roc_data: Dict) -> str:
        """Format Rate of Change data"""
        value = roc_data['value']
        signal = roc_data['signal']
        
        if value > 0:
            emoji = "📈"
        elif value < 0:
            emoji = "📉"
        else:
            emoji = "➖"
            
        return f"{value:.1f}% {emoji} [{signal}]"

    def _format_williams_r(self, williams_data: Dict) -> str:
        """Format Williams %R data"""
        value = williams_data['value']
        signal = williams_data['signal']
        
        if value > -20:
            emoji = "🔥"
        elif value < -80:
            emoji = "❄️"
        else:
            emoji = "➖"
            
        return f"{value:.1f} {emoji} [{signal}]"

    def _format_obv(self, obv_data: Dict) -> str:
        """Format On Balance Volume data"""
        value = obv_data['value']
        change = obv_data['change']
        signal = obv_data['signal']
        
        if change > 0:
            emoji = "📈"
        elif change < 0:
            emoji = "📉"
        else:
            emoji = "➖"
            
        return f"{self._format_large_number(value)} {emoji} [{signal}]"

    def _format_vwap(self, vwap_data: Dict) -> str:
        """Format VWAP data"""
        value = vwap_data['value']
        signal = vwap_data['signal']
        
        return f"${value:,.2f} [{signal}]"

    def _format_cmf(self, cmf_data: Dict) -> str:
        """Format Chaikin Money Flow data"""
        value = cmf_data['value']
        signal = cmf_data['signal']
        
        if value > 0.1:
            emoji = "📈"
        elif value < -0.1:
            emoji = "📉"
        else:
            emoji = "➖"
            
        return f"{value:.3f} {emoji} [{signal}]"

    def _format_ad(self, ad_data: Dict) -> str:
        """Format Accumulation/Distribution data"""
        signal = ad_data['signal']
        
        if signal == "Accumulation":
            emoji = "📈"
        elif signal == "Distribution":
            emoji = "📉"
        else:
            emoji = "➖"
            
        return f"{emoji} [{signal}]"

    def _format_atr(self, atr_data: Dict) -> str:
        """Format Average True Range data"""
        value = atr_data['value']
        percentage = atr_data['percentage']
        interpretation = atr_data['interpretation']
        
        return f"${value:.2f} ({percentage:.1f}%) [{interpretation}]"

    def _format_historical_volatility(self, vol_data: Dict) -> str:
        """Format Historical Volatility data"""
        value = vol_data['value']
        interpretation = vol_data['interpretation']
        
        if value > 50:
            emoji = "🔥"
        elif value < 20:
            emoji = "❄️"
        else:
            emoji = "➖"
            
        return f"{value:.1f}% {emoji} [{interpretation}]"

    def _format_large_number(self, number: float) -> str:
        """Format large numbers with K, M, B suffixes"""
        if abs(number) >= 1e9:
            return f"{number/1e9:.2f}B"
        elif abs(number) >= 1e6:
            return f"{number/1e6:.2f}M"
        elif abs(number) >= 1e3:
            return f"{number/1e3:.2f}K"
        else:
            return f"{number:.2f}"

    def _format_support_resistance(self, levels: Dict) -> str:
        """Format support and resistance levels"""
        support_levels = levels.get('support_levels', [])
        resistance_levels = levels.get('resistance_levels', [])
        
        formatted_lines = [
            f"🎯 {self._t('support_resistance')}",
            f"{'─' * 32}"
        ]
        
        if resistance_levels:
            formatted_lines.append(f"• {self._t('resistance_at')}: ${resistance_levels[0]:,.2f}")
            if len(resistance_levels) > 1:
                formatted_lines.append(f"• {self._t('next_resistance')}: ${resistance_levels[1]:,.2f}")
                
        if support_levels:
            formatted_lines.append(f"• {self._t('support_at')}: ${support_levels[-1]:,.2f}")
            if len(support_levels) > 1:
                formatted_lines.append(f"• {self._t('next_support')}: ${support_levels[-2]:,.2f}")
                
        return "\n".join(formatted_lines)

    def _format_patterns(self, patterns: Dict) -> str:
        """Format pattern recognition results"""
        pattern_list = patterns.get('patterns', {})
        if not pattern_list:
            return ""
            
        formatted_lines = [
            f"🔮 {self._t('patterns_detected')}",
            f"{'─' * 32}"
        ]
        
        for pattern_name in pattern_list:
            formatted_name = pattern_name.replace('_', ' ').title()
            formatted_lines.append(f"• {formatted_name}")
            
        return "\n".join(formatted_lines)
    
    def _format_volume_trend(self, volume_data: Dict) -> str:
        """Format volume trend data"""
        current = volume_data['current_volume']
        sma = volume_data['sma']
        ratio = volume_data['ratio']
        
        if ratio > 1.5:
            trend = f"🔥 {self._t('very_high')}"
        elif ratio > 1.2:
            trend = f"📈 {self._t('high')}"
        elif ratio < 0.8:
            trend = f"📉 {self._t('low')}"
        elif ratio < 0.5:
            trend = f"❄️ {self._t('very_low')}"
        else:
            trend = f"➖ {self._t('normal')}"
            
        return f"{self._format_large_number(current)} / {self._format_large_number(sma)} [{trend}]"

    def _format_price_action(self, price_data: Dict) -> str:
        """Format price action data"""
        trend = price_data['trend']
        strength = price_data['strength']
        
        emoji = {
            'Strong Uptrend': '🚀',
            'Uptrend': '📈',
            'Sideways': '↔️',
            'Downtrend': '📉',
            'Strong Downtrend': '💥'
        }.get(trend, '➖')
        
        return f"{emoji} {trend} ({strength}%)"

    def _format_fibonacci_levels(self, fib_data: Dict) -> str:
        """Format Fibonacci retracement levels"""
        levels = [
            f"• 0.236: ${fib_data['0.236']:,.2f}",
            f"• 0.382: ${fib_data['0.382']:,.2f}",
            f"• 0.500: ${fib_data['0.500']:,.2f}",
            f"• 0.618: ${fib_data['0.618']:,.2f}",
            f"• 0.786: ${fib_data['0.786']:,.2f}"
        ]
        return "\n".join(levels)

    def _format_pivot_points(self, pivot_data: Dict) -> str:
        """Format pivot points"""
        return (
            f"P: ${pivot_data['P']:,.2f}\n"
            f"R1: ${pivot_data['R1']:,.2f}\n"
            f"R2: ${pivot_data['R2']:,.2f}\n"
            f"S1: ${pivot_data['S1']:,.2f}\n"
            f"S2: ${pivot_data['S2']:,.2f}"
        )

    def _format_moving_averages(self, ma_data: Dict) -> str:
        """Format moving averages data"""
        crosses = []
        for ma in ['MA20', 'MA50', 'MA200']:
            if ma_data[ma.lower()]['cross'] == 'above':
                crosses.append(f"↗️ Price above {ma}")
            elif ma_data[ma.lower()]['cross'] == 'below':
                crosses.append(f"↘️ Price below {ma}")
                
        return "\n".join(crosses) if crosses else "↔️ No significant crosses"

    def _format_volatility_bands(self, bands_data: Dict) -> str:
        """Format volatility bands data"""
        position = bands_data['position']
        
        if position == 'above':
            return "🔥 Price above bands (High volatility)"
        elif position == 'below':
            return "❄️ Price below bands (Low volatility)"
        else:
            return "➖ Price within bands (Normal volatility)"

    def _format_trend_strength(self, strength_data: Dict) -> str:
        """Format trend strength indicator"""
        strength = strength_data['value']
        direction = strength_data['direction']
        
        if strength > 40:
            emoji = "💪"
        elif strength > 20:
            emoji = "👍"
        else:
            emoji = "👋"
            
        return f"{emoji} {direction} ({strength}%)"

    def _format_divergence(self, divergence_data: Dict) -> str:
        """Format divergence signals"""
        if not divergence_data['present']:
            return "No divergence detected"
            
        type_emoji = {
            'bullish': '🟢',
            'bearish': '🔴',
            'hidden_bullish': '🟡',
            'hidden_bearish': '🟡'
        }
        
        return f"{type_emoji[divergence_data['type']]} {divergence_data['type'].replace('_', ' ').title()} divergence"

    def _format_pattern_confidence(self, pattern_data: Dict) -> str:
        """Format pattern confidence levels"""
        confidence = pattern_data['confidence']
        
        if confidence >= 80:
            emoji = "🎯"
        elif confidence >= 60:
            emoji = "✅"
        else:
            emoji = "⚠️"
            
        return f"{emoji} {confidence}% confidence"

    def _format_market_condition(self, condition_data: Dict) -> str:
        """Format overall market condition"""
        condition = condition_data['condition']
        strength = condition_data['strength']
        
        emojis = {
            'Strong Bull': '🚀',
            'Bull': '📈',
            'Neutral': '↔️',
            'Bear': '📉',
            'Strong Bear': '💥'
        }
        
        return f"{emojis.get(condition, '➖')} {condition} ({strength}%)"

    def _format_risk_rating(self, risk_data: Dict) -> str:
        """Format risk rating"""
        risk_level = risk_data['level']
        score = risk_data['score']
        
        emojis = {
            'Very High': '⛔',
            'High': '🔴',
            'Medium': '🟡',
            'Low': '🟢',
            'Very Low': '💚'
        }
        
        return f"{emojis.get(risk_level, '⚪')} {risk_level} Risk ({score}%)"

    def _format_signal(self, signal: str) -> str:
        """Format signal with appropriate emoji"""
        emoji_map = {
            'Strong Bullish': '🟢',
            'Bullish': '🟢',
            'Neutral': '⚪',
            'Bearish': '🔴',
            'Strong Bearish': '🔴'
        }
        emoji = emoji_map.get(signal, '⚪')
        return f"{emoji} {signal}"

    def _format_consolidated_rating(self, rating_data: Dict) -> str:
        """Format consolidated analysis rating"""
        rating = rating_data['rating']
        score = rating_data['score']
        
        emojis = {
            'Strong Buy': '🟢',
            'Buy': '🟢',
            'Neutral': '⚪',
            'Sell': '🔴',
            'Strong Sell': '🔴'
        }
        
        return f"{emojis.get(rating, '⚪')} {rating} ({score}%)"
    
    
    def _format_momentum_analysis(self, momentum: Dict) -> str:
        """Format momentum indicators"""
        try:
            # Start momentum section
            sections = [
                f"🔄 {self._t('momentum_analysis')}",
                f"{'─' * 32}"
            ]
            
            # RSI
            if 'rsi' in momentum:
                rsi_data = momentum['rsi']
                rsi_value = rsi_data.get('value', 0)
                rsi_signal = self._get_rsi_signal(rsi_value)
                sections.append(f"• RSI: {rsi_value:.2f} {rsi_signal}")
            
            # Stochastic
            if 'stochastic' in momentum:
                stoch = momentum['stochastic']
                sections.append(f"• Stochastic: K({stoch.get('k', 0):.1f}) D({stoch.get('d', 0):.1f})")
            
            # Williams %R
            if 'williams_r' in momentum:
                williams = momentum['williams_r']
                sections.append(f"• Williams %R: {williams.get('value', 0):.1f}")
            
            # MFI
            if 'mfi' in momentum:
                mfi = momentum['mfi']
                sections.append(f"• Money Flow Index: {mfi.get('value', 0):.1f}")
            
            # CCI
            if 'cci' in momentum:
                cci = momentum['cci']
                sections.append(f"• CCI: {cci.get('value', 0):.1f}")
            
            return "\n".join(sections)
        except Exception as e:
            return f"🔄 {self._t('momentum_analysis')}\n{'─' * 32}\nError: {str(e)}"

    def _format_volume_analysis(self, volume: Dict) -> str:
        """Format volume indicators"""
        try:
            sections = [
                f"📊 {self._t('volume_analysis')}",
                f"{'─' * 32}"
            ]
            
            # Volume SMA
            if 'volume_sma' in volume:
                vol_sma = volume['volume_sma']
                current_vol = self._format_large_number(vol_sma.get('current_volume', 0))
                avg_vol = self._format_large_number(vol_sma.get('sma', 0))
                sections.append(f"• Current Volume: {current_vol}")
                sections.append(f"• Average Volume: {avg_vol}")
            
            # OBV
            if 'obv' in volume:
                obv_data = volume['obv']
                sections.append(f"• OBV: {self._format_large_number(obv_data.get('value', 0))}")
            
            # VWAP
            if 'vwap' in volume:
                vwap_data = volume['vwap']
                sections.append(f"• VWAP: ${vwap_data.get('value', 0):,.2f}")
            
            # Chaikin Money Flow
            if 'chaikin_money_flow' in volume:
                cmf = volume['chaikin_money_flow']
                sections.append(f"• CMF: {cmf.get('value', 0):.3f}")
            
            return "\n".join(sections)
        except Exception as e:
            return f"📊 {self._t('volume_analysis')}\n{'─' * 32}\nError: {str(e)}"

    def _format_volatility_analysis(self, volatility: Dict) -> str:
        """Format volatility indicators"""
        try:
            sections = [
                f"📉 {self._t('volatility_analysis')}",
                f"{'─' * 32}"
            ]
            
            # Bollinger Bands
            if 'bollinger_bands' in volatility:
                bb = volatility['bollinger_bands']
                sections.extend([
                    f"• Bollinger Bands:",
                    f"  - Upper: ${bb.get('upper', 0):,.2f}",
                    f"  - Middle: ${bb.get('middle', 0):,.2f}",
                    f"  - Lower: ${bb.get('lower', 0):,.2f}",
                    f"  - Width: {bb.get('bandwidth', 0):.2f}%"
                ])
            
            # ATR
            if 'atr' in volatility:
                atr = volatility['atr']
                sections.append(f"• ATR: ${atr.get('value', 0):,.2f} ({atr.get('percentage', 0):.1f}%)")
            
            # Historical Volatility
            if 'historical_volatility' in volatility:
                hist_vol = volatility['historical_volatility']
                sections.append(f"• Historical Volatility: {hist_vol.get('value', 0):.1f}%")
            
            return "\n".join(sections)
        except Exception as e:
            return f"📉 {self._t('volatility_analysis')}\n{'─' * 32}\nError: {str(e)}"

    def _get_rsi_signal(self, value: float) -> str:
        """Get RSI signal with emoji"""
        if value >= 70:
            return "🔥 Overbought"
        elif value <= 30:
            return "❄️ Oversold"
        else:
            return "➖ Neutral"


    
    
    