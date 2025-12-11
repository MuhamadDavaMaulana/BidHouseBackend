from datetime import datetime, timezone 
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, models, auth
from ..database import SessionLocal 

router = APIRouter(tags=["Auction Items"])

# dependency DB
def get_db():
    db = SessionLocal() 
    try:
        yield db
    finally:
        db.close()

# admin only
@router.post("/items", response_model=models.ItemInDB, status_code=status.HTTP_201_CREATED)
def create_new_item(
    item: models.ItemCreate, 
    db: Session = Depends(get_db), 
    current_admin: models.UserInDB = Depends(auth.get_current_admin)
):
    """Membuat item lelang baru (Hanya Admin)."""
    # validasi end_time
    if item.end_time <= datetime.now(timezone.utc):
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="End time must be after the current time.")
         
    return crud.create_item(db=db, item=item, admin_id=current_admin.id)

@router.patch("/items/{item_id}", response_model=models.ItemInDB)
def update_item_info(
    item_id: int, 
    item: models.ItemUpdate, 
    db: Session = Depends(get_db), 
    current_admin: models.UserInDB = Depends(auth.get_current_admin)
):
    """Memperbarui informasi item (Hanya Admin)."""
    db_item = crud.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        
    update_data = item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/items/{item_id}", status_code=status.HTTP_200_OK)
def delete_item_by_id(
    item_id: int, 
    db: Session = Depends(get_db), 
    current_admin: models.UserInDB = Depends(auth.get_current_admin)
):
    """Menghapus item lelang (Hanya Admin)."""
    db_item = crud.get_item(db, item_id)
    if db_item is None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}

@router.post("/items/{item_id}/close", response_model=models.ItemInDB)
def close_auction(
    item_id: int, 
    db: Session = Depends(get_db), 
    current_admin: models.UserInDB = Depends(auth.get_current_admin)
):
    """Menutup lelang secara manual dan menentukan pemenang (Hanya Admin)."""
    db_item = crud.get_item(db, item_id)
    
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        
    aware_end_time = db_item.end_time.replace(tzinfo=timezone.utc)
    
    if aware_end_time > datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Auction period is not over yet.")

    closed_item = crud.close_auction(db, item_id)
    
    if closed_item is None:
        # gagal ada pemenang (misal tidak ada bid)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Auction is already closed or failed to find winner.")
        
    return closed_item

# public routes
@router.get("/items", response_model=List[models.ItemInDB])
def read_active_items(db: Session = Depends(get_db)):
    """Melihat daftar semua item lelang yang aktif (Akses Publik)."""
    items = crud.get_active_items(db)
    return items

@router.get("/items/{item_id}", response_model=models.ItemInDB)
def read_item(item_id: int, db: Session = Depends(get_db)):
    """Melihat detail spesifik item lelang (Akses Publik)."""
    db_item = crud.get_item(db, item_id)
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return db_item