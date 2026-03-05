# tests/test_user_service.py
import pytest
from sqlalchemy.orm import Session
from app.service.user_service import user_register
from app.schemas.user import UserRegisterRequest
from app.core.db import SessionLocal, Base, engine

# 测试前置：创建测试表
@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.rollback()
    db.close()

# 测试注册成功
def test_user_register_success(db: Session):
    req = UserRegisterRequest(phone="13800138001", password="123456", username="test_win")
    user = user_register(db, req)
    assert user.phone == "13800138001"
    assert user.username == "test_win"

# 测试手机号已注册
def test_user_register_phone_exist(db: Session):
    req = UserRegisterRequest(phone="13800138001", password="123456")
    with pytest.raises(Exception) as excinfo:
        user_register(db, req)
    assert "手机号已注册" in str(excinfo.value)