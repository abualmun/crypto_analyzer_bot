from typing import Dict, List
import json
import os

class TelegramFormatter:
    def __init__(self):
        self.languages = {
            'en': self._load_language('en'),
            'ar': self._load_language('ar')
        }
        self.current_language = 'ar'

    def _load_language(self, lang_code: str) -> Dict:
        """Load language translations from JSON file"""
        try:
            file_path = os.path.join('src', 'languages', lang_code, 'messages.json')
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception:
            return {}

    def set_language(self, lang_code: str):
        """Set the current language for formatting"""
        if lang_code in self.languages:
            self.current_language = lang_code

    def _t(self, key: str) -> str:
        """Get translation for key"""
        return self.languages[self.current_language].get(key, key)

    def format_quick_analysis(self, analysis: Dict, coin_id: str) -> str:
        """Format quick analysis results"""
        if "error" in analysis:
            return f"⚠️ {self._t('error_analysis')}: {analysis['error']}"

        # Format price change with arrow
        price_change = analysis['price_change']
        change_arrow = "🔺" if price_change > 0 else "🔻"
        
        message = [
            f"📊 {self._t('quick_analysis')} - {coin_id.upper()}",
            "",
            f"💰 {self._t('current_price')}: ${analysis['current_price']:,.2f}",
            f"📈 {self._t('price_change')}: {change_arrow} {abs(price_change):.2f}%",
            f"📊 RSI: {analysis['rsi']:.2f}",
            f"〽️ {self._t('trend')}: {self._get_trend_emoji(analysis['trend'])} {analysis['trend']}"
        ]

        return "\n".join(message)

    def format_full_analysis(self, analysis: Dict, coin_id: str) -> str:
        """Format comprehensive analysis results"""
        if "error" in analysis:
            return f"⚠️ {self._t('error_analysis')}: {analysis['error']}"

        # Basic info formatting
        basic_info = analysis['basic_info']
        price_change = basic_info['price_change_24h']
        change_arrow = "🔺" if price_change > 0 else "🔻"

        # Create message sections
        sections = []

        # Header section
        header = [
            f"🔍 {self._t('detailed_analysis')} - {coin_id.upper()}",
            "═══════════════════",
            "",
            f"💰 {self._t('current_price')}: ${basic_info['current_price']:,.2f}",
            f"📈 24h {self._t('change')}: {change_arrow} {abs(price_change):.2f}%",
            f"📊 24h {self._t('volume')}: ${basic_info['volume_24h']:,.0f}",
            ""
        ]
        sections.append("\n".join(header))

        # Trend Analysis
        trend = analysis['trend_indicators']
        trend_section = [
            f"📈 {self._t('trend_analysis')}:",
            f"• {self._t('trend')}: {self._get_trend_emoji(trend['trend'])} {trend['trend']}",
            f"• MA20: ${trend['ma20']:,.2f}",
            f"• MA50: ${trend['ma50']:,.2f}",
            f"• MACD: {self._format_macd(trend['macd'])}",
            ""
        ]
        sections.append("\n".join(trend_section))

        # Momentum Analysis
        momentum = analysis['momentum_indicators']
        momentum_section = [
            f"📊 {self._t('momentum_analysis')}:",
            f"• RSI: {self._format_rsi(momentum['rsi'])}",
            f"• {self._t('stochastic')}: K({momentum['stochastic']['k']:.1f}) D({momentum['stochastic']['d']:.1f})",
            ""
        ]
        sections.append("\n".join(momentum_section))

        # Support/Resistance
        sr_levels = analysis['support_resistance']
        sr_section = [
            f"🎯 {self._t('support_resistance')}:",
            f"• {self._t('resistance')}: ${sr_levels['resistance_levels'][0]:,.2f}",
            f"• {self._t('support')}: ${sr_levels['support_levels'][-1]:,.2f}",
            ""
        ]
        sections.append("\n".join(sr_section))

        # Patterns
        patterns = analysis['patterns']['patterns']
        if patterns:
            pattern_section = [
                f"🔮 {self._t('patterns_detected')}:"
            ]
            for pattern in patterns:
                pattern_section.append(f"• {pattern.replace('_', ' ').title()}")
            pattern_section.append("")
            sections.append("\n".join(pattern_section))

        # Summary
        summary = analysis['summary']
        summary_section = [
            f"📝 {self._t('summary')}:",
            f"• {self._t('sentiment')}: {self._get_sentiment_emoji(summary['overall_sentiment'])} {summary['overall_sentiment']}",
            f"• {self._t('confidence')}: {summary['confidence']}%",
            "",
            f"🔍 {self._t('signals')}:"
        ]
        for signal in summary['signals']:
            emoji = self._get_sentiment_emoji(signal[0])
            summary_section.append(f"• {emoji} {signal[1]}")

        sections.append("\n".join(summary_section))

        # Combine all sections
        return "\n".join(sections)

    def _get_trend_emoji(self, trend: str) -> str:
        """Get appropriate emoji for trend"""
        return {
            'Bullish': '🟢',
            'Bearish': '🔴',
            'Neutral': '⚪'
        }.get(trend, '⚪')

    def _get_sentiment_emoji(self, sentiment: str) -> str:
        """Get appropriate emoji for sentiment"""
        return {
            'Bullish': '📈',
            'Bearish': '📉',
            'Neutral': '↔️'
        }.get(sentiment, '↔️')

    def _format_rsi(self, rsi: float) -> str:
        """Format RSI with interpretation"""
        if rsi > 70:
            return f"{rsi:.1f} 📈 ({self._t('overbought')})"
        elif rsi < 30:
            return f"{rsi:.1f} 📉 ({self._t('oversold')})"
        return f"{rsi:.1f} ↔️"

    def _format_macd(self, macd: Dict) -> str:
        """Format MACD values"""
        if macd['macd'] > macd['signal']:
            trend = "📈"
        else:
            trend = "📉"
        return f"{macd['macd']:.2f} {trend}"

    def format_error_message(self, error: str) -> str:
        """Format error messages"""
        return f"⚠️ {self._t('error')}: {error}"

    def format_loading_message(self) -> str:
        """Format loading message"""
        return f"⏳ {self._t('analyzing')}..."