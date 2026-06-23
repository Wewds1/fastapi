import uvicorn
from fastapi import FastAPI, Path
from typing import Dict, Optional
from models import Product
from database import session


app = FastAPI()



students = {
    1: {
        "name": "Allen",
        "age": 22,
    }
}


products = [
    Product(id=1, name="pencil", description="a pencil", price=100, quantity=10),
    Product(id=2, name="pen", description="a pen", price=100, quantity=10),
    Product(id=3, name="paper", description="a paper", price=100, quantity=10),
    Product(id=4, name="ColorPen", description="a coloring pen", price=100, quantity=10),
    Product(id=5, name="Bread", description="a bread", price=100, quantity=10),
]


@app.get("/products")
def get_all_products():
    db = session()
    db.query()
    return products

@app.get("/product/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product.id == product_id:
            return product
    return {"Data": "Product not found"}


@app.post("/product")
def add_product(product: Product):
    products.append(product)
    return product



@app.put("/product/{product_id}")
def update_product(product_id: int, product: Product):
    for i in range(len(products)):
        if products[i].id == product_id:
            products[i] = product
            return "Product updated"
    return "Product not found"


@app.delete("/product/{product_id}")
def delete_product(product_id: int):
    for i in range(len(products)):
        if products[i].id == product_id:
            del products[i]
            return "Product deleted"
    return "Product not found"



@app.get("/greet")
def greeting():
    return  "Hello Allen"

@app.get("/")
def index():
    return {"Hello": "World"}

@app.get("/get_student/{student_id}")
def get_student(student_id: int):
    if student_id not in students:
        return {"Data": "Student not found"}
    return students[student_id]


@app.get("/get_student_name")
def get_student_name(name: Optional[str] = None):
    for student_id in students:
        if students[student_id]["name"] == name:
            return students[student_id]["name"]
        return {"Data": "Student not found"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5555)


