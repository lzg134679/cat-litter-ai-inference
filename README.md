# 猫砂盆识别推理服务

### 性能考虑

- **CPU 推理**
- **模型选择**：使用 FP32 自训练模型：cat\_litter\_model\_fp32.onnx/cat\_litter\_model\_fp32.onnx.data

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

1. 如果该目录存在且包含 `cat_litter_model_fp32.onnx` 和 `cat_litter_model_fp32.onnx.data` 文件，则复制到容器内使用
2. 如果目录不存在或没有模型文件，则使用容器内的默认模型
3. **使用 API 接口**
   - 使用 `POST http://[hass-ip]:5555/predict` 接口进行推理
   - 发送 JSON 数据：`{"image_url": "http://camera-ip/capture.jpg"}`

## 配置选项

| 选项          | 类型      | 默认值    | 描述                   |
| ----------- | ------- | ------ | -------------------- |
| `log_level` | string  | `info` | 日志级别                 |
| `port`      | integer | `5555` | API服务端口，范围1024-65535 |

## 自动化内使用参考

1. 配置HomeAssistant的`configuration.yaml`，添加以下内容：
```YAML
rest_command:
  cat_litter_inference:
    url: "http://localhost:5555/predict"
    method: POST
    headers:
      content-type: "application/json"
    payload: '{"image_url": "{{ image_url }}"}'
```

2. 自动化中以简单的测试为例子，复制下面配置，以yaml方式添加自动化：
```YAML
alias: 猫砂盆AI识别测试
description: ""
triggers:
  - trigger: event
    event_type: 猫砂盆AI识别测试
actions:
  - variables:
      snapshot_filename: cat_litter_{{ now().strftime('%Y%m%d_%H%M%S') }}.jpg
      ha_host: http://homeassistant.local:8123
  - metadata: {}
    target:
      entity_id: camera.mao_sha_pen（替换成你的猫砂盆摄像头实体ID）
    data:
      filename: /config/www/camera_snapshots/{{ snapshot_filename }}
    action: camera.snapshot
  - delay:
      seconds: 1
  - data:
      image_url: "{{ ha_host }}/local/camera_snapshots/{{ snapshot_filename }}"
    response_variable: response
    action: rest_command.call_cat_litter_ai
  - variables:
      has_cat: "{{ response.content.classes.has_cat.prediction }}"
      no_cat: "{{ response.content.classes.no_cat.prediction }}"
      just_poop: "{{ response.content.classes.just_poop.prediction }}"
      just_pee: "{{ response.content.classes.just_pee.prediction }}"
      cleaning: "{{ response.content.classes.cleaning.prediction }}"
      no_litter: "{{ response.content.classes.no_litter.prediction }}"
      has_cat_probability: "{{ response.content.classes.has_cat.probability }}"
      no_cat_probability: "{{ response.content.classes.no_cat.probability }}"
      just_poop_probability: "{{ response.content.classes.just_poop.probability }}"
      just_pee_probability: "{{ response.content.classes.just_pee.probability }}"
      cleaning_probability: "{{ response.content.classes.cleaning.probability }}"
      no_litter_probability: "{{ response.content.classes.no_litter.probability }}"
  - metadata: {}
    data:
      title: 猫砂盆AI识别结果
      message: |
        快照文件: {{ snapshot_filename }}
        ![猫砂盆实时快照]({{ ha_host }}/local/camera_snapshots/{{ snapshot_filename }})
        识别结果:
        - 有猫: {{ has_cat }} ({{ has_cat_probability }}%)
        - 无猫: {{ no_cat }} ({{ no_cat_probability }}%)
        - 正在排便: {{ just_poop }} ({{ just_poop_probability }}%)
        - 正在排尿: {{ just_pee }} ({{ just_pee_probability }}%)
        - 正在清理: {{ cleaning }} ({{ cleaning_probability }}%)
        - 无猫砂: {{ no_litter }} ({{ no_litter_probability }}%)
    action: persistent_notification.create
```

3.手动运行后会收到HA通知：
![HA通知](https://github.com/lzg134679/cat-litter-ai-inference/blob/main/%E9%80%9A%E7%9F%A5%E9%A2%84%E8%A7%88.png)