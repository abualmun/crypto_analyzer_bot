from src.utils.formatters import TelegramFormatter
from src.analysis.technical import TechnicalAnalyzer

# Initialize
formatter = TelegramFormatter()
analyzer = TechnicalAnalyzer()

# Test English format
analysis = analyzer.analyze_coin('bitcoin')
message = formatter.format_full_analysis(analysis, 'bitcoin')
print(message)

# Test Arabic format
formatter.set_language('ar')
message = formatter.format_full_analysis(analysis, 'bitcoin')
print(message)