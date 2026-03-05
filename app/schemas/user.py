# 导入Pydantic核心校验类
from pydantic import BaseModel, Field, ConfigDict
# 导入时间类型（用于返回用户创建时间）
from datetime import datetime

# 基础用户信息校验模型（作为父类，供其他模型继承）
class UserBase(BaseModel):
    """用户基础信息校验模型（父类）"""
    pass  # 当前版本无需基础字段

# 注册请求校验模型
class UserRegisterRequest(BaseModel):
    """用户注册请求参数校验模型"""
    # 手机号：必填，固定11位（符合国内手机号规则）
    phone: str = Field(
        ..., 
        min_length=11, 
        max_length=11, 
        description="手机号（必填，11位数字）"
    )
    # 密码：必填，长度6-20字符
    password: str = Field(
        ..., 
        min_length=6, 
        max_length=20, 
        description="密码（必填，6-20字符）"
    )

# 登录请求校验模型（独立模型，仅包含手机号+密码）
class UserLoginRequest(BaseModel):
    """用户登录请求参数校验模型"""
    # 手机号：必填，固定11位
    phone: str = Field(
        ..., 
        min_length=11, 
        max_length=11, 
        description="手机号（必填，11位数字）"
    )
    # 密码：必填，长度6-20字符
    password: str = Field(
        ..., 
        min_length=6, 
        max_length=20, 
        description="密码（必填，6-20字符）"
    )

# 用户返回数据校验模型（隐藏密码，返回核心信息）
class UserResponse(BaseModel):
    """用户信息返回模型（隐藏敏感字段）"""
    # 用户ID（数据库自增主键）
    id: int
    # 手机号
    phone: str
    # 用户状态（是否激活）
    is_active: bool
    # 用户创建时间
    create_time: datetime

    # 关键配置：支持从ORM对象（如SQLAlchemy模型）自动转换为Pydantic模型
    model_config = ConfigDict(from_attributes=True)