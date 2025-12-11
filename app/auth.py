from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError 
from . import crud, models
from .database import SessionLocal 

# config JWT
SECRET_KEY = "INI_RAHASIA_DAN_HARUS_DIGANTI" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# argon2
ph = PasswordHasher()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token") 

# dependency DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Memverifikasi password menggunakan Argon2."""
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Menghasilkan hash Argon2 dari password biasa."""
    return ph.hash(password) 


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    now_utc = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now_utc + expires_delta
    else:
        expire = now_utc + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[models.TokenData]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = models.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> models.UserInDB:
    token_data = decode_access_token(token)
    
    if token_data is None or token_data.username is None:
         raise HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Token invalid or expired",
             headers={"WWW-Authenticate": "Bearer"},
         )
    
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return models.UserInDB.model_validate(user)

def get_current_admin(current_user: models.UserInDB = Depends(get_current_user)) -> models.UserInDB:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation forbidden. Admin access required."
        )
    return current_user