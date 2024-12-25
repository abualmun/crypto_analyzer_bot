from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Index, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum

Base = declarative_base()

class TimeInterval(enum.Enum):
    ONE_DAY = 1
    SEVEN_DAYS = 7
    THIRTY_DAYS = 30
    NINETY_DAYS = 90

class CryptoOHLCV(Base):
    __tablename__ = 'crypto_ohlcv'
    
    id = Column(Integer, primary_key=True)
    coin_id = Column(String, nullable=False)
    vs_currency = Column(String, nullable=False)
    interval = Column(Enum(TimeInterval), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    market_cap = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)

    # Create indexes for faster querying
    __table_args__ = (
        Index('idx_coin_currency_interval_timestamp', 
              'coin_id', 'vs_currency', 'interval', 'timestamp'),
        Index('idx_last_updated', 'last_updated'),
    )

class CoinMetadata(Base):
    __tablename__ = 'coin_metadata'
    
    id = Column(Integer, primary_key=True)
    coin_id = Column(String, unique=True, nullable=False)
    symbol = Column(String)
    name = Column(String)
    extra_data = Column(JSON)
    last_updated = Column(DateTime, default=datetime.utcnow)
