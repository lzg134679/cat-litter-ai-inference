FROM python:3.10-slim

# 安装必要的系统库
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . /app

# 设置工作目录
WORKDIR /app

# 安装Python依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 启动命令
CMD ["python3", "main.py"]
