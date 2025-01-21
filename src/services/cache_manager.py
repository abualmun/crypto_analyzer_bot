from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from datetime import datetime, timedelta
import pandas as pd
import logging
from typing import Optional, Dict, List
from .database import Base, OHLC, TimeInterval, Coin
import os

class CacheManager:
    def __init__(self, database_url: str = None, cache_duration: Dict[str, int] = None):
        """Initialize the cache manager."""
        if database_url is None:
            database_url = self._construct_database_url()   
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        self.cache_duration = cache_duration or {
             1: 300,    # 5 minutes for 1-day data
             7: 600,    # 10 minutes for 7-day data
             30: 1800,  # 30 minutes for 30-day data
             90: 3600   # 1 hour for 90-day data
        }
        self.logger = logging.getLogger(__name__)

    def _construct_database_url(self) -> str:
        """Construct PostgreSQL database URL from environment variables."""
        # This method remains unchanged
        return f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', '')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'crypto_analytics')}"

    def get_ohlcv_data(
        self, 
        coin_id: str, 
        vs_currency: str,
        interval: str,
        start_time: datetime,
        end_time: datetime
    ) -> Optional[pd.DataFrame]:
        """Get OHLCV data from cache if available and not expired."""
        session = self.Session()
        try:
            cache_duration = self.cache_duration.get(interval, 300)
            cache_threshold = datetime.utcnow() - timedelta(seconds=cache_duration)
            
            query = (
                select(OHLC)  # Changed from CryptoOHLCV to OHLC
                .where(
                    OHLC.coin_id == coin_id,
                    OHLC.vs_currency == vs_currency,
                    OHLC.interval == TimeInterval(interval),
                    OHLC.timestamp.between(start_time, end_time),
                    OHLC.last_updated > cache_threshold
                )
                .order_by(OHLC.timestamp)
            )
            
            result = session.execute(query).fetchall()
            
            if result:
                df = pd.DataFrame([{
                    'timestamp': row.OHLC.timestamp,
                    'open': row.OHLC.open,
                    'high': row.OHLC.high,
                    'low': row.OHLC.low,
                    'close': row.OHLC.close,
                    'volume': row.OHLC.volume,
                    'market_cap': row.OHLC.market_cap
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
        """Update OHLCV data in the cache."""
        session = self.Session()
        try:
            start_time = df.index.min()
            end_time = df.index.max()
            
            # First, ensure the coin exists
            coin = session.query(Coin).filter(Coin.id == coin_id).first()
            if not coin:
                self.logger.error(f"Coin {coin_id} not found in database")
                raise ValueError(f"Coin {coin_id} not found in database")

            # Delete existing data
            session.query(OHLC).filter(
                OHLC.coin_id == coin_id,
                OHLC.vs_currency == vs_currency,
                OHLC.interval == TimeInterval(interval),
                OHLC.timestamp.between(start_time, end_time)
            ).delete()

            # Insert new data
            for timestamp, row in df.iterrows():
                entry = OHLC(
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
        """Update coin metadata in the cache."""
        session = self.Session()
        try:
            existing = session.query(Coin).filter_by(id=coin_data['id']).first()
            
            if existing:
                existing.symbol = coin_data.get('symbol')
                existing.name = coin_data.get('name')
                existing.platforms = coin_data.get('platforms', {})
                existing.extra_data = coin_data
                existing.last_updated = datetime.utcnow()
            else:
                entry = Coin(
                    id=coin_data['id'],
                    symbol=coin_data.get('symbol'),
                    name=coin_data.get('name'),
                    platforms=coin_data.get('platforms', {}),
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
        """Get coin metadata from cache if available and not expired."""
        session = self.Session()
        try:
            cache_threshold = datetime.utcnow() - timedelta(seconds=self.cache_duration[30])
            
            result = session.query(Coin).filter(
                Coin.id == coin_id,
                Coin.last_updated > cache_threshold
            ).first()
            
            if result:
                return {
                    'id': result.id,
                    'symbol': result.symbol,
                    'name': result.name,
                    'platforms': result.platforms,
                    'extra_data': result.extra_data
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching coin metadata: {str(e)}")
            return None
        finally:
            session.close()

    def get_coin_id_by_symbol(self, symbol: str) -> Optional[str]:
        """Get coin ID from database using symbol."""
        session = self.Session()
        try:
            result = session.query(Coin)\
                .filter(Coin.symbol.ilike(symbol))\
                .first()

            return result.id if result else None

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
                existing = session.query(Coin).filter_by(id=coin['id']).first()
                
                if existing:
                    existing.symbol = coin.get('symbol')
                    existing.name = coin.get('name')
                    existing.platforms = coin.get('platforms', {})
                    existing.extra_data = coin
                    existing.last_updated = datetime.utcnow()
                else:
                    entry = Coin(
                        id=coin['id'],
                        symbol=coin.get('symbol'),
                        name=coin.get('name'),
                        platforms=coin.get('platforms', {}),
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
            coins = session.query(Coin).all()
            return [{
                'id': coin.id,
                'symbol': coin.symbol,
                'name': coin.name,
                'platforms': coin.platforms,
                **coin.extra_data
            } for coin in coins]
        finally:
            session.close()