from sqlalchemy.orm import Session
from typing import List,Optional
from datetime import datetime

from .db import TaskModel,SessionLocal

class TaskManager:
  def __init__(self,db:Session=None):
    self.db=db or SessionLocal()
    self._own_session = db is None
  def __enter__(self):
    return self
  def __exit__(self, exc_type, exc_val, exc_tb):
    if self._own_session:
      self.db.close()
  def create_task(self, title:str,description:str="",deadline:Optional[datetime]=None,parent_id:Optional[int]=None)->TaskModel:
    task=TaskModel(title=title,
          description=description,
          deadline=deadline,
          is_completed=False,
          parent_id=parent_id)
    self.db.add(task)
    self.db.commit()
    self.db.refresh(task)
    return task
  def get_task(self,task_id:int)->Optional[TaskModel]:
    return self.db.query(TaskModel).filter(TaskModel.id==task_id).first()
  def list_tasks(self,completed:Optional[bool]=None,limit:int=50)->List[TaskModel]:
    query=self.db.query(TaskModel)
    if completed is not None:
      query=query.filter(TaskModel.is_completed==completed)
    return query.order_by(TaskModel.create_at.desc()).limit(limit).all()
  def update_task(self,task_id:int,**kwargs)->TaskModel:
    task=self.get_task(task_id)
    if not task:
      return None
    for key,value in kwargs.items():
      if hasattr(task,key):
        setattr(task,key,value)
      self.db.commit()
      self.db.refresh(task)
      return task
  def delete_task(self,task_id:int)->bool:
    task=self.get_task(task_id)
    if not task:
      return False
    self.db.delete(task)
    self.db.commit()
    return True 
  def get_task_tree(self)->List[dict]:
    all_tasks=self.db.query(TaskModel).order_by(TaskModel.id).all()
    task_map={t.id:t for t in all_tasks}
    roots=[]
    for t in all_tasks:
      if t.parent_id is None:
        roots.append(t)
      else:
        parent=task_map.get(t.parent_id)
        if parent:
          pass
    return roots
def get_task_manager()->TaskManager:
  return TaskManager()