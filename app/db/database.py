import os

from typing import Generator

from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine=create_engine(DATABASE_URL)

def create_db_and_tables():
	SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            print("=" * 50)
            print("✅ PostgreSQL connected successfully")
            print(result.scalar())
            print("=" * 50)

    except Exception as e:
        print(e)