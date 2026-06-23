from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey

Base = declarative_base()


class Products(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name =  Column(String)
    description = Column(String)
    price = Column(Float)
    quantity = Column(Integer)


