# app/core/settings.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()  # 加载.env文件

class Settings(BaseSettings):
    # PostgreSQL配置
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: int = os.getenv("DB_PORT")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")
    DB_NAME: str = os.getenv("DB_NAME")
    # Redis配置
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_PORT: int = os.getenv("REDIS_PORT")
    # JWT配置
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    JWT_EXPIRE_MINUTES: int = os.getenv("JWT_EXPIRE_MINUTES")
    # 服务配置
    SERVER_HOST: str = os.getenv("SERVER_HOST")
    SERVER_PORT: int = os.getenv("SERVER_PORT")

    # PostgreSQL连接URL（核心）
    @property
    def DB_URL(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # 讯飞LFasr配置
    XF_APP_ID: str = os.getenv("XF_APP_ID")
    XF_API_SECRET: str = os.getenv("XF_API_SECRET")
    XF_AUDIO_TIMEOUT: int = int(os.getenv("XF_AUDIO_TIMEOUT", 30))  # 转写超时时间
    XF_AUDIO_INTERVAL: int = int(os.getenv("XF_AUDIO_INTERVAL", 5))  # 轮询间隔
settings = Settings()