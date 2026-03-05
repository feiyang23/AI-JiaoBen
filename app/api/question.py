# app/api/question.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

# 新增：导入缺失的变量
from sqlalchemy import and_  # 用到and_条件，必须导入
from app.models.question import question_user_association  # 导入关联表

from app.core.db import get_db
from app.schemas.question import (
    QuestionCreateRequest, QuestionResponse, QuestionListResponse,
    QuestionAssignUserRequest
)
from app.service.question_service import (
    create_question, assign_question_to_users,
    get_question_list_for_user, get_question_detail,
    update_question_status
)
from app.utils.jwt_util import verify_access_token

router = APIRouter()

# 依赖：获取当前登录用户ID
def get_current_user_id(
    token: str = Depends(lambda request: request.headers.get("Authorization").split(" ")[1] if request.headers.get("Authorization") else None),
    db: Session = Depends(get_db)
):
    try:
        user_id = verify_access_token(token)
        return user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"鉴权失败：{str(e)}")

# ---------------------- 接口1：创建问题 ----------------------
@router.post("/create", summary="创建问题", response_model=QuestionResponse)
async def create_question_api(
    req: QuestionCreateRequest,
    db: Session = Depends(get_db),
    # 无需user_id：创建问题时不分配用户，后续手动分配
):
    return create_question(db, req)

# ---------------------- 接口2：分配问题给用户（核心） ----------------------
@router.post("/assign", summary="分配问题给用户（配置谁能看该问题）", response_model=QuestionResponse)
async def assign_question_to_users_api(
    req: QuestionAssignUserRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)  # 仅登录用户可分配（可后续加管理员权限）
):
    return assign_question_to_users(db, req)

# ---------------------- 接口3：获取当前用户能看到的问题列表 ----------------------
@router.get("/list", summary="获取当前用户可见的问题列表", response_model=QuestionListResponse)
async def get_question_list_api(
    is_active: Optional[bool] = Query(None, description="是否启用：true/false"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=50, description="每页条数"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    return get_question_list_for_user(db, user_id, is_active, page, size)

# ---------------------- 接口4：获取问题详情 ----------------------
@router.get("/{question_id}", summary="获取问题详情（含可查看的用户）", response_model=QuestionResponse)
async def get_question_detail_api(
    question_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    # 校验当前用户是否有权限查看该问题
    is_authorized = db.query(question_user_association).filter(
        and_(
            question_user_association.c.question_id == question_id,
            question_user_association.c.user_id == user_id
        )
    ).first()
    if not is_authorized:
        raise HTTPException(status_code=403, detail="无权限查看该问题")
    
    return get_question_detail(db, question_id)

# ---------------------- 接口5：更新问题启用状态 ----------------------
@router.put("/{question_id}/status", summary="更新问题启用状态", response_model=QuestionResponse)
async def update_question_status_api(
    question_id: int,
    is_active: bool = Query(..., description="是否启用：true/false"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    return update_question_status(db, question_id, is_active)