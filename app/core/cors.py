# app/core/cors.py
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 开发环境，生产改前端域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )