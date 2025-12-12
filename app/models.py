from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    username: str
    is_admin: bool = False

class UserCreate(UserBase):
    password: str = Field(..., min_length=8) 

class UserInDB(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"



class TokenData(BaseModel):
    username: Optional[str] = None

class ItemBase(BaseModel):
    name: str
    description: str
    start_price: float
    end_time: datetime

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    end_time: Optional[datetime] = None

class ItemInDB(ItemBase):
    id: int
    admin_id: int
    current_price: float
    start_time: datetime
    is_active: bool
    winner_id: Optional[int] = None
    
    class Config:
        from_attributes = True
        

class BidBase(BaseModel):
    item_id: int
    amount: float

class BidCreate(BidBase):
    pass

class BidInDB(BidBase):
    id: int
    user_id: int
    bid_time: datetime
    
    class Config:
        from_attributes = True
