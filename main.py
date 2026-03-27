import os
import shutil
from flask import Flask, request, jsonify

# 模型路径
DEFAULT_MODEL_PATH = "cat_litter_model_fp32.onnx"
HA_MODEL_DIR = "/config/check_cat_litter_ai/"

# 检查 HA 目录是否有模型文件，如果有则复制到容器内
def apply_local_overrides():
    """复制模型文件进容器方便调试"""
    if not os.path.isdir(HA_MODEL_DIR):
        print(f"⚠️ HA 模型目录 {HA_MODEL_DIR} 不存在，使用默认模型")
        return
    
    ha_model_path = os.path.join(HA_MODEL_DIR, DEFAULT_MODEL_PATH)
    if not os.path.exists(ha_model_path):
        print(f"⚠️ HA 模型目录中未找到模型文件，使用默认模型")
        return
    
    print(f"🔄 发现 HA 目录中的模型文件，正在复制到容器...")
    try:
        shutil.copy2(ha_model_path, DEFAULT_MODEL_PATH)
        # 同时复制 .data 文件
        data_file_path = ha_model_path + ".data"
        if os.path.exists(data_file_path):
            shutil.copy2(data_file_path, DEFAULT_MODEL_PATH + ".data")
        print(f"✅ 模型文件已更新")
    except Exception as exc:
        print(f"❌ 复制模型文件失败: {exc}")

# 应用本地覆盖
apply_local_overrides()

# 导入推理模块
from inference import CatLitterInference

app = Flask(__name__)

# 模型实例
model = None

def initialize_model():
    """初始化模型"""
    global model
    
    # 检查模型文件是否存在
    if os.path.exists(DEFAULT_MODEL_PATH):
        try:
            model = CatLitterInference(DEFAULT_MODEL_PATH)
            print(f"✅ 模型加载成功")
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
    else:
        print(f"❌ 模型文件 {DEFAULT_MODEL_PATH} 不存在")

@app.route('/predict', methods=['POST'])
def predict():
    """推理 API 端点
    
    接受 POST 请求，参数为 image_url
    返回推理结果
    """
    if model is None:
        return jsonify({"error": "模型未初始化"}), 500
    
    data = request.json
    if not data or "image_url" not in data:
        return jsonify({"error": "缺少 image_url 参数"}), 400
    
    image_url = data["image_url"]
    result = model.predict(image_url)
    
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    """健康检查端点
    """
    return jsonify({"status": "healthy", "model_loaded": model is not None})

if __name__ == "__main__":
    print("🚀 初始化猫砂盆识别推理服务...")
    initialize_model()
    # 从环境变量中读取端口，默认为5555
    port = int(os.environ.get('PORT', 5555))
    print(f"🌐 启动 API 服务... 端口: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
