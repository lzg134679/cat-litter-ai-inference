# 猫砂盆识别推理服务

### 性能考虑

- **CPU 推理**
- **模型选择**：使用 FP32 自训练模型：cat_litter_model_fp32.onnx

## API 接口

### 推理接口

- **URL**: `/predict`
- **方法**: POST
- **参数**: JSON 格式，包含 `image_url` 字段
- **返回**: JSON 格式，包含各分类的概率和预测结果

**请求示例**：
```json
{
  "image_url": "https://example.com/cat_litter.jpg"
}
```

**响应示例**：
```json
{
  "classes": {
    "has_cat": {
      "probability": 95.00,
      "prediction": true
    },
    "no_cat": {
      "probability": 5.55,
      "prediction": false
    },
    "just_poop": {
      "probability": 8.00,
      "prediction": true
    },
    "just_pee": {
      "probability": 1.00,
      "prediction": false
    },
    "cleaning": {
      "probability": 5.05,
      "prediction": false
    },
    "no_litter": {
      "probability": 1.01,
      "prediction": false
    }
  }
}
```

### 健康检查接口

- **URL**: `/health`
- **方法**: GET
- **返回**: JSON 格式，包含服务状态

**响应示例**：
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

## 模型文件管理

服务启动时会检查 Home Assistant 的 `/config/check_cat_litter_ai/` 目录：

1. 如果该目录存在且包含 `cat_litter_model_fp32.onnx` 文件，则复制到容器内使用
2. 如果目录不存在或没有模型文件，则使用容器内的默认模型

6. **使用 API 接口**
   - 使用 `POST http://[hass-ip]:5555/predict` 接口进行推理
   - 发送 JSON 数据：`{"image_url": "http://camera-ip/capture.jpg"}`

## 配置选项

| 选项 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `log_level` | string | `info` | 日志级别 |
| `port` | integer | `5555` | API服务端口，范围1024-65535 |
