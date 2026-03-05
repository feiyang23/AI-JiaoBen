# app/api/answer.py
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Request, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.db import get_db
from app.schemas.answer import (
    AnswerCreateRequest, AnswerResponse, AnswerListResponse, AnswerUpdateRequest
)
from app.service.answer_service import (
    create_answer, get_answer_list_for_user, get_answer_detail, update_answer_status, update_answer_content
)
from app.utils.jwt_util import verify_access_token
from app.models.question import question_user_association
from sqlalchemy import and_
import json

router = APIRouter()

# ---------------------- 依赖：获取当前登录用户ID ----------------------
def get_current_user_id(
    request: Request,  # 第一步：正确注入Request对象
    db: Session = Depends(get_db)
):
    try:
        # 第二步：从Request.headers获取Authorization头
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="未传入Authorization令牌")
        
        # 第三步：拆分Bearer Token（处理格式错误）
        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            raise HTTPException(status_code=401, detail="令牌格式错误，需为Bearer + token")
        
        token = parts[1]
        user_id = verify_access_token(token)  # 解析token获取user_id
        return user_id
    except HTTPException:
        raise  # 业务异常直接抛出
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"鉴权失败：{str(e)}")

# ---------------------- 接口1：创建答卷（支持音频上传+文本） ----------------------
@router.post("/create", summary="创建答卷（支持音频+文本）", response_model=AnswerResponse)
async def create_answer_api(
    # 将req作为表单字段接收，然后手动解析为Pydantic模型
    req_data: str = Form(...),  # 客户端需要将JSON序列化为字符串
    audio_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    # 手动解析req_data为AnswerCreateRequest对象
    try:
        req_dict = json.loads(req_data)
        req = AnswerCreateRequest(**req_dict)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"req参数解析失败：{str(e)}")
    
    # 校验当前用户是否有权限访问该问题
    is_authorized = db.query(question_user_association).filter(
        and_(
            question_user_association.c.question_id == req.question_id,
            question_user_association.c.user_id == user_id
        )
    ).first()
    if not is_authorized:
        raise HTTPException(status_code=403, detail="无权限回答该问题")
    
    # 处理音频文件（如果上传）
    audio_data = None
    audio_format = None
    audio_size = None
    if audio_file:
        audio_data = await audio_file.read()  # 读取二进制数据
        audio_format = audio_file.filename.split(".")[-1] if "." in audio_file.filename else None
        audio_size = len(audio_data)
    
    # 调用service创建答卷
    return create_answer(
        db=db,
        req=req,
        user_id=user_id,
        audio_file=audio_data,
        audio_format=audio_format,
        audio_size=audio_size
    )

# ---------------------- 接口2：获取当前用户的答卷列表 ----------------------
@router.get("/list", summary="获取当前用户的答卷列表", response_model=AnswerListResponse)
async def get_answer_list_api(
    question_id: Optional[int] = Query(None, description="按问题ID筛选"),
    is_active: Optional[bool] = Query(None, description="是否启用：true/false"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=50, description="每页条数"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    return get_answer_list_for_user(
        db=db,
        user_id=user_id,
        question_id=question_id,
        is_active=is_active,
        page=page,
        size=size
    )

# ---------------------- 接口3：获取答卷详情 ----------------------
@router.get("/{answer_id}", summary="获取答卷详情", response_model=AnswerResponse)
async def get_answer_detail_api(
    answer_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    # 校验答卷归属（只能看自己的答卷）
    answer = get_answer_detail(db, answer_id)
    if answer.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权限查看该答卷")
    return answer

# ---------------------- 接口4：更新答卷启用状态 ----------------------
@router.put("/{answer_id}/status", summary="更新答卷启用状态", response_model=AnswerResponse)
async def update_answer_status_api(
    answer_id: int,
    is_active: bool = Query(..., description="是否启用：true/false"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    # 校验归属
    answer = get_answer_detail(db, answer_id)
    if answer.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权限修改该答卷")
    return update_answer_status(db, answer_id, is_active)

# ---------------------- 接口5：更新答卷文本内容 ----------------------
@router.put("/{answer_id}/content", summary="更新答卷文本内容", response_model=AnswerResponse)
async def update_answer_content_api(
    answer_id: int,
    content: str = Query(..., max_length=2000, description="音频转写文本"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    # 校验归属
    answer = get_answer_detail(db, answer_id)
    if answer.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权限修改该答卷")
    return update_answer_content(db, answer_id, content)