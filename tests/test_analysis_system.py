import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analysis.technical import TechnicalAnalyzer
from src.utils.formatters import TelegramFormatter
from src.data.processor import DataProcessor

class AnalysisSystemTester:
    def __init__(self):
        self.analyzer = TechnicalAnalyzer()
        self.formatter = TelegramFormatter()
        self.data_processor = DataProcessor()
        self.test_coins = ['bitcoin', 'ethereum']  # Test with major coins first
        
    def run_all_tests(self):
        """Run all system tests"""
        print("\n🧪 Starting Analysis System Tests\n" + "="*50)
        
        self.test_data_fetching()
        self.test_technical_indicators()
        self.test_formatting()
        self.test_error_handling()
        self.test_performance()
        self.test_analysis_structure()
        self.test_formatted_output()

    def test_data_fetching(self):
        """Test data fetching functionality"""
        print("\n📊 Testing Data Fetching:")
        
        for coin in self.test_coins:
            print(f"\nTesting {coin}:")
            try:
                df = self.data_processor.get_ohlcv_data(coin)
                if df is not None and not df.empty:
                    print(f"✅ Data fetched successfully")
                    print(f"  - Rows: {len(df)}")
                    print(f"  - Columns: {df.columns.tolist()}")
                else:
                    print(f"❌ No data received")
            except Exception as e:
                print(f"❌ Error fetching data: {str(e)}")

    def test_technical_indicators(self):
        """Test technical indicator calculations"""
        print("\n📈 Testing Technical Indicators:")
        
        for coin in self.test_coins:
            print(f"\nAnalyzing {coin}:")
            try:
                analysis = self.analyzer.analyze_coin(coin)
                
                # Test momentum indicators
                self._validate_momentum(analysis)
                
                # Test trend indicators
                self._validate_trend(analysis)
                
                # Test volume indicators
                self._validate_volume(analysis)
                
                # Test volatility indicators
                self._validate_volatility(analysis)
                
            except Exception as e:
                print(f"❌ Error in analysis: {str(e)}")

    def _validate_momentum(self, analysis):
        """Validate momentum indicators"""
        momentum = analysis.get('momentum_indicators', {})
        print("\nMomentum Indicators:")
        
        # Check RSI
        if 'rsi' in momentum:
            rsi = momentum['rsi'].get('value', 0)
            print(f"  ✓ RSI: {rsi:.2f} {'(Valid)' if 0 <= rsi <= 100 else '(Invalid)'}")
        
        # Check other momentum indicators
        for indicator in ['stochastic', 'williams_r', 'mfi', 'cci']:
            if indicator in momentum:
                print(f"  ✓ {indicator.upper()}: Present and calculated")

    def _validate_trend(self, analysis):
        """Validate trend indicators"""
        trend = analysis.get('trend_indicators', {})
        print("\nTrend Indicators:")
        
        # Check Moving Averages
        if 'moving_averages' in trend:
            ma = trend['moving_averages']
            print(f"  ✓ Moving Averages: All present")
            print(f"    - MA20: {ma.get('ma20', 'Missing')}")
            print(f"    - MA50: {ma.get('ma50', 'Missing')}")
            print(f"    - MA200: {ma.get('ma200', 'Missing')}")

        # Check MACD
        if 'macd' in trend:
            print(f"  ✓ MACD: Present and calculated")

    def _validate_volume(self, analysis):
        """Validate volume indicators"""
        volume = analysis.get('volume_indicators', {})
        print("\nVolume Indicators:")
        
        for indicator in ['obv', 'volume_sma', 'vwap', 'accumulation_distribution']:
            if indicator in volume:
                print(f"  ✓ {indicator.upper()}: Present and calculated")

    def _validate_volatility(self, analysis):
        """Validate volatility indicators"""
        volatility = analysis.get('volatility_indicators', {})
        print("\nVolatility Indicators:")
        
        if 'bollinger_bands' in volatility:
            bb = volatility['bollinger_bands']
            print(f"  ✓ Bollinger Bands: All components present")
            print(f"    - Upper: {bb.get('upper', 'Missing')}")
            print(f"    - Middle: {bb.get('middle', 'Missing')}")
            print(f"    - Lower: {bb.get('lower', 'Missing')}")

    def test_formatting(self):
        """Test message formatting"""
        print("\n📝 Testing Formatting:")
        
        for coin in self.test_coins:
            print(f"\nTesting formatting for {coin}:")
            try:
                # Test English formatting
                self.formatter.set_language('en')
                analysis = self.analyzer.analyze_coin(coin)
                formatted_en = self.formatter.format_full_analysis(analysis, coin)
                print("✅ English formatting successful")
                
                # Test Arabic formatting
                self.formatter.set_language('ar')
                formatted_ar = self.formatter.format_full_analysis(analysis, coin)
                print("✅ Arabic formatting successful")
                
                # Validate formatting length
                print(f"  - English message length: {len(formatted_en)} chars")
                print(f"  - Arabic message length: {len(formatted_ar)} chars")
                
            except Exception as e:
                print(f"❌ Formatting error: {str(e)}")

    def test_error_handling(self):
        """Test error handling"""
        print("\n⚠️ Testing Error Handling:")
        
        # Test invalid coin
        print("\nTesting invalid coin:")
        try:
            analysis = self.analyzer.analyze_coin('invalid_coin_name')
            print("  ✓ Invalid coin handled correctly")
        except Exception as e:
            print(f"❌ Error handling failed: {str(e)}")
        
        # Test network error handling
        # Add more error scenarios...
        
    # Add this to your test script
    def test_analysis_structure(self):
        """Test full analysis structure"""
        print("\nTesting Full Analysis Structure:")
        
        for coin in self.test_coins:
            print(f"\nAnalyzing {coin} full structure:")
            try:
                analysis = self.analyzer.analyze_coin(coin)
                print("\nAnalysis Keys:", analysis.keys())
                for key in analysis.keys():
                    print(f"\n{key} type:", type(analysis[key]))
            except Exception as e:
                print(f"❌ Error analyzing structure: {str(e)}")

    def test_performance(self):
        """Test performance metrics"""
        print("\n⚡ Testing Performance:")
        
        import time
        
        for coin in self.test_coins:
            print(f"\nTesting performance for {coin}:")
            
            # Test analysis speed
            start_time = time.time()
            self.analyzer.analyze_coin(coin)
            analysis_time = time.time() - start_time
            
            print(f"  - Analysis time: {analysis_time:.2f} seconds")
            
            if analysis_time > 5:
                print("⚠️ Warning: Analysis taking longer than expected")
            else:
                print("✅ Performance within acceptable range")
                
    def test_formatted_output(self):
        """Test actual formatted output"""
        print("\nTesting Formatted Output:")
        
        for coin in self.test_coins:
            print(f"\n{'-'*50}")
            print(f"Formatted output for {coin}:")
            try:
                analysis = self.analyzer.analyze_coin(coin)
                formatted = self.formatter.format_full_analysis(analysis, coin)
                print(formatted)
            except Exception as e:
                print(f"Error formatting {coin}: {str(e)}")

if __name__ == "__main__":
    tester = AnalysisSystemTester()
    tester.run_all_tests()