import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    BOT_TOKEN: str
    WEB_URL: str
    ADMIN_ID: int
    DB_URL: str
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
        extra='ignore'
    )

    def get_webhook(self):
        return f"{self.WEB_URL}/webhook"
    
settings = Settings()

