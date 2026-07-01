import uvicorn
import asyncio
from fastapi import FastAPI, Path, Depends, HTTPException, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Optional, AsyncGenerator
from models import Product
from database import engine, AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import security
import database_models
from contextlib import asynccontextmanager
from logging_config import setup_logging, logger

setup_logging()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def send_notification(product_id: int, event: str):
    # Simulate an asynchronous I/O operation (e.g., sending an email or external API call)
    await asyncio.sleep(2)
    logger.info(f"NOTIFICATION: Product {product_id} was {event}")

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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB and Users
    async with AsyncSessionLocal() as db:
        # 1. Table creation is now handled by Alembic migrations
        pass

        # 2. Seed Products
        product_count = await db.execute(select(func.count()).select_from(database_models.Products))
        if product_count.scalar() == 0:
            for product in products:
                db.add(database_models.Products(**product.model_dump()))
            await db.commit()

        # 3. Seed Admin User
        user_count = await db.execute(select(func.count()).select_from(database_models.User))
        if user_count.scalar() == 0:
            admin = database_models.User(
                username="admin",
                hashed_password=security.get_password_hash("secret123"),
                role="admin"
            )
            db.add(admin)
            await db.commit()

    yield
    # Shutdown: clean up if needed
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

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

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    username = security.decode_access_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    result = await db.execute(select(database_models.User).where(database_models.User.username == username))
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def admin_required(user = Depends(get_current_user)):
    # Note: this is a sync wrapper for an async dependency.
    # Since it's used in Depends, FastAPI handles it.
    # But wait, get_current_user is async.
    # The function admin_required itself doesn't need to be async if it just checks the returned object.
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")
    return user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(database_models.User).where(database_models.User.username == form_data.username))
    user = result.scalars().first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = security.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/products")
async def get_all_products(db: AsyncSession = Depends(get_db), current_user = Depends(get_current_user)):
    result = await db.execute(select(database_models.Products))
    db_products = result.scalars().all()
    return db_products

@app.get("/product/{product_id}")
async def get_product(product_id: int, db : AsyncSession = Depends(get_db)):
    result = await db.execute(select(database_models.Products).where(database_models.Products.id == product_id))
    db_product = result.scalars().first()
    return db_product

@app.post("/product")
async def add_product(product: Product, db: AsyncSession = Depends(get_db), background_tasks: BackgroundTasks = Depends()):
    db_product = database_models.Products(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    background_tasks.add_task(send_notification, db_product.id, "CREATED")
    return  db_product

@app.put("/product/{product_id}")
async def update_product(product_id: int, product: Product, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(database_models.Products).where(database_models.Products.id == product_id))
    db_product = result.scalars().first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_product.name = product.name
    db_product.description = product.description
    db_product.price = product.price
    db_product.quantity = product.quantity
    await db.commit()
    return db_product

@app.delete("/product/{product_id}")
async def delete_product(product_id: int, user = Depends(admin_required), db: AsyncSession = Depends(get_db), background_tasks: BackgroundTasks = Depends()):
    result = await db.execute(select(database_models.Products).where(database_models.Products.id == product_id))
    db_product = result.scalars().first()
    if db_product:
        await db.delete(db_product)
        await db.commit()
        background_tasks.add_task(send_notification, product_id, "DELETED")
        return "Product deleted"
    return "Product not found"

@app.get("/greet")
async def greeting():
    return  "Hello Allen"

@app.get("/")
async def index():
    return {"Hello": "World"}

@app.get("/get_student/{student_id}")
async def get_student(student_id: int):
    if student_id not in students:
        return {"Data": "Student not found"}
    return students[student_id]

@app.get("/get_student_name")
async def get_student_name(name: Optional[str] = None):
    for student_id in students:
        if students[student_id]["name"] == name:
            return students[student_id]["name"]
    return {"Data": "Student not found"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5555)
