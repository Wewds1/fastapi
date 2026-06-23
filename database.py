from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



db_url = "postgresql://postgres:3283@localhost:5432/products"
engine = create_engine(db_url)
session = sessionmaker(autocommit=False, autoflush=True, bind=engine)


