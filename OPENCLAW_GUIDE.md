# OpenClaw Skill 安装和使用指南

## 📦 什么是 OpenClaw？

OpenClaw 是一个强大的技能(Skill)管理框架，用于调用和管理各种工具和服务。本指南将帮助你安装 OpenClaw 并集成视频混剪工具作为一个 Skill。

---

## 🚀 安装步骤

### 1. 安装 OpenClaw

#### 使用 pip 安装（推荐）

```bash
pip install openclaw
```

#### 或从源码安装

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pip install -e .
```

#### 验证安装

```bash
openclaw --version
```

### 2. 安装依赖

#### 系统依赖

```bash
# Windows (使用 Chocolatey)
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt-get install ffmpeg ffprobe
```

#### Python 依赖（可选）

视频混剪工具本身没有额外的 Python 依赖，但推荐安装：

```bash
pip install python-json-logger  # 用于日志记录
```

### 3. 注册 Skill

OpenClaw 需要知道你的 Skill 在哪里。有两种方式：

#### 方式 1：使用 Skill 目录（推荐）

```bash
# 在 OpenClaw 的 skills 目录中创建符号链接
openclaw skill register --name video-mixer --path /path/to/goEditVideo
```

#### 方式 2：手动配置

编辑 `~/.openclaw/config.yaml` 添加：

```yaml
skills:
  video-mixer:
    path: /path/to/goEditVideo
    enabled: true
    version: 2.0.0
```

### 4. 验证 Skill 注册

```bash
openclaw skill list
openclaw skill info video-mixer
```

---

## 📝 使用方式

### 方式 1：命令行使用

#### 基础混剪

```bash
openclaw skill call video-mixer mix \
  --output "output.mp4" \
  --clips '[{"path":"video1.mp4","transition":"fade"},{"path":"video2.mp4"}]'
```

#### 带文字和效果的混剪

```bash
openclaw skill call video-mixer mix \
  --output "output.mp4" \
  --clips '[{"path":"video1.mp4"},{"path":"video2.mp4"}]' \
  --textOverlays '[{"text":"欢迎","startTime":0,"duration":3}]' \
  --audioFadeIn 1.0 \
  --audioFadeOut 2.0
```

#### 生成缩略图

```bash
openclaw skill call video-mixer thumbnail \
  --videoPath "output.mp4" \
  --output "thumb.jpg" \
  --timestamp 5
```

#### 获取转场列表

```bash
openclaw skill call video-mixer listTransitions
```

### 方式 2：Python API 使用

#### 创建 `openclaw_example.py`

```python
from openclaw import SkillManager

# 初始化技能管理器
skill_manager = SkillManager()

# 加载 video-mixer skill
skill = skill_manager.get_skill('video-mixer')

# 基础混剪
result = skill.call('mix', {
    'output': 'output.mp4',
    'clips': [
        {'path': 'video1.mp4', 'transition': 'fade'},
        {'path': 'video2.mp4', 'transition': 'wipeleft'}
    ]
})

print(f"成功: {result['success']}")
print(f"消息: {result['message']}")
print(f"输出: {result['output']}")
```

#### 带文字和效果

```python
result = skill.call('mix', {
    'output': 'video_with_effects.mp4',
    'clips': [
        {'path': 'video1.mp4'},
        {'path': 'video2.mp4'}
    ],
    'textOverlays': [
        {
            'text': '欢迎',
            'startTime': 0,
            'duration': 3,
            'fontsize': 48,
            'fontcolor': 'white'
        }
    ],
    'audioFadeIn': 1.0,
    'audioFadeOut': 2.0,
    'colorCorrection': {
        'enabled': True,
        'brightness': 0.1,
        'contrast': 1.2,
        'saturation': 1.1
    }
})
```

#### 生成缩略图

```python
result = skill.call('thumbnail', {
    'videoPath': 'output.mp4',
    'output': 'thumbnail.jpg',
    'timestamp': 5
})
```

### 方式 3：REST API 使用

如果 OpenClaw 运行了 API 服务器：

```bash
# 启动 API 服务器
openclaw server start --port 8000
```

然后使用 HTTP 请求：

```python
import requests

# 混剪视频
response = requests.post('http://localhost:8000/api/v1/video-mixer/mix', json={
    'output': 'output.mp4',
    'clips': [
        {'path': 'video1.mp4'},
        {'path': 'video2.mp4'}
    ]
})

print(response.json())
```

或使用 curl：

```bash
curl -X POST http://localhost:8000/api/v1/video-mixer/mix \
  -H "Content-Type: application/json" \
  -d '{
    "output": "output.mp4",
    "clips": [
      {"path": "video1.mp4"},
      {"path": "video2.mp4"}
    ]
  }'
