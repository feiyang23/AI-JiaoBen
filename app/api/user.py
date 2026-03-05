# app/api/user.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserResponse
from app.service.user_service import user_register, user_login
from app.core.db import get_db
from app.utils.jwt_util import verify_access_token
from app.models.user import User

router = APIRouter()

# 注册接口
@router.post("/register", summary="用户注册", response_model=UserResponse)
async def register(
    req: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    return user_register(db, req)

# 登录接口
@router.post("/login", summary="用户登录")
async def login(
    req: UserLoginRequest,
    db: Session = Depends(get_db)
):
    result = user_login(db, req)
    return {
        "code": 0,
        "msg": "登录成功",
        "data": {
            "user_info": UserResponse.model_validate(result["user_info"]), 
            "access_token": result["access_token"],
            "token_type": result["token_type"]
        }
    }

# 获取用户信息（鉴权）
@router.get("/info", summary="获取用户信息", response_model=UserResponse)
async def get_user_info(
    request: Request,
    db: Session = Depends(get_db)
):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少有效的认证令牌")
    
    token = auth_header.split(" ")[1]
    try:
        user_id = verify_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"鉴权失败：{str(e)}")
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return UserResponse.model_validate(db_user)