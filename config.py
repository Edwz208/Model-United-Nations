from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    REFRESH_KEY: str
    SPREADSHEET: str
    JWT_ALGORITHM: str = "HS256"
    DEBUG: bool = True
    WEBSOCKET_PATH: str = "/ws"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080
    
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")

settings = Settings() # type: ignore
