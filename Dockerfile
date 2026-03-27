FROM alpine:3.18

# 安装Python和必要的系统库
RUN apk add --no-cache python3 py3-pip python3-dev

# 复制项目文件
COPY . /app

# 设置工作目录
WORKDIR /app

# 安装Python依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 启动命令
CMD ["python3", "main.py"]
