# src/data/market_data.py

import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from src.data.crypto_data import CryptoDataClient

class MarketDataProcessor:
    def __init__(self, crypto_client: CryptoDataClient):
        self.crypto_client = crypto_client

    async def get_ohlcv_data(self, 
                            coin_id: str, 
                            days: str = '30',
                            interval: str = 'daily') -> Optional[pd.DataFrame]:
        """Get OHLCV data in pandas DataFrame format."""
        try:
            history = await self.crypto_client.get_coin_history(coin_id, days)
            if not history:
                return None

            # Extract price and volume data
            prices = history.get('prices', [])
            volumes = history.get('total_volumes', [])

            # Create DataFrame
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['volume'] = pd.DataFrame(volumes, columns=['timestamp', 'volume'])['volume']
            
            # Process timestamp
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            # Resample to get OHLCV
            ohlcv = df.resample('D').agg({
                'price': ['first', 'high', 'low', 'last'],
                'volume': 'sum'
            })

            # Clean up column names
            ohlcv.columns = ['open', 'high', 'low', 'close', 'volume']
            return ohlcv

        except Exception as e:
            logging.error(f"Error processing OHLCV data for {coin_id}: {e}")
            return None

    async def get_market_summary(self, coin_id: str) -> Optional[Dict]:
        """Get market summary including price changes and volume."""
        try:
            info = await self.crypto_client.get_coin_info(coin_id)
            if not info or 'market_data' not in info:
                return None

            market_data = info['market_data']
            return {
                'current_price': market_data.get('current_price', {}).get('usd'),
                'price_change_24h': market_data.get('price_change_percentage_24h'),
                'volume_24h': market_data.get('total_volume', {}).get('usd'),
                'market_cap': market_data.get('market_cap', {}).get('usd'),
                'high_24h': market_data.get('high_24h', {}).get('usd'),
                'low_24h': market_data.get('low_24h', {}).get('usd')
            }

        except Exception as e:
            logging.error(f"Error getting market summary for {coin_id}: {e}")
            return None