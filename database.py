import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///app.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

session = SessionLocal()

# Create tables only if not in production (to avoid issues with migrations)
if os.environ.get("FLASK_ENV") != "production":
    Base.metadata.create_all(bind=engine)
