import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from redis.asyncio import Redis

load_dotenv()

redis_client = Redis.from_url("redis://redis:6379", decode_responses=True)

# Для удобного получения секретных данных
class Settings(BaseSettings):
    BOT_TOKEN: str
    WEB_URL: str
    ADMIN_ID: int
    DB_URL: str
    GEMINI_API_KEY: str
    POSTGRES_PASSWORD: str
    GROQ_API_KEY: str
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        extra='ignore'
    )

    def get_webhook(self):
        return f"{self.WEB_URL}/webhook"
    
settings = Settings()

