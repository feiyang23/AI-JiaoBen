# app/service/user_service.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.question import Question, question_user_association  # 确保导入正确
from app.schemas.user import UserRegisterRequest, UserLoginRequest
from app.utils.common_util import encrypt_password, check_password
from app.utils.jwt_util import create_access_token
from fastapi import HTTPException

# 用户注册（适配新字段 + 修复变量作用域）
def user_register(db: Session, req: UserRegisterRequest):
    """
    用户注册函数（仅手机号+密码）
    :param db: 数据库会话
    :param req: 注册请求（phone + password）
    :return: 新用户对象
    """
    # 校验手机号是否已注册
    db_user = db.query(User).filter(User.phone == req.phone).first()
    if db_user:
        raise HTTPException(status_code=400, detail="手机号已注册")
    
    # 加密密码
    encrypt_pwd = encrypt_password(req.password)
    
    # 创建用户（仅手机号+密码，其他字段默认）
    new_user = User(
        phone=req.phone,
        password=encrypt_pwd
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # 获取新用户ID

    # ---------------------- 自动分配1、2、3号问题给新用户 ----------------------
    try:
        auto_assign_question_ids = [1, 2, 3]
        valid_question_ids = []
        
        # 校验问题是否存在
        for qid in auto_assign_question_ids:
            exist_question = db.query(Question).filter(Question.id == qid).first()
            if exist_question:
                valid_question_ids.append(qid)
            else:
                print(f"【自动分配失败】问题ID {qid} 不存在，跳过")
        
        # 批量插入关联记录（关键：直接用表对象，避免变量作用域问题）
        if valid_question_ids:
            batch_data = [
                {"question_id": qid, "user_id": new_user.id}
                for qid in valid_question_ids
            ]
            # 直接使用question_user_association.insert()，避免作用域问题
            db.execute(question_user_association.insert(), batch_data)
            db.commit()
            print(f"【自动分配成功】新用户{new_user.id}已分配问题：{valid_question_ids}")
    except Exception as e:
        # 分配失败不影响注册，仅打印日志
        print(f"【自动分配异常】新用户{new_user.id}：{str(e)}")

    return new_user

# 用户登录（逻辑不变）
def user_login(db: Session, req: UserLoginRequest):
    db_user = db.query(User).filter(User.phone == req.phone).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="手机号/密码错误")
    if not check_password(req.password, db_user.password):
        raise HTTPException(status_code=400, detail="手机号/密码错误")
    if not db_user.is_active:
        raise HTTPException(status_code=400, detail="用户被禁用")
    
    token = create_access_token(data={"sub": str(db_user.id)})
    return {
        "user_info": db_user,
        "access_token": token,
        "token_type": "bearer"
    }