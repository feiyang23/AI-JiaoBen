# app/service/answer_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import and_
from app.models.answer import Answer
from app.models.question import Question
from app.schemas.answer import AnswerCreateRequest, AnswerUpdateRequest

# 1. 创建答卷（核心）
def create_answer(
    db: Session,
    req: AnswerCreateRequest,
    user_id: int,
    audio_file: bytes = None,
    audio_format: str = None,
    audio_size: int = None
):
    # 校验问题是否存在且启用
    db_question = db.query(Question).filter(
        and_(Question.id == req.question_id, Question.is_active == True)
    ).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="问题不存在或已禁用")
    
    # 创建答卷对象
    new_answer = Answer(
        user_id=user_id,
        question_id=req.question_id,
        content=req.content,
        audio_file=audio_file,
        audio_format=audio_format,
        audio_size=audio_size,
        is_active=req.is_active if req.is_active is not None else True
    )
    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)
    return new_answer

# 2. 获取当前用户的答卷列表
def get_answer_list_for_user(
    db: Session,
    user_id: int,
    question_id: int = None,
    is_active: bool = None,
    page: int = 1,
    size: int = 10
):
    # 基础查询：仅当前用户的答卷
    query = db.query(Answer).filter(Answer.user_id == user_id)
    
    # 可选筛选：问题ID
    if question_id is not None:
        query = query.filter(Answer.question_id == question_id)
    
    # 可选筛选：是否启用
    if is_active is not None:
        query = query.filter(Answer.is_active == is_active)
    
    # 统计总条数
    total = query.count()
    # 分页查询（按创建时间倒序）
    items = query.order_by(Answer.create_time.desc()).offset((page-1)*size).limit(size).all()
    return {"total": total, "items": items}

# 3. 获取答卷详情
def get_answer_detail(db: Session, answer_id: int):
    db_answer = db.query(Answer).filter(Answer.id == answer_id).first()
    if not db_answer:
        raise HTTPException(status_code=404, detail="答卷不存在")
    return db_answer

# 4. 更新答卷启用状态
def update_answer_status(db: Session, answer_id: int, is_active: bool):
    db_answer = get_answer_detail(db, answer_id)
    db_answer.is_active = is_active
    db.commit()
    db.refresh(db_answer)
    return db_answer

# 5. 更新答卷文本内容
def update_answer_content(db: Session, answer_id: int, content: str):
    db_answer = get_answer_detail(db, answer_id)
    db_answer.content = content
    db.commit()
    db.refresh(db_answer)
    return db_answer