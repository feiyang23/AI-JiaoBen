# main.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError  # 导入校验异常类
from app.core.cors import setup_cors
from app.api import user, question, answer  # 新增：导入答卷模块

# 初始化FastAPI
app = FastAPI(
    title="Python后端（Windows11+Poetry+PostgreSQL）",
    version="1.0.0",
    description="基于Windows11、Poetry和PostgreSQL的Python后端服务",
)

# ---------------------- 核心新增：全局校验异常处理器（转中文提示） ----------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # 构建中文错误信息
    chinese_errors = []
    for err in exc.errors():
        # 提取错误位置、类型、参数
        field = err["loc"][-1]  # 取最后一个元素（如password）
        err_type = err["type"]
        ctx = err.get("ctx", {})
        
        # 把英文提示转为中文
        if err_type == "string_too_short":
            msg = f"{field}长度不能少于{ctx['min_length']}位"
        elif err_type == "string_too_long":
            msg = f"{field}长度不能超过{ctx['max_length']}位"
        elif err_type == "field_required":
            msg = f"{field}为必填项"
        elif err_type == "string_pattern_mismatch":
            msg = f"{field}格式错误"
        else:
            msg = f"{field}参数错误：{err['msg']}"  # 兜底提示
        
        chinese_errors.append({
            "field": field,
            "message": msg
        })
    
    # 返回中文错误响应
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": 422,
            "msg": "参数校验失败",
            "data": chinese_errors
        }
    )

# 原有配置（保留）
setup_cors(app)
app.include_router(user.router, prefix="/api/v1/user", tags=["用户模块"])
app.include_router(question.router, prefix="/api/v1/question", tags=["问题模块"])
app.include_router(answer.router, prefix="/api/v1/answer", tags=["答卷模块"])  # 新增：包含答卷路由

@app.get("/")
async def root():
    return {"code": 0, "msg": "服务启动成功", "data": None}