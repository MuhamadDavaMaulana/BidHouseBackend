from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone 
from typing import List

# db config
SQLALCHEMY_DATABASE_URL = "sqlite:///./bidhouse.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    
    items_created = relationship( 
        "Item", 
        foreign_keys="[Item.admin_id]", 
        back_populates="admin"
    )
    
    items_won = relationship( 
        "Item", 
        foreign_keys="[Item.winner_id]", 
        back_populates="winner"
    )
    
    bids = relationship("Bid", back_populates="bidder") 
    
class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    start_price = Column(Float, default=0.0)
    current_price = Column(Float, default=0.0)
    
    start_time = Column(DateTime, default=lambda: datetime.now(timezone.utc)) 
    end_time = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    admin_id = Column(Integer, ForeignKey("users.id"))
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True) 
    
    admin = relationship(
        "User", 
        back_populates="items_created", 
        foreign_keys=[admin_id]
    )
    
    winner = relationship(
        "User", 
        back_populates="items_won", 
        foreign_keys=[winner_id]
    )
    
    bids = relationship("Bid", back_populates="item")

class Bid(Base):
    __tablename__ = "bids"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    
    bid_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    item = relationship("Item", back_populates="bids")
    bidder = relationship("User", back_populates="bids")

def init_db():
    Base.metadata.create_all(bind=engine)