```

---

## 🔧 Skill 文件说明

```
e:\goEditVideo\
├── skill.yml                    # Skill 定义文件
├── skill_handler.py             # Skill 执行处理程序
├── video_mixer.py               # 核心工具类
├── example_usage.py             # 基础示例
├── advanced_examples.py         # 高级示例
└── README.md                    # 文档
```

### skill.yml

定义 Skill 的元数据、命令、参数等：
- `commands`: 支持的命令列表
- `parameters`: 各命令的参数定义
- `output`: 输出格式
- `examples`: 使用示例

### skill_handler.py

实现了 Skill 的执行逻辑：
- `VideoMixerSkillHandler`: 主处理类
- `SkillResponse`: 响应格式类
- 各命令的处理方法

---

## 📚 命令参考

### mix 命令

混剪多个视频片段。

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| output | string | ✓ | 输出视频路径 |
| clips | array | ✓ | 视频片段列表 |
| resolution | array | | 输出分辨率 [宽, 高]，默认 [1920, 1080] |
| textOverlays | array | | 文字叠加列表 |
| audioFadeIn | number | | 音频淡入时长（秒） |
| audioFadeOut | number | | 音频淡出时长（秒） |
| colorCorrection | object | | 颜色校正参数 |

**示例：**

```json
{
  "output": "output.mp4",
  "clips": [
    {
      "path": "video1.mp4",
      "transition": "fade",
      "transitionDuration": 1.0
    },
    {
      "path": "video2.mp4",
      "transition": "wipeleft",
      "transitionDuration": 1.5
    }
  ],
  "resolution": [1920, 1080],
  "audioFadeIn": 1.0,
  "audioFadeOut": 2.0
}
```

### thumbnail 命令

生成视频缩略图。

**参数：**

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| videoPath | string | ✓ | 视频文件路径 |
| output | string | ✓ | 输出缩略图路径 |
| timestamp | number | | 截图时间点（秒） |
| width | integer | | 缩略图宽度，默认 320 |

### listTransitions 命令

获取所有支持的转场效果。

**返回：**

```json
{
  "success": true,
  "output": [
    {"name": "fade", "description": "淡入淡出"},
    {"name": "wipeleft", "description": "从左向右划过"},
    ...
  ]
}
```

---

## 🎯 实践示例

### 例 1：创建 YouTube 视频

```python
from openclaw import SkillManager

skill_manager = SkillManager()
skill = skill_manager.get_skill('video-mixer')

result = skill.call('mix', {
    'output': 'youtube_video.mp4',
    'resolution': [1920, 1080],
    'clips': [
        {'path': 'intro.mp4', 'transition': 'fade', 'transitionDuration': 1.0},
        {'path': 'content.mp4', 'transition': 'wipeleft', 'transitionDuration': 1.0},
        {'path': 'outro.mp4', 'transition': 'fade', 'transitionDuration': 1.0}
    ],
    'textOverlays': [
        {
            'text': '🎬 欢迎订阅',
            'startTime': 0,
            'duration': 3,
            'fontsize': 48,
            'fontcolor': 'white'
        },
        {
            'text': '❤ 点赞和订阅',
            'startTime': 8,
            'duration': 2,
            'fontsize': 36,
            'fontcolor': 'red',
            'y': 'bottom'
        }
    ],
    'audioFadeIn': 1.0,
    'audioFadeOut': 1.5,
    'colorCorrection': {
        'enabled': True,
        'brightness': 0.05,
        'contrast': 1.2,
        'saturation': 1.1
    }
})

if result['success']:
    print(f"视频已生成: {result['output']}")
    
    # 生成缩略图
    thumb_result = skill.call('thumbnail', {
        'videoPath': result['output'],
        'output': 'youtube_thumb.jpg',
        'timestamp': 2
    })
    
    print(f"缩略图已生成: {thumb_result['output']}")
```

### 例 2：创建社交媒体视频

```python
result = skill.call('mix', {
    'output': 'social_media.mp4',
    'resolution': [1080, 1920],  # 竖屏
    'clips': [
        {'path': 'clip1.mp4', 'transition': 'fade', 'transitionDuration': 0.5},
        {'path': 'clip2.mp4', 'transition': 'zoomin', 'transitionDuration': 0.5},
        {'path': 'clip3.mp4', 'transition': 'wipeleft', 'transitionDuration': 0.5}
    ],
    'textOverlays': [
        {'text': '快速混剪', 'startTime': 0, 'duration': 1},
        {'text': '点赞👍', 'startTime': 2, 'duration': 1}
    ],
    'audioFadeIn': 0.5,
    'audioFadeOut': 0.5
})
```

---

## 🐛 问题排查

### 问题 1：Skill 未找到

```
Error: Skill 'video-mixer' not found
```

**解决方案：**

```bash
# 重新注册 skill
openclaw skill register --name video-mixer --path /path/to/goEditVideo

# 查看是否注册成功
openclaw skill list
```

### 问题 2：FFmpeg 未找到

```
Error: ffmpeg not found
```

**解决方案：**

确保 FFmpeg 已安装并在 PATH 中：

```bash
which ffmpeg  # Linux/macOS
where ffmpeg  # Windows
```

### 问题 3：参数格式错误

```
Error: Invalid JSON in parameters
```

**解决方案：**

确保参数是正确的 JSON 格式。使用在线 JSON 验证工具检查。

### 问题 4：权限错误

```
Error: Permission denied
```

**解决方案：**

确保输出目录有写入权限：

```bash
chmod 755 /path/to/output/directory  # Linux/macOS
```

---

## 📖 更多资源

- [OpenClaw 官方文档](https://openclaw.dev/)
- [OpenClaw GitHub 仓库](https://github.com/openclaw/)
- [Skill 开发指南](https://openclaw.dev/docs/skill-development)

---

## 🎓 下一步

1. **探索其他 Skills**：`openclaw skill search`
2. **创建自定义 Skill**：查看 Skill 开发指南
3. **集成到应用**：使用 Python API 或 REST API

---

祝你使用愉快！🚀✨
