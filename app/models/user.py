# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base

# ---------------------- 关键：先导入中间表（避免作用域问题） ----------------------
from app.models.question import question_user_association

class User(Base):
    __tablename__ = "user"

    # 主键ID
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 手机号（唯一，非空）
    phone = Column(String(11), unique=True, nullable=False, comment="手机号")
    # 密码（加密后，非空）
    password = Column(String(100), nullable=False, comment="密码（加密）")
    # 是否启用（默认True）
    is_active = Column(Boolean, default=True, comment="是否启用")
    # 创建时间（带时区，默认当前时间）
    create_time = Column(DateTime(timezone=True), default=func.now(), comment="创建时间")
    # 更新时间（带时区，自动更新）
    update_time = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")

    # ---------------------- 关键：移除显式join条件 ----------------------
    questions = relationship(
        "Question",
        secondary=question_user_association,  # 只指定中间表即可
        back_populates="users",
        lazy="joined"
    )

    # 新增：关联答卷（一个用户有多个答卷）
    answers = relationship(
        "Answer",
        back_populates="user",
        lazy="joined"  # 懒加载优化（查询用户时自动加载答卷）
    )