# app/schemas/answer.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.schemas.user import UserResponse
from app.schemas.question import QuestionResponse

# ---------------------- 基础模型（父类） ----------------------
class AnswerBase(BaseModel):
    """答卷基础信息校验模型（父类）"""
    content: Optional[str] = Field(None, max_length=2000, description="音频转写文本")
    audio_format: Optional[str] = Field(None, max_length=20, description="音频格式（mp3/wav）")
    audio_size: Optional[int] = Field(None, description="音频文件大小（字节）")
    is_active: Optional[bool] = Field(None, description="是否启用")

# ---------------------- 请求模型 ----------------------
class AnswerCreateRequest(AnswerBase):
    """创建答卷请求模型"""
    question_id: int = Field(..., description="问题ID（必填）")
    content: str = Field("", max_length=2000, description="音频转写文本（默认空）")  # 非必填，兼容仅上传音频场景

class AnswerUpdateRequest(AnswerBase):
    """更新答卷请求模型"""
    pass  # 按需扩展字段

# ---------------------- 响应模型 ----------------------
class AnswerResponse(AnswerBase):
    """答卷信息返回模型"""
    id: int
    user_id: int
    question_id: int
    create_time: datetime
    user: Optional[UserResponse] = None  # 关联用户信息

    # 支持从 SQLAlchemy ORM 对象自动转换
    model_config = ConfigDict(from_attributes=True)

class AnswerListResponse(BaseModel):
    """答卷列表返回模型"""
    total: int
    items: List[AnswerResponse]