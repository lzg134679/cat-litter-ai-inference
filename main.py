import os
import shutil
from flask import Flask, request, jsonify
from inference import CatLitterInference

app = Flask(__name__)

# 模型路径
DEFAULT_MODEL_PATH = "cat_litter_model_fp32.onnx"
HA_MODEL_DIR = "/config/check_cat_litter_ai/"

# 模型实例
model = None

def initialize_model():
    """初始化模型
    
    检查 HA 目录是否有模型文件，如果有则复制到容器内
    """
    global model
    
    # 检查 HA 目录
    if os.path.exists(HA_MODEL_DIR) and os.path.isdir(HA_MODEL_DIR):
        ha_model_path = os.path.join(HA_MODEL_DIR, DEFAULT_MODEL_PATH)
        if os.path.exists(ha_model_path):
            print(f"🔄 发现 HA 目录中的模型文件，正在复制到容器...")
            shutil.copy2(ha_model_path, DEFAULT_MODEL_PATH)
            print(f"✅ 模型文件已更新")
    else:
        print(f"⚠️ HA 模型目录 {HA_MODEL_DIR} 不存在，使用默认模型")
    
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
    print("🌐 启动 API 服务...")
    app.run(host='0.0.0.0', port=5000, debug=False)
