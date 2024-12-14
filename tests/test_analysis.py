from src.analysis.technical import TechnicalAnalyzer

analyzer = TechnicalAnalyzer()

# Get quick analysis
quick = analyzer.get_quick_analysis('bitcoin')
print("Quick Analysis:", quick)

# Get full analysis
analysis = analyzer.analyze_coin('bitcoin')
print("\nFull Analysis Summary:", analysis['summary'])