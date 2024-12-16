import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bot.handlers.analysis_handlers import AnalysisHandler
from telegram import Update, Message, Chat, User
from unittest.mock import Mock, AsyncMock

class HandlerTester:
    def __init__(self):
        self.handler = AnalysisHandler()
        
    async def setup_mock_update(self, command: str, args: list = None):
        """Setup mock update object"""
        message = Mock(spec=Message)
        message.reply_text = AsyncMock()
        message.reply_photo = AsyncMock()
        message.edit_text = AsyncMock()
        message.delete = AsyncMock()
        message.reply_document = AsyncMock()
        update = Mock(spec=Update)
        update.message = message
        update.effective_chat = Mock(spec=Chat)
        update.effective_user = Mock(spec=User)
        
        context = Mock()
        context.args = args or []
        
        return update, context

    async def test_analyze_command(self):
        """Test the analyze command with different scenarios"""
        print("\n🧪 Testing /analyze command:")
        
        # Test cases
        test_cases = [
            ("bitcoin", None),  # Default timeframe
            ("bitcoin", "1d"),  # Daily timeframe
            ("bitcoin", "1w"),  # Weekly timeframe
            ("invalid_coin", None),  # Invalid coin
            ("bitcoin", "invalid_timeframe"),  # Invalid timeframe
        ]
        
        for coin, timeframe in test_cases:
            print(f"\nTesting analyze with coin: {coin}, timeframe: {timeframe}")
            args = [coin] if timeframe is None else [coin, timeframe]
            update, context = await self.setup_mock_update("analyze", args)
            
            try:
                await self.handler.cmd_analyze(update, context)
                print(f"✅ Analysis completed for {coin}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")

    async def test_quick_command(self):
        """Test the quick analysis command"""
        print("\n🧪 Testing /quick command:")
        
        test_cases = [
            "bitcoin",
            "ethereum",
            "invalid_coin"
        ]
        
        for coin in test_cases:
            print(f"\nTesting quick analysis for: {coin}")
            update, context = await self.setup_mock_update("quick", [coin])
            
            try:
                await self.handler.cmd_quick(update, context)
                print(f"✅ Quick analysis completed for {coin}")
            except Exception as e:
                print(f"❌ Error: {str(e)}")

    async def test_chart_command(self):
        """Test the chart command with different types"""
        print("\n🧪 Testing /chart command:")
        
        test_cases = [
            ("bitcoin", "price", "1d"),
            ("bitcoin", "ma", "1w"),
            ("bitcoin", "macd", "1d"),
            ("bitcoin", "rsi", "1d"),
            ("bitcoin", "volume", "1d"),
            ("bitcoin", "invalid_type", "1d"),
            ("invalid_coin", "price", "1d"),
        ]
        
        for coin, chart_type, timeframe in test_cases:
            print(f"\nTesting chart for: {coin}, type: {chart_type}, timeframe: {timeframe}")
            update, context = await self.setup_mock_update("chart", [coin, chart_type, timeframe])
            
            try:
                await self.handler.cmd_chart(update, context)
                print(f"✅ Chart generated for {coin} ({chart_type})")
            except Exception as e:
                print(f"❌ Error: {str(e)}")

    async def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🧪 Testing error handling:")
        
        # Test no arguments
        print("\nTesting commands with no arguments:")
        for command in ["analyze", "quick", "chart"]:
            update, context = await self.setup_mock_update(command, [])
            try:
                if command == "analyze":
                    await self.handler.cmd_analyze(update, context)
                elif command == "quick":
                    await self.handler.cmd_quick(update, context)
                elif command == "chart":
                    await self.handler.cmd_chart(update, context)
                print(f"✅ Error handling worked for {command} with no args")
            except Exception as e:
                print(f"❌ Error in {command}: {str(e)}")

    async def run_all_tests(self):
        """Run all handler tests"""
        print("🚀 Starting Handler Tests\n" + "="*50)
        
        await self.test_analyze_command()
        await self.test_quick_command()
        await self.test_chart_command()
        await self.test_error_handling()
        
        print("\n✨ Tests completed!")

def main():
    """Run the tests"""
    tester = HandlerTester()
    asyncio.run(tester.run_all_tests())

if __name__ == "__main__":
    main()