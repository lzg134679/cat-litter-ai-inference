import os
import shutil
from flask import Flask, request, jsonify

# 模型路径
DEFAULT_MODEL_PATH = "cat_litter_model_fp32.onnx"
HA_MODEL_DIR = "/config/check_cat_litter_ai/"

# 检查 HA 目录是否有模型文件，如果有则复制到容器内
def apply_local_overrides():
    """复制模型文件进容器方便调试"""
    print(f"🔍 检查 HA 模型目录: {HA_MODEL_DIR}")
    
    # 检查并创建 HA 模型目录
    if not os.path.exists(HA_MODEL_DIR):
        print(f"⚠️ HA 模型目录 {HA_MODEL_DIR} 不存在，正在创建...")
        try:
            os.makedirs(HA_MODEL_DIR, exist_ok=True)
            print(f"✅ HA 模型目录 {HA_MODEL_DIR} 创建成功")
        except Exception as e:
            print(f"❌ 创建 HA 模型目录失败: {e}")
            return
    else:
        print(f"✅ HA 模型目录 {HA_MODEL_DIR} 存在")
    
    # 列出 HA 模型目录下的内容
    try:
        ha_contents = os.listdir(HA_MODEL_DIR)
        print(f"📁 HA 模型目录内容: {ha_contents}")
    except Exception as e:
        print(f"❌ 无法读取 HA 模型目录: {e}")
        return
    
    # 检查并复制模型文件
    model_files = [
        "cat_litter_model_fp32.onnx",
        "cat_litter_model_fp32.onnx.data"
    ]
    
    files_copied = False
    for model_file in model_files:
        ha_file_path = os.path.join(HA_MODEL_DIR, model_file)
        if os.path.exists(ha_file_path):
            print(f"🔄 发现 HA 目录中的文件: {model_file}")
            try:
                shutil.copy2(ha_file_path, model_file)
                print(f"✅ 已复制文件: {ha_file_path} -> {model_file}")
                files_copied = True
            except Exception as e:
                print(f"❌ 复制文件 {model_file} 失败: {e}")
        else:
            print(f"⚠️ HA 模型目录中未找到文件: {model_file}")
    
    if files_copied:
        print(f"✅ 模型文件已更新")
    else:
        print(f"⚠️ 未找到可复制的模型文件")

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
