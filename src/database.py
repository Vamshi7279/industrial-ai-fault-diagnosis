import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.config import settings
from src.models_orm import Base

db_url = settings.DATABASE_URL
is_sqlite = db_url.startswith("sqlite")

connect_args = {"check_same_thread": False, "timeout": 30.0} if is_sqlite else {}

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    if is_sqlite:
        # Enable WAL mode for SQLite concurrency
        raw_db_path = db_url.replace("sqlite:///", "").replace("./", "")
        if os.path.exists(raw_db_path):
            try:
                conn = sqlite3.connect(raw_db_path, timeout=30.0)
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.execute("PRAGMA busy_timeout=30000;")
                conn.close()
            except Exception as e:
                print(f"[DB] SQLite WAL mode setup warning: {e}")

    Base.metadata.create_all(bind=engine)
    print(f"[Database] Engine initialized cleanly using: {db_url}")
