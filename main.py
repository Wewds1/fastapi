import uvicorn
from fastapi import FastAPI, Path, Depends, HTTPException
from typing import Dict, Optional
from models import Product
from database import session, engine
from sqlalchemy.orm import Session

import database_models


app = FastAPI()

database_models.Base.metadata.create_all(engine)

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

def init_db():
    db = session()
    count = db.query(database_models.Products).count()
    if count == 0:
        for product in products:
            db.add(database_models.Products(**product.model_dump()))
    db.commit()


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()




init_db()
@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    db_products = db.query(database_models.Products).all()
    return db_products

@app.get("/product/{product_id}")
def get_product(product_id: int, db : Session = Depends(get_db)):
    db_product = db.query(database_models.Products).filter(database_models.Products.id == product_id).first()
    return db_product




@app.post("/product")
def add_product(product: Product, db: Session = Depends(get_db)):

    db_product = database_models.Products(**product.model_dump())
    db.add(db_product)
    db.commit()
    return  db_product



@app.put("/product/{product_id}")
def update_product(product_id: int, product: Product, db: Session = Depends(get_db)):
    db_product = db.query(database_models.Products).filter(database_models.Products.id == product.id).first()
    db_product.name = product.name
    db_product.description = product.description
    db_product.price = product.price
    db_product.quantity = product.quantity
    db.commit()
    return db_product




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


