from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from .database import get_db, engine
from .models.database import Base, Product as DBProduct, Student as DBStudent
from .models.schemas import Product, Student
from contextlib import asynccontextmanager
import asyncio

async def send_notification(product_id: int, event: str):
    await asyncio.sleep(2)
    print(f"NOTIFICATION: Product {product_id} was {event}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan, title="CMS Content Service")

@app.get("/products")
async def get_all_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBProduct))
    return result.scalars().all()

@app.get("/product/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBProduct).where(DBProduct.id == product_id))
    return result.scalars().first()

@app.post("/product")
async def add_product(product: Product, db: AsyncSession = Depends(get_db), background_tasks: BackgroundTasks = Depends()):
    db_product = DBProduct(**product.model_dump())
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    background_tasks.add_task(send_notification, db_product.id, "CREATED")
    return db_product

@app.put("/product/{product_id}")
async def update_product(product_id: int, product: Product, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBProduct).where(DBProduct.id == product_id))
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
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db), background_tasks: BackgroundTasks = Depends()):
    result = await db.execute(select(DBProduct).where(DBProduct.id == product_id))
    db_product = result.scalars().first()
    if db_product:
        await db.delete(db_product)
        await db.commit()
        background_tasks.add_task(send_notification, product_id, "DELETED")
        return "Product deleted"
    return "Product not found"

@app.get("/student/{student_id}")
async def get_student(student_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBStudent).where(DBStudent.id == student_id))
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.get("/student/search")
async def search_student(name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBStudent).where(DBStudent.name == name))
    student = result.scalars().first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
