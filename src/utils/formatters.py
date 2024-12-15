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
        if "error" in analysis:
            return f"⚠️ {self._t('error_analysis')}: {analysis['error']}"

        sections = []

        # Header Section
        header = self._format_header(analysis['basic_info'], coin_id)
        sections.append(header)

        # Trend Analysis
        trend = self._format_trend_analysis(analysis['trend_indicators'])
        sections.append(trend)

        # Momentum Analysis
        momentum = self._format_momentum_analysis(analysis['momentum_indicators'])
        sections.append(momentum)

        # Volume Analysis
        volume = self._format_volume_analysis(analysis['volume_indicators'])
        sections.append(volume)

        # Volatility Analysis
        volatility = self._format_volatility_analysis(analysis['volatility_indicators'])
        sections.append(volatility)

        # Pattern Recognition
        if analysis.get('patterns', {}).get('patterns'):
            patterns = self._format_patterns(analysis['patterns'])
            sections.append(patterns)

        # Support/Resistance
        sr_levels = self._format_support_resistance(analysis['support_resistance'])
        sections.append(sr_levels)

        # Risk Assessment
        risk = self._format_risk_assessment(analysis['summary'])
        sections.append(risk)

        # Final Summary
        summary = self._format_summary(analysis['summary'])
        sections.append(summary)

        return "\n\n".join(sections)

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
            ma_data = trend['moving_averages']
            
            # Get MACD data
            macd_data = trend['macd']
            macd_interpretation = macd_data['interpretation']
            
            # Get ADX data
            adx_data = trend['adx']
            adx_strength = adx_data['strength']

            # Format the section
            return (
                f"📈 {self._t('trend_analysis')}\n"
                f"{'─' * 32}\n"
                f"• MA20: ${ma_data['ma20']:,.2f}\n"
                f"• MA50: ${ma_data['ma50']:,.2f}\n"
                f"• EMA20: ${ma_data['ema20']:,.2f}\n"
                f"• {self._t('trend_signal')}: {self._get_trend_emoji(ma_data['signal'])} {ma_data['signal']}\n\n"
                f"• MACD:\n"
                f"  - Value: {macd_data['macd']:.2f}\n"
                f"  - Signal: {macd_data['signal']:.2f}\n"
                f"  - Histogram: {macd_data['histogram']:.2f}\n"
                f"  - Cross: {macd_interpretation['crossover']}\n"
                f"  - Strength: {macd_interpretation['strength']}%\n\n"
                f"• ADX:\n"
                f"  - Value: {adx_data['value']:.1f}\n"
                f"  - Trend Strength: {adx_strength['trend_strength']}\n"
                f"  - Signal Strength: {adx_strength['signal_strength']}%"
            )
        except Exception as e:
            return f"📈 {self._t('trend_analysis')}\n{'─' * 32}\nError formatting trend data: {str(e)}"

    def _format_momentum_analysis(self, momentum: Dict) -> str:
        """Format momentum indicators"""
        return (
            f"🔄 {self._t('momentum_analysis')}\n"
            f"{'─' * 32}\n"
            f"• RSI: {self._format_rsi(momentum['rsi'])}\n"
            f"• {self._t('stochastic')}: {self._format_stochastic(momentum['stochastic'])}\n"
            f"• CCI: {self._format_cci(momentum['cci'])}\n"
            f"• MFI: {self._format_mfi(momentum['mfi'])}\n"
            f"• ROC: {self._format_roc(momentum['roc'])}\n"
            f"• Williams %R: {self._format_williams_r(momentum['williams_r'])}"
        )

    def _format_volume_analysis(self, volume: Dict) -> str:
        """Format volume indicators"""
        return (
            f"📊 {self._t('volume_analysis')}\n"
            f"{'─' * 32}\n"
            f"• {self._t('volume_trend')}: {self._format_volume_trend(volume['volume_sma'])}\n"
            f"• OBV: {self._format_obv(volume['obv'])}\n"
            f"• VWAP: {self._format_vwap(volume['vwap'])}\n"
            f"• CMF: {self._format_cmf(volume['chaikin_money_flow'])}\n"
            f"• A/D Line: {self._format_ad(volume['accumulation_distribution'])}"
        )

    def _format_volatility_analysis(self, volatility: Dict) -> str:
        """Format volatility indicators"""
        bb = volatility['bollinger_bands']
        return (
            f"📉 {self._t('volatility_analysis')}\n"
            f"{'─' * 32}\n"
            f"• {self._t('bollinger_bands')}:\n"
            f"  Upper: ${bb['upper']:,.2f}\n"
            f"  Middle: ${bb['middle']:,.2f}\n"
            f"  Lower: ${bb['lower']:,.2f}\n"
            f"  {self._t('signal')}: {bb['signal']}\n"
            f"• ATR: {self._format_atr(volatility['atr'])}\n"
            f"• {self._t('historical_volatility')}: {self._format_historical_volatility(volatility['historical_volatility'])}"
        )

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

    def _get_sentiment_emoji(self, sentiment: str) -> str:
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