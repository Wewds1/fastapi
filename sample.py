from pydantic import BaseModel



class Library (BaseModel):
    name: str
    price: float
    quantity: int


