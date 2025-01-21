import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional, Tuple
import logging

from ..services.coingecko_api import CoinGeckoAPI
from ..services.cache_manager import CacheManager

class DataProcessor:
    def __init__(self):
        self.api = CoinGeckoAPI()
        # self.cache_manager = CacheManager("sqlite:///crypto_cache.db")
        self.cache_manager = CacheManager()
        self.logger = logging.getLogger(__name__)


    def get_ohlcv_data(
        self, 
        coin_id: str, 
        vs_currency: str = 'usd',
        days: int = 30,
        interval: Optional[str] = 'daily'
    ) -> Optional[pd.DataFrame]:
        """
        Fetch and process OHLCV (Open, High, Low, Close, Volume) data.
        
        Args:
            coin_id: The coin identifier (e.g., 'bitcoin')
            vs_currency: The target currency (default: 'usd')
            days: Number of days of data to fetch (default: 30)
            interval: Data interval (default: 'daily')
            
        Returns:
            pandas.DataFrame with OHLCV data or None if error occurs
        """
        
        # coin_id = self.cache_manager.get_coin_id_by_symbol(coin_id)
        if coin_id is None:
            self.logger.error(f"Coin ID not found for symbol: {coin_id}")
            return None
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        # Try to get data from cache
        cached_data = self.cache_manager.get_ohlcv_data(
            coin_id=coin_id,
            vs_currency=vs_currency,
            interval=days,
            start_time=start_time,
            end_time=end_time
        )
        
        if cached_data is not None:
            return cached_data

        try:
            # Get market chart data
            market_data = self.api.get_coin_market_chart(
                id=coin_id,
                vs_currency=vs_currency,
                days=days,
                interval=interval
            )

            # Get OHLC data
            ohlc_data = self.api.get_coin_ohlc(
                id=coin_id,
                vs_currency=vs_currency,
                days=days
            )

            # Process and combine the data
            df = self._process_market_data(market_data, ohlc_data)
            
            # Update cache
            self.cache_manager.update_ohlcv_data(
                coin_id=coin_id,
                vs_currency=vs_currency,
                interval=days,
                df=df
            )
            
            return df

        except Exception as e:
            self.logger.error(f"Error fetching data for {coin_id}: {str(e)}")
            return None

    def _process_market_data(self, market_data: Dict, ohlc_data: List) -> pd.DataFrame:
        """
        Process raw market data into a pandas DataFrame suitable for technical analysis.
        """
        # Convert OHLC data
        ohlc_df = pd.DataFrame(ohlc_data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        ohlc_df['timestamp'] = pd.to_datetime(ohlc_df['timestamp'], unit='ms')
        ohlc_df.set_index('timestamp', inplace=True)

        # Process market data
        prices = pd.DataFrame(market_data['prices'], columns=['timestamp', 'price'])
        volumes = pd.DataFrame(market_data['total_volumes'], columns=['timestamp', 'volume'])
        market_caps = pd.DataFrame(market_data['market_caps'], columns=['timestamp', 'market_cap'])

        # Convert timestamps
        prices['timestamp'] = pd.to_datetime(prices['timestamp'], unit='ms')
        volumes['timestamp'] = pd.to_datetime(volumes['timestamp'], unit='ms')
        market_caps['timestamp'] = pd.to_datetime(market_caps['timestamp'], unit='ms')

        # Merge all data
        df = prices.merge(volumes, on='timestamp', how='outer')
        df = df.merge(market_caps, on='timestamp', how='outer')
        df.set_index('timestamp', inplace=True)

        # Combine with OHLC data
        final_df = pd.concat([ohlc_df, df[['volume', 'market_cap']]], axis=1)
        
        # Sort by timestamp and remove duplicates
        final_df.sort_index(inplace=True)
        final_df = final_df[~final_df.index.duplicated(keep='first')]

        # Fill any missing values
        final_df.fillna(method='ffill', inplace=True)
        
        return final_df

    def get_multiple_coins_data(
        self, 
        coin_ids: List[str], 
        vs_currency: str = 'usd',
        days: int = 30
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple coins with rate limiting.
        """
        results = {}
        for coin_id in coin_ids:
            
            results[coin_id] = self.get_ohlcv_data(coin_id, vs_currency, days)
            time.sleep(1)  # Rate limiting
        return results

    def get_latest_price(self, coin_id: str, vs_currency: str = 'usd') -> Optional[float]:
        """
        Get the latest price for a coin.
        """
        try:
            # coin_id = self.cache_manager.get_coin_id_by_symbol(coin_id)
            if coin_id is None:
                self.logger.error(f"Coin ID not found for symbol: {coin_id}")
                return None
            price_data = self.api.get_simple_price(
                ids=coin_id,
                vs_currencies=vs_currency
            )
            return price_data[coin_id][vs_currency]
        except Exception as e:
            self.logger.error(f"Error fetching price for {coin_id}: {str(e)}")
            return None


    def validate_coin_id(self, coin_id: str) -> bool:
        """
        Validate if a coin ID exists, checking cache first.
        """
        # Check cache first
        coins = self.get_available_coins()
        cached_metadata = self.cache_manager.get_coin_metadata(coin_id)
        if cached_metadata is not None:
            return True

        # If not in cache, check API
        try:
            search_result = self.api.search(coin_id)
            coins = search_result.get('coins', [])
            
            # If found, update cache
            for coin in coins:
                if coin['id'].lower() == coin_id.lower():
                    self.cache_manager.update_coin_metadata(coin)
                    return True
            for coin in coins:
                if coin['symbol'].lower() == coin_id.lower():
                    self.cache_manager.update_coin_metadata(coin)
                    return True
            return False
            
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            return False

    def get_available_coins(self) -> List[Dict]:
        """Get list of available coins, updating cache if needed."""
        try:
            cached_coins = self.cache_manager.get_all_coins()
            if cached_coins:
                return cached_coins

            coins = self.api.get_coins_list()
            if coins:
                self.cache_manager.update_coins_list(coins)
            return coins

        except Exception as e:
            self.logger.error(f"Error fetching coin list: {str(e)}")
            return []