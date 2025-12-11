from datetime import datetime, timezone 
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, models, auth
from ..database import SessionLocal 

router = APIRouter(tags=["Bids & Bidding"])

# dependency DB
def get_db():
    db = SessionLocal() 
    try:
        yield db
    finally:
        db.close()

@router.post("/bids", response_model=models.BidInDB, status_code=status.HTTP_201_CREATED)
def place_bid_on_item(
    bid: models.BidCreate, 
    db: Session = Depends(get_db), 
    current_user: models.UserInDB = Depends(auth.get_current_user) # Membutuhkan login
):
    """Menempatkan penawaran baru pada item lelang."""
    
    db_item = crud.get_item(db, bid.item_id)
    
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found.")
        
    aware_end_time = db_item.end_time.replace(tzinfo=timezone.utc)

    # validasi lelang (aktif / tidak)
    if not db_item.is_active or aware_end_time < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Auction for this item is closed or inactive.")
        
    # validasi bid
    if bid.amount <= db_item.current_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Bid amount must be higher than current price: {db_item.current_price}"
        )
        
    # buat Bid
    return crud.create_bid(db=db, bid=bid, user_id=current_user.id)