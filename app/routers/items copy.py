# app/routers/items.py
from datetime import datetime, timezone 
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, models, auth
from ..database import SessionLocal 

router = APIRouter(tags=["Auction Items"])

# Dependency DB
def get_db():
    db = SessionLocal() 
    try:
        yield db
    finally:
        db.close()

# --- ADMIN-ONLY ROUTES ---

@router.post("/items", response_model=models.ItemInDB, status_code=status.HTTP_201_CREATED)
def create_new_item(
    item: models.ItemCreate, 
    db: Session = Depends(get_db), 
    current_admin: models.UserInDB = Depends(auth.get_current_admin)
):
    """Membuat item lelang baru (Hanya Admin)."""
    # Validasi: end_time harus di masa depan
    # Perbandingan antara waktu Pydantic (Aware) dengan waktu saat ini (Aware) sudah benar.
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
        
    # Placeholder: Menggunakan logika update langsung di router
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
        
    # PERBAIKAN KRITIS: Mengatasi TypeError dengan menjadikan waktu DB 'aware'
    aware_end_time = db_item.end_time.replace(tzinfo=timezone.utc)
        
    # Validasi: Hanya dapat ditutup jika waktu sudah berakhir (membandingkan dua objek 'aware')
    if aware_end_time > datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Auction period is not over yet.")

    closed_item = crud.close_auction(db, item_id)
    
    if closed_item is None:
        # Ini terjadi jika crud.close_auction gagal (misalnya item sudah ditutup sebelumnya)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Auction is already closed or failed to find winner.")
        
    return closed_item

# --- PUBLIC/AUTHENTICATED ROUTES ---

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