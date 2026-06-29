from pydantic import BaseModel, Field


class Product(BaseModel):
    id: int = Field(..., description="The product ID")
    name: str = Field(..., min_length=1, max_length=255, description="The name of the product")
    description: str = Field(..., min_length=1, max_length=255, description="A brief description of the product")
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    quantity: int = Field(..., ge=0, description="The quantity must be zero or more")
