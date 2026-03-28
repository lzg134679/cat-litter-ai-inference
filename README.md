# 猫砂盆识别推理服务

### 部署
1. 本项目用于部署到homeassistant的加载项中（新版本ha内叫“应用”）
2. 需要现在ha的加载项右上角的仓库中添加本项目的地址
3. 安装加载项：Cat Litter AI Inference

### 性能参考

- **CPU 推理**
- **模型选择**：使用 FP32 自训练模型：cat\_litter\_model\_fp32.onnx和cat\_litter\_model\_fp32.onnx.data
- **推理性能消耗**：内存占用约3.55MB，单张图片推理时间约3.5ms（此时间为本地直接推理算出，不包含网络传输时间，实际推理需要先下载图片到内存，因此内存占用与图片大小相关，推理时间也与图片大小和网速相关）

## 使用说明

服务启动时会检查 Home Assistant 的 `/config/check_cat_litter_ai/` 目录：

1. 如果该目录存在且包含 `cat_litter_model_fp32.onnx` 和 `cat_litter_model_fp32.onnx.data` 文件，则复制到容器内使用
2. 如果目录不存在或没有模型文件，则使用容器内的默认模型
3. **使用 API 接口**
   - 使用 `POST http://[homeassistant-ip]:5555/predict` 接口进行推理
   - 发送 JSON 数据：`{"image_url": "http://homeassistant.local:8123/local/camera_snapshots/123456.jpg"}`
   - 下方给出了怎么在 Home Assistant 中使用该接口的示例
4. **分类标签的含义**
   - `has_cat`：有猫
   - `no_cat`： 无猫
   - `just_poop`：刚拉完屎
   - `just_pee`：刚尿完尿
   - `cleaning`：自动清理猫砂
   - `no_litter`：非猫砂盆内视角
   
## 自动化内使用参考

先配置 Home Assistant 的`configuration.yaml`，添加以下内容，实现发送api请求到加载项推理：

```YAML
rest_command:
  cat_litter_inference:
    url: "http://localhost:5555/predict"
    method: POST
    headers:
      content-type: "application/json"
    payload: '{"image_url": "{{ image_url }}"}'
```

自动化中以简单的测试为例子，手动运行后会收到HA通知，需要先在 Home Assistant 的 `/config/www/` 目录新建一个用于存放摄像头快照的文件夹 `camera_snapshots`。再复制下面的YAML配置，添加一条自动化：

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

![自动化发送的通知预览](https://i.cetsteam.com/imgs/2026/03/28/5f67ea5d42f52483.png)

（可选）由于总是需要保存摄像头快照，会导致图片越来越多，因此可以在 Home Assistant 的`configuration.yaml`中添加以下内容：

```YAML
shell_command:
  clean_camera_snapshots: 'find /config/www/camera_snapshots -name "*.jpg" -mtime +90 -delete'
```

（可选）然后在自动化中调用对应动作，实现清理三个月前的快照图片（为了让快照图片可以在近期内访问，因此只清理三个月前的文件）：

```YAML
  - action: shell_command.clean_camera_snapshots
    metadata: {}
    data: {}
```

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

**响应参数含义**：
- `probability`：该分类的置信度概率，范围0-100
- `prediction`：是否预测为该分类，True和False

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
