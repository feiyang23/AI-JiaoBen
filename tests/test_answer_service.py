# tests/test_answer_service.py
import pytest
from sqlalchemy.orm import Session
from app.service.answer_service import create_answer, get_answer_detail
from app.schemas.answer import AnswerCreateRequest
from app.core.db import SessionLocal, Base, engine

# 测试前置：创建测试表
@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.rollback()
    db.close()

# 测试创建答卷
def test_create_answer_success(db: Session):
    # 前提：存在用户ID=1、问题ID=1（需提前初始化测试数据）
    req = AnswerCreateRequest(
        question_id=1,
        content="测试音频转写文本",
        audio_format="mp3",
        audio_size=1024
    )
    answer = create_answer(db, req, user_id=1)
    assert answer.user_id == 1
    assert answer.question_id == 1
    assert answer.content == "测试音频转写文本"

# 测试获取答卷详情
def test_get_answer_detail(db: Session):
    # 先创建一个答卷
    req = AnswerCreateRequest(question_id=1, content="测试")
    new_answer = create_answer(db, req, user_id=1)
    # 查询详情
    detail = get_answer_detail(db, new_answer.id)
    assert detail.id == new_answer.id
    assert detail.content == "测试"