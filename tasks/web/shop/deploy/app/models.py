from sqlalchemy import Column, Integer, String, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from .database import Base

# Association table for purchases
purchase_table = Table(
    'purchases', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('item_id', Integer, ForeignKey('items.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    balance = Column(Integer, default=100)
    purchases = relationship("Item", secondary=purchase_table, back_populates="buyers")

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    image = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Integer, default=10)
    buyers = relationship("User", secondary=purchase_table, back_populates="purchases")
