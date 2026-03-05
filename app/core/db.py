# app/core/db.py
from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings

# 创建PostgreSQL引擎
engine = create_engine(
    settings.DB_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"options": "-c timezone=Asia/Shanghai"}  # 时区适配
)
# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 模型基类
Base = declarative_base()

# 依赖项：获取数据库会话（FastAPI注入用）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()