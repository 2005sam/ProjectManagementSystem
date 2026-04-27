from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime,timezone
from typing import Generator
import os
from config import config
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

os.makedirs("date", exist_ok=True)
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
  create_at=Column(DateTime, default=datetime.now(timezone.utc))
  updata_at=Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
  user_id=Column(Integer, default=1)
  parent_id=Column(Integer, ForeignKey("tasks.id"), nullable=True)
  children_id=relationship("TaskModel", backref=backref("parent", remote_side=[id]))

Base.metadata.create_all(bind=engine)  
def get_db() -> Generator[Session, None, None]:
  db=SessionLocal()
  try:
    yield db
  finally:
    db.close()