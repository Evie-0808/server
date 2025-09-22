# 基础镜像：包含 Python 和 Node.js（同时支持前后端）
FROM python:3.9-slim

# 安装 Node.js（用于 Vue 开发服务器）
RUN apt-get update && apt-get install -y curl \
    && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 安装 supervisord（管理多进程）
RUN pip install supervisor

# 设置工作目录
WORKDIR /app

# 复制后端依赖并安装
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制前端依赖并安装（仅安装依赖，代码通过卷挂载同步）
COPY frontend/package.json ./frontend/
WORKDIR /app/frontend
RUN npm install

# 回到工作目录
WORKDIR /app

# 复制 supervisord 配置
COPY supervisord.conf .

# 暴露端口：FastAPI(8000) + Vue 开发服务器(8080)
EXPOSE 8000 8080

# 启动 supervisord 管理前后端服务
CMD ["supervisord", "-c", "supervisord.conf"]