import onnxruntime
import numpy as np
from PIL import Image
import requests
from io import BytesIO

class CatLitterInference:
    def __init__(self, model_path):
        """初始化推理模型
        
        Args:
            model_path: ONNX模型文件路径
        """
        self.session = onnxruntime.InferenceSession(model_path)
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name
        self.class_names = ["has_cat", "no_cat", "just_poop", "just_pee", "cleaning", "no_litter"]
    
    def preprocess(self, image):
        """预处理图片
        
        Args:
            image: PIL Image对象
        
        Returns:
            预处理后的numpy数组
        """
        # 调整大小
        image = image.resize((320, 320))
        # 转换为RGB
        image = image.convert('RGB')
        # 转换为numpy数组
        image_array = np.array(image, dtype=np.float32)
        # 归一化
        image_array = image_array / 255.0
        # 标准化
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        image_array = (image_array - mean) / std
        # 调整维度顺序 (H, W, C) -> (C, H, W)
        image_array = np.transpose(image_array, (2, 0, 1))
        # 添加批次维度
        image_array = np.expand_dims(image_array, axis=0)
        # 确保数据类型为float32
        image_array = image_array.astype(np.float32)
        return image_array
    
    def predict(self, image_url):
        """预测图片
        
        Args:
            image_url: 图片URL
        
        Returns:
            预测结果字典
        """
        try:
            # 下载图片
            response = requests.get(image_url)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            
            # 预处理
            input_data = self.preprocess(image)
            
            # 推理
            outputs = self.session.run([self.output_name], {self.input_name: input_data})
            
            # 处理输出
            logits = outputs[0][0]
            
            # 计算概率
            probabilities = 1 / (1 + np.exp(-logits))
            
            # 构建结果
            result = {
                "classes": {}
            }
            
            for i, class_name in enumerate(self.class_names):
                # 将概率乘以100并保留两位小数，避免科学计数法
                prob_value = float(probabilities[i]) * 100
                formatted_prob = round(prob_value, 2)
                
                result["classes"][class_name] = {
                    "probability": formatted_prob,
                    "prediction": bool(probabilities[i] > 0.5)
                }
            
            return result
            
        except Exception as e:
            return {
                "error": str(e)
            }
