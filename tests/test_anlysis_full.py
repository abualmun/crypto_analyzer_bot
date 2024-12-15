from src.analysis.technical import TechnicalAnalyzer

analyzer = TechnicalAnalyzer()
analysis = analyzer.analyze_coin('bitcoin')

# Check each component
print("\nTrend Analysis:", analysis['trend_indicators'])
print("\nMomentum Analysis:", analysis['momentum_indicators'])
print("\nVolume Analysis:", analysis['volume_indicators'])
print("\nSummary:", analysis['summary'])