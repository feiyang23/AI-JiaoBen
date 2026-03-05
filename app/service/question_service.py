# app/service/question_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from sqlalchemy import and_
from app.models.question import Question, question_user_association
from app.models.user import User
from app.schemas.question import QuestionCreateRequest, QuestionAssignUserRequest

# 1. 创建问题（仅创建问题，不分配用户）
def create_question(db: Session, req: QuestionCreateRequest):
    new_question = Question(
        title=req.title,
        description=req.description,
        is_active=req.is_active if req.is_active is not None else True
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

# 2. 分配问题给用户（核心：手动配置哪些用户能看该问题）
def assign_question_to_users(db: Session, req: QuestionAssignUserRequest):
    # 校验问题是否存在
    db_question = db.query(Question).filter(Question.id == req.question_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="问题不存在")
    
    # 校验用户是否存在
    invalid_user_ids = []
    for user_id in req.user_ids:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            invalid_user_ids.append(user_id)
    if invalid_user_ids:
        raise HTTPException(status_code=404, detail=f"用户ID不存在：{invalid_user_ids}")
    
    # 先删除该问题已有的分配记录（可选：覆盖原有分配；如需追加，注释这行）
    db.execute(
        question_user_association.delete().where(
            question_user_association.c.question_id == req.question_id
        )
    )
    
    # 插入新的分配记录（一个问题对应多个用户）
    for user_id in req.user_ids:
        db.execute(
            question_user_association.insert().values(
                question_id=req.question_id,
                user_id=user_id
            )
        )
    db.commit()
    
    # 返回更新后的问题（包含分配的用户）
    return get_question_detail(db, req.question_id)

# 3. 获取当前用户能看到的问题列表（核心：根据中间表查询）
def get_question_list_for_user(db: Session, user_id: int, is_active: bool = None, page: int = 1, size: int = 10):
    # 基础查询：通过中间表关联，只查当前用户能看到的问题
    query = db.query(Question).join(
        question_user_association,
        and_(
            Question.id == question_user_association.c.question_id,
            question_user_association.c.user_id == user_id
        )
    )
    
    # 可选筛选：是否启用
    if is_active is not None:
        query = query.filter(Question.is_active == is_active)
    
    # 统计总条数
    total = query.count()
    # 分页查询（按创建时间倒序）
    items = query.order_by(Question.create_time.desc()).offset((page-1)*size).limit(size).all()
    return {"total": total, "items": items}

# 4. 获取问题详情（包含可查看的用户列表）
def get_question_detail(db: Session, question_id: int):
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if not db_question:
        raise HTTPException(status_code=404, detail="问题不存在")
    return db_question

# 5. 更新问题启用状态
def update_question_status(db: Session, question_id: int, is_active: bool):
    db_question = get_question_detail(db, question_id)
    db_question.is_active = is_active
    db.commit()
    db.refresh(db_question)
    return db_question