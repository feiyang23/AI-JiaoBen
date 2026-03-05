# app/models/answer.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, LargeBinary
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.db import Base

# ========== 新增：显式导入 User/Question 模型 ==========
# 解决 "expression 'User' failed to locate a name" 错误
from app.models.user import User
from app.models.question import Question

class Answer(Base):
    __tablename__ = "answer"

    # 主键
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # 关联用户（外键）
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, comment="用户ID")
    # 关联问题（外键）
    question_id = Column(Integer, ForeignKey("question.id"), nullable=False, comment="问题ID")
    # 音频转写后的文本内容（核心）
    content = Column(String(2000), default="", comment="音频转写文本")
    # 音频文件二进制（PostgreSQL用LargeBinary对应bytea类型）
    audio_file = Column(LargeBinary, nullable=True, comment="音频文件二进制")
    # 音频格式（如mp3/wav，方便后续解析）
    audio_format = Column(String(20), nullable=True, comment="音频格式")
    # 音频文件大小（字节，可选）
    audio_size = Column(Integer, nullable=True, comment="音频文件大小（字节）")
    # 创建时间
    create_time = Column(DateTime(timezone=True), default=func.now(), comment="创建时间")
    # 是否启用（默认True）
    is_active = Column(Boolean, default=True, comment="是否启用")

    # 关联关系：答卷→用户（反向关联）
    user = relationship(
        "User",  # 现在能正确找到导入的 User 模型
        back_populates="answers",
        lazy="joined"
    )
    # 关联关系：答卷→问题（反向关联）
    question = relationship(
        "Question",  # 现在能正确找到导入的 Question 模型
        back_populates="answers",
        lazy="joined"
    )