# 【文件位置：项目根目录/Dockerfile】
FROM python:3.10-slim

WORKDIR /app

# 第一步：先更新pip（可选，消除提示）
RUN pip install --no-cache-dir --upgrade pip

# 第二步：安装最新版Poetry
RUN pip install --no-cache-dir poetry==1.8.3

# 第三步：配置Poetry不创建虚拟环境
RUN poetry config virtualenvs.create false

# 第四步：复制项目所有代码（包含app目录）
COPY . .

# 第五步：安装生产依赖（此时app目录已存在，可以打包）
RUN poetry install --without dev --no-interaction --no-ansi

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]