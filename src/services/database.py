from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

# Create base class for declarative models
Base = declarative_base()

class Coin(Base):
    """Model for storing basic cryptocurrency information."""
    __tablename__ = 'coins'

    id = Column(String, primary_key=True)  # e.g., "bitcoin"
    symbol = Column(String, nullable=False)  # e.g., "btc"
    name = Column(String, nullable=False)  # e.g., "Bitcoin"
    platforms = Column(JSON)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    prices = relationship("CoinPrice", back_populates="coin", cascade="all, delete-orphan")
    ohlc_data = relationship("OHLC", back_populates="coin", cascade="all, delete-orphan")
    trending_data = relationship("TrendingCoin", back_populates="coin", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Coin(id={self.id}, symbol={self.symbol}, name={self.name})>"

class CoinPrice(Base):
    """Model for storing current price data for cryptocurrencies."""
    __tablename__ = 'coin_prices'

    id = Column(Integer, primary_key=True)
    coin_id = Column(String, ForeignKey('coins.id', ondelete='CASCADE'), nullable=False)
    currency = Column(String, nullable=False)
    price = Column(Float)
    market_cap = Column(Float)
    volume_24h = Column(Float)
    price_change_24h = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)

    # Relationship
    coin = relationship("Coin", back_populates="prices")

    # Unique constraint for coin_id and currency combination
    __table_args__ = (UniqueConstraint('coin_id', 'currency', name='unique_coin_currency'),)

    def __repr__(self):
        return f"<CoinPrice(coin_id={self.coin_id}, currency={self.currency}, price={self.price})>"

class OHLC(Base):
    """Model for storing historical OHLC (Open, High, Low, Close) data."""
    __tablename__ = 'ohlc'

    id = Column(Integer, primary_key=True)
    coin_id = Column(String, ForeignKey('coins.id', ondelete='CASCADE'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)

    # Relationship
    coin = relationship("Coin", back_populates="ohlc_data")

    # Unique constraint for coin_id and timestamp combination
    __table_args__ = (UniqueConstraint('coin_id', 'timestamp', name='unique_coin_timestamp'),)

    def __repr__(self):
        return f"<OHLC(coin_id={self.coin_id}, timestamp={self.timestamp}, close={self.close})>"

class TrendingCoin(Base):
    """Model for storing trending cryptocurrency data."""
    __tablename__ = 'trending_coins'

    id = Column(Integer, primary_key=True)
    coin_id = Column(String, ForeignKey('coins.id', ondelete='CASCADE'), nullable=False)
    rank = Column(Integer, nullable=False)
    score = Column(Float)
    market_cap = Column(Float)
    thumb = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)

    # Relationship
    coin = relationship("Coin", back_populates="trending_data")

    # Unique constraint for coin_id (one trending entry per coin)
    __table_args__ = (UniqueConstraint('coin_id', name='unique_trending_coin'),)

    def __repr__(self):
        return f"<TrendingCoin(coin_id={self.coin_id}, rank={self.rank}, score={self.score})>"

# Database initialization function
def init_db(database_url='sqlite:///crypto_analytics.db'):
    """Initialize the database and create all tables."""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()