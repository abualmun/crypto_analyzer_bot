from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union, Tuple
from sqlalchemy import create_engine, and_, desc
from sqlalchemy.orm import sessionmaker, Session, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import DetachedInstanceError
from contextlib import contextmanager
import logging

from database import Base, Coin, CoinPrice, OHLC, TrendingCoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, database_url: str = 'sqlite:///crypto_analytics.db'):
        """Initialize database connection and session maker."""
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionMaker = sessionmaker(bind=self.engine)

    @contextmanager
    def session_scope(self) -> Session:
        """Context manager for database sessions with automatic commit/rollback."""
        session = self.SessionMaker()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()

    def update_coin(self, coin_data: Dict) -> Optional[Coin]:
        """Add or update a coin in the database."""
        try:
            with self.session_scope() as session:
                coin = session.query(Coin).filter_by(id=coin_data['id']).first()
                if coin:
                    # Update existing coin
                    for key, value in coin_data.items():
                        setattr(coin, key, value)
                else:
                    # Create new coin
                    coin = Coin(**coin_data)
                    session.add(coin)
                session.flush()
                return coin
        except SQLAlchemyError as e:
            logger.error(f"Error updating coin {coin_data.get('id')}: {str(e)}")
            return None

    def bulk_update_coins(self, coins_data: List[Dict]) -> int:
        """Bulk update or insert coins."""
        success_count = 0
        try:
            with self.session_scope() as session:
                for coin_data in coins_data:
                    try:
                        coin = session.query(Coin).filter_by(id=coin_data['id']).first()
                        if coin:
                            for key, value in coin_data.items():
                                setattr(coin, key, value)
                        else:
                            coin = Coin(**coin_data)
                            session.add(coin)
                        success_count += 1
                    except SQLAlchemyError as e:
                        logger.error(f"Error processing coin {coin_data.get('id')}: {str(e)}")
                        continue
                session.flush()
        except SQLAlchemyError as e:
            logger.error(f"Bulk update error: {str(e)}")
        return success_count

    def update_coin_price(self, price_data: Dict) -> Optional[CoinPrice]:
        """Add or update a coin price entry."""
        try:
            with self.session_scope() as session:
                price = session.query(CoinPrice).filter_by(
                    coin_id=price_data['coin_id'],
                    currency=price_data['currency']
                ).first()
                
                if price:
                    for key, value in price_data.items():
                        setattr(price, key, value)
                else:
                    price = CoinPrice(**price_data)
                    session.add(price)
                session.flush()
                return price
        except SQLAlchemyError as e:
            logger.error(f"Error updating price for coin {price_data.get('coin_id')}: {str(e)}")
            return None

    def bulk_update_ohlc(self, ohlc_data_list: List[Dict]) -> int:
        """Bulk update or insert OHLC data."""
        success_count = 0
        try:
            with self.session_scope() as session:
                for ohlc_data in ohlc_data_list:
                    try:
                        ohlc = session.query(OHLC).filter_by(
                            coin_id=ohlc_data['coin_id'],
                            timestamp=ohlc_data['timestamp']
                        ).first()
                        
                        if ohlc:
                            for key, value in ohlc_data.items():
                                setattr(ohlc, key, value)
                        else:
                            ohlc = OHLC(**ohlc_data)
                            session.add(ohlc)
                        success_count += 1
                    except SQLAlchemyError as e:
                        logger.error(f"Error processing OHLC data: {str(e)}")
                        continue
                session.flush()
        except SQLAlchemyError as e:
            logger.error(f"Bulk OHLC update error: {str(e)}")
        return success_count

    def update_trending_coins(self, trending_data: List[Dict]) -> int:
        """Update trending coins list."""
        success_count = 0
        try:
            with self.session_scope() as session:
                # Clear existing trending data
                session.query(TrendingCoin).delete()
                
                # Add new trending data
                for trend_data in trending_data:
                    try:
                        trending = TrendingCoin(**trend_data)
                        session.add(trending)
                        success_count += 1
                    except SQLAlchemyError as e:
                        logger.error(f"Error processing trending coin: {str(e)}")
                        continue
                session.flush()
        except SQLAlchemyError as e:
            logger.error(f"Trending coins update error: {str(e)}")
        return success_count

    def sync_with_api(self, api_fetcher) -> Tuple[int, int, int, int]:
        """
        Sync database with latest data from API.
        Returns tuple of (coins_updated, prices_updated, ohlc_updated, trending_updated)
        """
        try:
            # Update coins
            coins_data = api_fetcher.fetch_coins()
            coins_updated = self.bulk_update_coins(coins_data)

            # Update prices
            prices_data = api_fetcher.fetch_prices()
            prices_updated = 0
            for price_data in prices_data:
                if self.update_coin_price(price_data):
                    prices_updated += 1

            # Update OHLC
            ohlc_data = api_fetcher.fetch_ohlc()
            ohlc_updated = self.bulk_update_ohlc(ohlc_data)

            # Update trending
            trending_data = api_fetcher.fetch_trending()
            trending_updated = self.update_trending_coins(trending_data)

            return coins_updated, prices_updated, ohlc_updated, trending_updated

        except Exception as e:
            logger.error(f"API sync error: {str(e)}")
            return 0, 0, 0, 0

    def _clone_object(self, obj):
        """Create a dictionary of object attributes, excluding SQLAlchemy internal attributes."""
        if not obj:
            return None
        return {
            key: getattr(obj, key)
            for key in obj.__table__.columns.keys()
        }

    def _clone_object_list(self, objects):
        """Create a list of dictionaries from objects, excluding SQLAlchemy internal attributes."""
        return [self._clone_object(obj) for obj in objects]

    def get_all_coins(self) -> List[Dict]:
        """Retrieve all coins from the database."""
        try:
            with self.session_scope() as session:
                coins = session.query(Coin).options(
                    joinedload(Coin.prices),
                    joinedload(Coin.ohlc_data),
                    joinedload(Coin.trending_data)
                ).all()
                # Convert to dictionaries before session closes
                return self._clone_object_list(coins)
        except SQLAlchemyError as e:
            logger.error(f"Error fetching coins: {str(e)}")
            return []

    def get_coin_by_id(self, coin_id: str) -> Optional[Dict]:
        """Retrieve a specific coin by ID."""
        try:
            with self.session_scope() as session:
                coin = session.query(Coin).options(
                    joinedload(Coin.prices),
                    joinedload(Coin.ohlc_data),
                    joinedload(Coin.trending_data)
                ).filter_by(id=coin_id).first()
                return self._clone_object(coin)
        except SQLAlchemyError as e:
            logger.error(f"Error fetching coin {coin_id}: {str(e)}")
            return None

    def get_coin_by_symbol(self, symbol: str) -> Optional[Dict]:
        """
        Retrieve a specific coin by its symbol (case-insensitive).
        
        Args:
            symbol (str): The symbol of the coin (e.g., 'btc' for Bitcoin)
            
        Returns:
            Optional[Dict]: Dictionary containing coin data if found, None otherwise
        """
        try:
            with self.session_scope() as session:
                coin = session.query(Coin).options(
                    joinedload(Coin.prices),
                    joinedload(Coin.ohlc_data),
                    joinedload(Coin.trending_data)
                ).filter(Coin.symbol.ilike(symbol)).first()
                
                return self._clone_object(coin)
        except SQLAlchemyError as e:
            logger.error(f"Error fetching coin with symbol {symbol}: {str(e)}")
            return None

    def get_coin_price(self, coin_id: str, currency: str = 'usd') -> Optional[Dict]:
        """Get current price data for a specific coin."""
        try:
            with self.session_scope() as session:
                price = session.query(CoinPrice).filter_by(
                    coin_id=coin_id,
                    currency=currency
                ).order_by(desc(CoinPrice.last_updated)).first()
                return self._clone_object(price)
        except SQLAlchemyError as e:
            logger.error(f"Error fetching price for coin {coin_id}: {str(e)}")
            return None

    def get_ohlc_data(
        self,
        coin_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict]:
        """Retrieve OHLC data for a coin within a time range."""
        try:
            with self.session_scope() as session:
                ohlc_data = session.query(OHLC).filter(
                    and_(
                        OHLC.coin_id == coin_id,
                        OHLC.timestamp >= start_time,
                        OHLC.timestamp <= end_time
                    )
                ).order_by(OHLC.timestamp).all()
                return self._clone_object_list(ohlc_data)
        except SQLAlchemyError as e:
            logger.error(f"Error fetching OHLC data for coin {coin_id}: {str(e)}")
            return []

    def get_trending_coins(self, limit: int = 10) -> List[Dict]:
        """Retrieve trending coins ordered by rank."""
        try:
            with self.session_scope() as session:
                trending = session.query(TrendingCoin).options(
                    joinedload(TrendingCoin.coin)
                ).order_by(
                    TrendingCoin.rank
                ).limit(limit).all()
                return self._clone_object_list(trending)
        except SQLAlchemyError as e:
            logger.error(f"Error fetching trending coins: {str(e)}")
            return []