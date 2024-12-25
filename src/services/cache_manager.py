from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from datetime import datetime, timedelta
import pandas as pd
import logging
from typing import Optional, Dict, List
from .models import Base, CryptoOHLCV, TimeInterval, CoinMetadata

class CacheManager:
    def __init__(self, database_url: str, cache_duration: Dict[str, int] = None):
        """
        Initialize the cache manager.
        
        Args:
            database_url: SQLAlchemy database URL
            cache_duration: Dict of cache durations in seconds for different intervals
                          e.g., {'1': 300, '7': 600, '30': 1800, '90': 3600}
        """
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Default cache durations for different intervals (in seconds)
        self.cache_duration = cache_duration or {
             1: 300,    # 5 minutes for 1-day data
             7: 600,    # 10 minutes for 7-day data
             30: 1800,  # 30 minutes for 30-day data
             90: 3600   # 1 hour for 90-day data
        }
        self.logger = logging.getLogger(__name__)

    def get_ohlcv_data(
        self, 
        coin_id: str, 
        vs_currency: str,
        interval: str,
        start_time: datetime,
        end_time: datetime
    ) -> Optional[pd.DataFrame]:
        """
        Get OHLCV data from cache if available and not expired.
        
        Args:
            coin_id: Cryptocurrency identifier
            vs_currency: Quote currency (e.g., 'usd')
            interval: Time interval ('1', '7', '30', '90')
            start_time: Start time for data range
            end_time: End time for data range
        """
        session = self.Session()
        try:
            # Get cache duration for this interval
            cache_duration = self.cache_duration.get(interval, 300)
            cache_threshold = datetime.utcnow() - timedelta(seconds=cache_duration)
            
            query = (
                select(CryptoOHLCV)
                .where(
                    CryptoOHLCV.coin_id == coin_id,
                    CryptoOHLCV.vs_currency == vs_currency,
                    CryptoOHLCV.interval == TimeInterval(interval),
                    CryptoOHLCV.timestamp.between(start_time, end_time),
                    CryptoOHLCV.last_updated > cache_threshold
                )
                .order_by(CryptoOHLCV.timestamp)
            )
            
            result = session.execute(query).fetchall()
            
            if result:
                # Convert to DataFrame
                df = pd.DataFrame([{
                    'timestamp': row.CryptoOHLCV.timestamp,
                    'open': row.CryptoOHLCV.open,
                    'high': row.CryptoOHLCV.high,
                    'low': row.CryptoOHLCV.low,
                    'close': row.CryptoOHLCV.close,
                    'volume': row.CryptoOHLCV.volume,
                    'market_cap': row.CryptoOHLCV.market_cap
                } for row in result])
                
                df.set_index('timestamp', inplace=True)
                return df
                
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching from cache: {str(e)}")
            return None
        finally:
            session.close()

    def update_ohlcv_data(
        self,
        coin_id: str,
        vs_currency: str,
        interval: str,
        df: pd.DataFrame
    ):
        """
        Update OHLCV data in the cache.
        
        Args:
            coin_id: Cryptocurrency identifier
            vs_currency: Quote currency (e.g., 'usd')
            interval: Time interval ('1', '7', '30', '90')
            df: DataFrame containing OHLCV data
        """
        session = self.Session()
        try:
            # Delete existing data for the same period and interval
            start_time = df.index.min()
            end_time = df.index.max()
            
            session.query(CryptoOHLCV).filter(
                CryptoOHLCV.coin_id == coin_id,
                CryptoOHLCV.vs_currency == vs_currency,
                CryptoOHLCV.interval == TimeInterval(interval),
                CryptoOHLCV.timestamp.between(start_time, end_time)
            ).delete()

            # Insert new data
            for timestamp, row in df.iterrows():
                entry = CryptoOHLCV(
                    coin_id=coin_id,
                    vs_currency=vs_currency,
                    interval=TimeInterval(interval),
                    timestamp=timestamp,
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    volume=row['volume'],
                    market_cap=row['market_cap'],
                    last_updated=datetime.utcnow()
                )
                session.add(entry)
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error updating cache: {str(e)}")
            raise
        finally:
            session.close()
    
    def update_coin_metadata(self, coin_data: Dict):
        """
        Update coin metadata in the cache.
        """
        session = self.Session()
        try:
            existing = session.query(CoinMetadata).filter_by(
                coin_id=coin_data['id']
            ).first()
            
            if existing:
                existing.symbol = coin_data.get('symbol')
                existing.name = coin_data.get('name')
                existing.extra_data = coin_data
                existing.last_updated = datetime.utcnow()
            else:
                entry = CoinMetadata(
                    coin_id=coin_data['id'],
                    symbol=coin_data.get('symbol'),
                    name=coin_data.get('name'),
                    extra_data=coin_data,
                    last_updated=datetime.utcnow()
                )
                session.add(entry)
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error updating coin metadata: {str(e)}")
            raise
        finally:
            session.close()

    def get_coin_metadata(self, coin_id: str) -> Optional[Dict]:
        """
        Get coin metadata from cache if available and not expired.
        """
        session = self.Session()
        try:
            cache_threshold = datetime.utcnow() - timedelta(seconds=self.cache_duration[30])
            
            result = session.query(CoinMetadata).filter(
                CoinMetadata.coin_id == coin_id,
                CoinMetadata.last_updated > cache_threshold
            ).first()
            
            if result:
                return {
                    'id': result.coin_id,
                    'symbol': result.symbol,
                    'name': result.name,
                    'extra_data': result.extra_data
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching coin metadata: {str(e)}")
            return None
        finally:
            session.close()

    def get_coin_id_by_symbol(self, symbol: str) -> Optional[str]:
        """
        Get coin ID from database using symbol.
        Returns None if symbol not found.
        """
        session = self.Session()
        try:
            result = session.query(CoinMetadata)\
                .filter(CoinMetadata.symbol.ilike(symbol))\
                .first()

            return result.coin_id if result else None

        except Exception as e:
            self.logger.error(f"Error searching symbol {symbol}: {str(e)}")
            return None
        finally:
            session.close()

    def update_coins_list(self, coins: List[Dict]):
        """Update all coins metadata in cache."""
        session = self.Session()
        try:
            for coin in coins:
                existing = session.query(CoinMetadata).filter_by(coin_id=coin['id']).first()
                
                if existing:
                    existing.symbol = coin.get('symbol')
                    existing.name = coin.get('name')
                    existing.extra_data = coin
                    existing.last_updated = datetime.utcnow()
                else:
                    entry = CoinMetadata(
                        coin_id=coin['id'],
                        symbol=coin.get('symbol'),
                        name=coin.get('name'),
                        extra_data=coin,
                        last_updated=datetime.utcnow()
                    )
                    session.add(entry)
            
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error updating coins list: {str(e)}")
            raise
        finally:
            session.close()

    def get_all_coins(self) -> List[Dict]:
        """Get all coins from cache."""
        session = self.Session()
        try:
            coins = session.query(CoinMetadata).all()
            return [{
                'id': coin.coin_id,
                'symbol': coin.symbol,
                'name': coin.name,
                **coin.extra_data
            } for coin in coins]
        finally:
            session.close()