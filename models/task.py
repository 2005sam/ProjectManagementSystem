from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TaskCreate(BaseModel):
  title: str=Field(...,min_length=1,max_length=200,description="Title of the task")
  description: str=Field(...,min_length=1,max_length=500,description="Description of the task")
  deadline: Optional[datetime]= Field(...,description="End date of the task,ISO format (YYYY-MM-DD)")

class TaskUpdata(BaseModel):
  title: Optional[str]=Field(None,min_length=1,max_length=200,description="Title of the task")
  description: Optional[str]=None
  deadline: Optional[datetime]=None
  is_complete:Optional[bool]=None

class TaskResponse(BaseModel):
  id: int
  title: str
  description: str
  deadline: Optional[datetime]=None
  is_complete: bool
  created_at: datetime
  updated_at: datetime 
  class Config:
    from_attributes = True
