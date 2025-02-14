from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union, Tuple
from sqlalchemy import String, create_engine, and_, desc, func
from sqlalchemy.orm import sessionmaker, Session, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import DetachedInstanceError
from contextlib import contextmanager
import logging
from typing import List, Dict, Optional, Union, Tuple
from .database import User, UserType, UserActivity, Admin, AdminActivity, Base, Coin, CoinPrice, OHLC, TrendingCoin
import os
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, database_url: str = None):
        """Initialize database connection and session maker."""
        if database_url is None:
            database_url = self._construct_database_url()
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionMaker = sessionmaker(bind=self.engine)

    def _construct_database_url(self) -> str:
        """Construct PostgreSQL database URL from environment variables, prioritizing DATABASE_URL."""
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            return database_url
        else:
            return f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', '')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'crypto_analytics')}"
    
    def init_db(self) -> None:
        """Initialize the database and create all tables."""
        Base.metadata.create_all(self.engine)

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
        


        # Add these imports to existing ones


    def create_user(self, user_data: Dict) -> Optional[Dict]:
        """Create a new user in the database."""
        try:
            with self.session_scope() as session:
                user = User(**user_data)
                session.add(user)
                session.flush()
                return self._clone_object(user)
        except SQLAlchemyError as e:
            logger.error(f"Error creating user: {str(e)}")
            return None

    def get_user_by_telegram_id(self, telegram_id: str) -> Optional[Dict]:
        """Retrieve a user by their Telegram ID."""
        try:
            with self.session_scope() as session:
                user = session.query(User).filter_by(telegram_id=str(telegram_id)).first()
                return self._clone_object(user)
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user with telegram_id {telegram_id}: {str(e)}")
            return None

    def update_user_type(self, user_id: str, new_type: UserType, admin_id: str) -> Optional[Dict]:
        """Update a user's subscription type and log the change."""
        try:
            with self.session_scope() as session:
                user = session.query(User).filter_by(telegram_id=user_id).first()
                if not user:
                    return None

                old_type = user.user_type
                user.user_type = new_type
                user.last_active = datetime.utcnow()

                # Log admin activity
                admin_activity = AdminActivity(
                    admin_id=admin_id,
                    activity_type="user_type_update",
                    target_user_id=user_id,
                    details={
                        "old_type": old_type.value,
                        "new_type": new_type.value
                    }
                )
                session.add(admin_activity)
                session.flush()
                return self._clone_object(user)
        except SQLAlchemyError as e:
            logger.error(f"Error updating user type for user {user_id}: {str(e)}")
            return None

    def update_user_language(self, user_id: int, new_lang: String) -> bool:
        """Update user's language."""
        try:
            with self.session_scope() as session:
                user = session.query(User).filter_by(telegram_id=user_id).first()
                if not user:
                    return False

                user.language = new_lang

                session.flush()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error updating user language {user_id}: {str(e)}")
            return False

    def log_user_activity(self, activity_data: Dict) -> Optional[Dict]:
        """Log a user's activity."""
        try:
            with self.session_scope() as session:
                user = self.get_user_by_telegram_id(activity_data.get('user_id'))
                activity_data['user_id'] = user.get('telegram_id')
                activity = UserActivity(**activity_data)
                session.add(activity)
                session.flush()
                return self._clone_object(activity)
        except SQLAlchemyError as e:
            logger.error(f"Error logging activity for user {activity_data.get('user_id')}: {str(e)}")
            return None

    def create_admin(self, admin_data: Dict) -> Optional[Dict]:
        """
        Create a new admin with specified role.
        
        admin_data should contain:
        - user_id: ID of the user to make admin
        - role: List of privilege strings
        - created_by: ID of admin creating this admin
        """
        try:
            with self.session_scope() as session:
                # Check if user is already an admin
                existing_admin = session.query(Admin).filter_by(
                    user_id=admin_data['user_id'],
                    is_active=True
                ).first()
                
                if existing_admin:
                    logger.error(f"User {admin_data['user_id']} is already an admin")
                    return None
                admin = Admin(
                    user_id=admin_data['user_id'],
                    role=admin_data['role'],
                    created_by=admin_data.get('created_by')
                )
                session.add(admin)
                
                # Log admin creation
                # activity = AdminActivity(
                #     admin_id=admin_data['created_by'],
                #     activity_type="admin_created",
                #     target_user_id=admin_data['user_id'],
                #     details={"role": admin_data['role']}
                # )
                # session.add(activity)
                
                # session.flush()
                return self._clone_object(admin)
        except SQLAlchemyError as e:
            logger.error(f"Error creating admin: {str(e)}")
            return None

    def remove_admin(self, admin_id: str, removed_by: str) -> bool:
        """
        Permanently remove an admin record from the database.
        Returns True if successful, False otherwise.
        """
        try:
            with self.session_scope() as session:
                admin = session.query(Admin).filter_by(user_id=admin_id).first()
                if not admin:
                    logger.error(f"Active admin with ID {admin_id} not found")
                    return False
                
                # Log admin removal before deleting the record
                activity = AdminActivity(
                    admin_id=removed_by,
                    activity_type="admin_removed",
                    target_user_id=admin.user_id,
                    details={"removed_admin_id": admin_id}
                )
                session.add(activity)
                
                # Delete the admin record
                session.delete(admin)
                
                session.flush()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error removing admin {admin_id}: {str(e)}")
            return False
 
    def get_admin_by_user_id(self, user_id: str) -> Optional[Dict]:
        """Get admin info by user ID if they are an admin."""
        
        try:
            user = self.get_user_by_telegram_id(user_id)
            if user:
                with self.session_scope() as session:
                    admin = session.query(Admin).filter_by(
                        user_id=user.get('telegram_id'),
                    ).first()
                    return self._clone_object(admin)
            else:
                logger.error(f"Error fetching admin for user {user_id}")
                return None    
        except SQLAlchemyError as e:
            logger.error(f"Error fetching admin for user {user_id}: {str(e)}")
            return None

    def get_most_popular_coins(self, limit: int = 10) -> List[Dict]:
        """
        Retrieve the most popular searches across all users.
        
        Args:
            limit: Maximum number of results to return (default: 10)
            
        Returns:
            List of dictionaries containing search term and count
            Example: [{'search_term': 'BTC', 'count': 150}, ...]
        """
        try:
            with self.session_scope() as session:
                popular_coins = (
                    session.query(
                        UserActivity.coin_id,
                        func.count(UserActivity.coin_id).label('search_count')
                    )
                    .group_by(UserActivity.coin_id)
                    .order_by(desc('search_count'))
                    .limit(limit)
                    .all()
                )
                
                # Convert to list of dictionaries
                return [
                    {
                        'coin': search.coin_id,
                        'count': search.search_count
                    }
                    for search in popular_coins
                ]
        except SQLAlchemyError as e:
            logger.error(f"Error fetching popular searches: {str(e)}")
            return []
        
    def get_most_popular_analysis_types(self, limit: int = 10) -> List[Dict]:
        """
        Retrieve the most frequently performed analysis types across all users.
        Each unique combination of activity type and timestamp is counted as a separate analysis.
        
        Args:
            limit: Maximum number of results to return (default: 10)
            
        Returns:
            List of dictionaries containing analysis type and its frequency
            Example: [{'analysis_type': 'quick_analysis', 'count': 120}, ...]
        """
        try:
            with self.session_scope() as session:
                popular_analyses = (
                    session.query(
                        UserActivity.activity_type,
                        func.count(
                            func.distinct(
                                func.concat(
                                    UserActivity.activity_type,
                                    func.cast(UserActivity.timestamp, String)
                                )
                            )
                        ).label('activity_count')
                    )
                    .group_by(UserActivity.activity_type)
                    .order_by(desc('activity_count'))
                    .limit(limit)
                    .all()
                )
                
                # Convert to list of dictionaries with meaningful names
                return [
                    {
                        'analysis_type': activity.activity_type,
                        'count': activity.activity_count,
                    }
                    for activity in popular_analyses
                ]
        except SQLAlchemyError as e:
            logger.error(f"Error fetching popular analysis types: {str(e)}")
            return []

    def update_admin_role(self,admin_id,new_role,updated_by):
        try:
            with self.session_scope() as session:
                admin = session.query(Admin).filter_by(user_id=admin_id).first()
                if not admin:
                    return None

                old_role = admin.role
                admin.role = new_role
                
                # Log admin activity
                admin_activity = AdminActivity(
                    admin_id=updated_by,
                    activity_type="admin_role_change",
                    target_user_id=admin_id,
                    details={
                        "old_role": old_role.value,
                        "new_role": new_role.value
                    }
                )
                session.add(admin_activity)
                session.flush()
                return self._clone_object(admin)
        except SQLAlchemyError as e:
            logger.error(f"Error updating user role for admin {admin_id}: {str(e)}")
            return None

    def get_admin_activities(self, admin_id: Optional[int] = None, limit: int = 10) -> List[Dict]: 
        """Retrieve admin activities, optionally filtered by admin_id."""
        try:
            with self.session_scope() as session:
                query = session.query(AdminActivity)
                if admin_id is not None:
                    query = query.filter_by(admin_id=admin_id)
                activities = query.order_by(desc(AdminActivity.timestamp)).limit(limit).all()
                return self._clone_object_list(activities)
        except SQLAlchemyError as e:
            logger.error(f"Error fetching admin activities: {str(e)}")
            return []