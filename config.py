import os
from dotenv import load_dotenv

load_dotenv()

class config:
  DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
  DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
  DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

  DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///date/agent.db")

  @classmethod
  def validate(cls)->None:
    if not cls.DEEPSEEK_API_KEY:
      raise ValueError("DEEPSEEK_API_KEY is not set") 
    
config=config()
config.validate()