from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")


class Products(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name =  Column(String)
    description = Column(String)
    price = Column(Float)
    quantity = Column(Integer)


