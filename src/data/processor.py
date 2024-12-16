import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional, Tuple
import logging

from ..services.coingecko_api import CoinGeckoAPI

class DataProcessor:
    def __init__(self):
        self.api = CoinGeckoAPI()
        self._cache = {}  # Simple memory cache
        self.cache_duration = 300  # Cache duration in seconds (5 minutes)
        self.logger = logging.getLogger(__name__)

    # Common symbol to id mappings
    symbol_mapping = {
        'btc': 'bitcoin',
        'eth': 'ethereum',
        'usdt': 'tether',
        'bnb': 'binance-coin',
        'xrp': 'ripple',
        # Add more common mappings
    }




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
        cache_key = f"{coin_id}_{vs_currency}_{days}_{interval}"
        
        # Check cache first
        cached_data = self._get_from_cache(cache_key)
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
            
            # Cache the processed data
            self._cache_data(cache_key, df)
            
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
        print(final_df)
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

    def _get_from_cache(self, key: str) -> Optional[pd.DataFrame]:
        """
        Retrieve data from cache if still valid.
        """
        if key in self._cache:
            timestamp, data = self._cache[key]
            if time.time() - timestamp < self.cache_duration:
                return data
            else:
                del self._cache[key]
        return None

    def _cache_data(self, key: str, data: pd.DataFrame):
        """
        Cache data with current timestamp.
        """
        self._cache[key] = (time.time(), data)

    def get_latest_price(self, coin_id: str, vs_currency: str = 'usd') -> Optional[float]:
        """
        Get the latest price for a coin.
        """
        try:
            price_data = self.api.get_simple_price(
                ids=coin_id,
                vs_currencies=vs_currency
            )
            return price_data[coin_id][vs_currency]
        except Exception as e:
            self.logger.error(f"Error fetching price for {coin_id}: {str(e)}")
            return None

    # src/data/processor.py

    def validate_coin_id(self, coin_id: str) -> bool:
        """
        Validate if a coin ID exists in CoinGecko.
        Add common symbol mappings for better UX.
        """
        # Common symbol to id mappings
        

        # Convert common symbols to their IDs
        coin_id = DataProcessor.symbol_mapping.get(coin_id.lower(), coin_id.lower())

        try:
            search_result = self.api.search(coin_id)
            coins = search_result.get('coins', [])
            return any(coin['id'] == coin_id for coin in coins)
        except Exception as e:
            print(f"Validation error: {str(e)}")
            return False

    def get_available_coins(self) -> List[Dict]:
        """
        Get list of available coins with basic info.
        """
        try:
            return self.api.get_coins_list()
        except Exception as e:
            self.logger.error(f"Error fetching coin list: {str(e)}")
            return []