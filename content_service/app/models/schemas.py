from pydantic import BaseModel, Field, field_validator
from typing import Optional

class Product(BaseModel):
    id: int = Field(..., description="The product ID")
    name: str = Field(..., min_length=1, max_length=255, description="The name of the product")
    description: str = Field(..., min_length=1, max_length=255, description="A brief description of the product")
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    quantity: int = Field(..., ge=0, description="The quantity must be zero or more")

class Student(BaseModel):
    id: int = Field(..., description="The student ID")
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., gt=0, lt=120)

    @field_validator('age')
    @classmethod
    def age_must_be_realistic(cls, v: int) -> int:
        if v < 5:
            raise ValueError('Student age must be at least 5 years old')
        return v
