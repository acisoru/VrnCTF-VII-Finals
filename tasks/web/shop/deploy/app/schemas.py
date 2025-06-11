from pydantic import BaseModel
from typing import List, Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    balance: int
    class Config:
        orm_mode = True

class ItemOut(BaseModel):
    id: int
    title: str
    image: str
    price: int
    class Config:
        orm_mode = True

class ItemDetail(ItemOut):
    description: str

class Purchase(BaseModel):
    item_id: int
