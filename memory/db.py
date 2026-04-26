from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Generator
import os
from config import config

os.makedirs("data", exist_ok=True)
engine=create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base=declarative_base()

class TaskModel(Base):
  __tablename__="tasks"
  id=Column(Integer, primary_key=True, index=True)
  title=Column(String, nullable=False)
  description=Column(Text, default="")
  deadline=Column(DateTime, nullable=True)
  is_completed=Column(Boolean, default=False)
  create_at=Column(DateTime, default=datetime.timezone.utc.now)
  updata_at=Column(DateTime, default=datetime.timezone.utc.now, onupdate=datetime.timezone.utc.now)
  user_id=Column(Integer, default=1)

Base.metadata.create_all(bind=engine)  
def get_db() -> Generator[Session, None, None]:
  db=SessionLocal()
  try:
    yield db
  finally:
    db.close()