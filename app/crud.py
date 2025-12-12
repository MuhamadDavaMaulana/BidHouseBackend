from sqlalchemy.orm import Session
from . import database, models, auth
from datetime import datetime, timezone 

def get_user_by_username(db: Session, username: str):
    return db.query(database.User).filter(database.User.username == username).first()

def get_user(db: Session, user_id: int):
    return db.query(database.User).filter(database.User.id == user_id).first()

def create_user(db: Session, user: models.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    
    db_user = database.User(
        username=user.username, 
        hashed_password=hashed_password, 
        is_admin=user.is_admin
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_item(db: Session, item_id: int):
    return db.query(database.Item).filter(database.Item.id == item_id).first()

def get_active_items(db: Session, skip: int = 0, limit: int = 10):
    return db.query(database.Item).filter(database.Item.is_active == True).offset(skip).limit(limit).all()

def create_item(db: Session, item: models.ItemCreate, admin_id: int):
    db_item = database.Item(
        **item.model_dump(), 
        admin_id=admin_id,
        current_price=item.start_price, 
        start_time=datetime.now(timezone.utc) 
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def close_auction(db: Session, item_id: int):
    db_item = get_item(db, item_id)
    
    if not db_item or not db_item.is_active:
        return None

    highest_bid = db.query(database.Bid) \
                     .filter(database.Bid.item_id == item_id) \
                     .order_by(database.Bid.amount.desc()) \
                     .first()

    if highest_bid:
        db_item.winner_id = highest_bid.user_id
        db_item.is_active = False
        db.commit()
        db.refresh(db_item)
        return db_item
    
    # tidak ada bid
    db_item.is_active = False
    db.commit()
    db.refresh(db_item)
    return db_item



def create_bid(db: Session, bid: models.BidCreate, user_id: int):
    db_bid = database.Bid(
        item_id=bid.item_id, 
        user_id=user_id, 
        amount=bid.amount, 
        bid_time=datetime.now(timezone.utc)
    )
    db.add(db_bid)
    
    db_item = get_item(db, bid.item_id)
    if db_item:
        db_item.current_price = bid.amount
        db.add(db_item)
        
    db.commit()
    db.refresh(db_bid) 
    return db_bid
