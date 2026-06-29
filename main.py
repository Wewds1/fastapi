import uvicorn
import os
import asyncio
from fastapi import FastAPI, Path, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Optional
from models import Product
from database import session, engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import security
import database_models

load_dotenv()

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": str(exc), "path": request.url.path},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTP Error", "message": exc.detail, "path": request.url.path},
    )

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

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    username = security.decode_access_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user = db.query(database_models.User).filter(database_models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user





def init_db():
    db = session()
    count = db.query(database_models.Products).count()
    if count == 0:
        for product in products:
            db.add(database_models.Products(**product.model_dump()))
    db.commit()

def init_users():
    db = session()
    if db.query(database_models.User).count() == 0:
        admin = database_models.User(
            username="admin",
            hashed_password=security.get_password_hash("secret123"),
            role="admin"
        )
        db.add(admin)
        db.commit()


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()




init_db()
init_users()
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(database_models.User).filter(database_models.User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/products")
def get_all_products(db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
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




def admin_required(user = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user

@app.delete("/product/{product_id}")
def delete_product(product_id: int, user = Depends(admin_required), db: Session = Depends(get_db)):
    db_product = db.query(database_models.Products).filter(database_models.Products.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
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


