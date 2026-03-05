# app/schemas/question.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.schemas.user import UserResponse  # 复用用户响应模型

# ---------------------- 基础模型 ----------------------
class QuestionBase(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500, description="问题标题")
    description: Optional[str] = Field(None, min_length=1, max_length=1000, description="问题描述/提示")
    is_active: Optional[bool] = Field(None, description="是否启用")

# ---------------------- 请求模型 ----------------------
# 创建问题请求
class QuestionCreateRequest(QuestionBase):
    title: str = Field(..., min_length=1, max_length=500, description="问题标题")  # 必传
    description: str = Field(..., min_length=1, max_length=1000, description="问题描述/提示")  # 必传

# 分配问题给用户的请求（核心：手动配置可见性）
class QuestionAssignUserRequest(BaseModel):
    question_id: int = Field(..., description="问题ID")
    user_ids: List[int] = Field(..., description="要分配的用户ID列表（支持多个）")

# ---------------------- 响应模型 ----------------------
# 问题响应（包含可查看的用户列表）
class QuestionResponse(QuestionBase):
    id: int
    create_time: datetime
    users: Optional[List[UserResponse]] = None  # 多对多关联的用户列表
    model_config = ConfigDict(from_attributes=True)  # 支持ORM模型转换

# 问题列表响应
class QuestionListResponse(BaseModel):
    total: int
    items: List[QuestionResponse]