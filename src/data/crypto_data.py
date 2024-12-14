# src/data/crypto_data.py

from pycoingecko import CoinGeckoAPI
from typing import Dict, List, Optional, Union
import time
import logging
from functools import lru_cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
class CryptoDataClient:
    def __init__(self):
        
        self.cg = CoinGeckoAPI()
        self.logger = logging.getLogger(__name__)
        
    @lru_cache(maxsize=100)
    def get_coin_list(self) -> List[Dict]:
        """Get list of all supported coins."""
        try:
            return self.cg.get_coins_list()
        except Exception as e:
            self.logger.error(f"Error fetching coin list: {e}")
            return []

    async def get_coin_price(self, coin_id: str, vs_currency: str = 'usd') -> Optional[float]:
        """Get current price of a coin."""
        try:
            result = self.cg.get_price(ids=coin_id, vs_currencies=vs_currency)
            return result.get(coin_id, {}).get(vs_currency)
        except Exception as e:
            self.logger.error(f"Error fetching price for {coin_id}: {e}")
            return None

    async def get_coin_history(self, 
                             coin_id: str, 
                             days: str,
                             vs_currency: str = 'usd') -> Optional[Dict]:
        """Get historical market data."""
        try:
            return self.cg.get_coin_market_chart_by_id(
                id=coin_id,
                vs_currency=vs_currency,
                days=days
            )
        except Exception as e:
            self.logger.error(f"Error fetching history for {coin_id}: {e}")
            return None

    async def get_coin_info(self, coin_id: str) -> Optional[Dict]:
        """Get detailed information about a coin."""
        try:
            return self.cg.get_coin_by_id(
                id=coin_id,
                localization=False,
                tickers=False,
                market_data=True,
                community_data=False,
                developer_data=False
            )
        except Exception as e:
            self.logger.error(f"Error fetching coin info for {coin_id}: {e}")
            return None

    async def search_coin(self, query: str) -> List[Dict]:
        """Search for coins by name or symbol."""
        try:
            coin_list = self.get_coin_list()
            return [
                coin for coin in coin_list
                if query.lower() in coin['id'].lower() 
                or query.lower() in coin['symbol'].lower()
            ][:10]  # Return top 10 matches
        except Exception as e:
            self.logger.error(f"Error searching for {query}: {e}")
            return []


