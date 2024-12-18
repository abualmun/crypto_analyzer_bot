from typing import Dict
import pandas as pd

class NewsFormatter:
    def format_news(self, df: pd.DataFrame, coin_symbol: str) -> str:
        """Format news data into a readable message with emojis"""
        try:
            # Get statistics
            stats = self._get_news_stats(df)
            
            # Get recent articles (top 5)
            recent_articles = df.nlargest(5, 'published_on')
            
            # Build message
            message_parts = [
                f"📰 News Summary for {coin_symbol}",
                "═" * 32,
                "",
                "📊 Statistics:",
                f"• Total Articles: {stats['total_articles']}",
                f"• Sources: {stats['unique_sources']}",
                f"• Most Active Source: {stats['most_common_source']}",
                f"• Overall Sentiment: {self._get_sentiment_emoji(stats['sentiment_distribution'])}",
                "",
                "🕒 Latest Articles:",
            ]
            
            # Add recent articles
            for _, article in recent_articles.iterrows():
                pub_date = article['published_on'].strftime('%Y-%m-%d %H:%M')
                message_parts.extend([
                    f"• 📌 {article['title']}",
                    f"  🔗 {article['url']}",
                    f"  📅 {pub_date}",
                    f"  {self._get_sentiment_emoji(article['sentiment'])} {article['sentiment']}",
                    ""
                ])
            
            # Add trending categories if available
            if stats['top_categories']:
                message_parts.extend([
                    "🏷️ Top Categories:",
                    *[f"• {cat}: {count}" for cat, count in stats['top_categories'].items()],
                    ""
                ])
            
            return "\n".join(message_parts)
            
        except Exception as e:
            return f"Error formatting news: {str(e)}"
    
    def _get_news_stats(self, df: pd.DataFrame) -> Dict:
        """Get basic statistics about the news articles"""
        stats = {
            'total_articles': len(df),
            'unique_sources': df['source_name'].nunique(),
            'most_common_source': df['source_name'].mode().iloc[0] if not df['source_name'].empty else "N/A",
            'sentiment_distribution': df['sentiment'].mode().iloc[0] if not df['sentiment'].empty else "NEUTRAL",
            'top_categories': pd.Series([
                cat for cats in df['categories'].dropna() 
                for cat in cats.split('|')
            ]).value_counts().head(3).to_dict()
        }
        return stats
    
    def _get_sentiment_emoji(self, sentiment: str) -> str:
        """Convert sentiment to emoji"""
        sentiment_map = {
            'POSITIVE': '📈 POSITIVE',
            'VERY POSITIVE': '🚀 VERY POSITIVE',
            'NEUTRAL': '➖ NEUTRAL',
            'NEGATIVE': '📉 NEGATIVE',
            'VERY NEGATIVE': '💥 VERY NEGATIVE'
        }
        return sentiment_map.get(sentiment.upper(), '❓')
    
    def format_loading_message(self) -> str:
        """Format loading message"""
        return "🔍 Fetching latest crypto news..."
    
    def format_error_message(self, error: str) -> str:
        """Format error message"""
        return f"❌ Error fetching news: {error}"