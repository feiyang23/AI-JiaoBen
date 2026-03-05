# app/models/question.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Table, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base

# ---------------------- 1. 定义带外键的中间表（核心） ----------------------
question_user_association = Table(
    "question_user",  # 中间表名
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, index=True),
    # 关联question.id（外键约束）
    Column("question_id", Integer, ForeignKey("question.id"), nullable=False, index=True),
    # 关联user.id（外键约束）
    Column("user_id", Integer, ForeignKey("user.id"), nullable=False, index=True),
)

# ---------------------- 2. Question模型（适配你的title/description字段） ----------------------
class Question(Base):
    __tablename__ = "question"

    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 问题标题（替换原来的content，500字符，非空）
    title = Column(String(500), nullable=False, comment="问题标题")
    # 问题描述/提示（可选，1000字符，默认空字符串）
    description = Column(String(1000), default="", comment="问题描述/提示")
    # 创建时间（带时区，默认当前时间）
    create_time = Column(DateTime(timezone=True), default=func.now(), comment="创建时间")
    # 是否启用（默认True）
    is_active = Column(Boolean, default=True, comment="是否启用")

    # ---------------------- 关键：移除显式join条件，让SQLAlchemy自动识别外键 ----------------------
    users = relationship(
        "User",
        secondary=question_user_association,  # 只指定中间表即可
        back_populates="questions",
        lazy="joined"  # 懒加载优化（可选）
    )
    
    # 新增：关联答卷（一个问题有多个用户的答卷）
    answers = relationship(
        "Answer",
        back_populates="question",
        lazy="joined"
    )