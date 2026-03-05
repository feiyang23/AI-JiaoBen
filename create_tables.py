# create_tables.py
from app.core.db import engine, Base
from app.models import user, question, answer  # 导入所有模型

# 显式声明checkfirst=True，创建前先检查
Base.metadata.create_all(bind=engine, checkfirst=True)
print("PostgreSQL表创建成功！")