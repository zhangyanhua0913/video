# 🎬 视频混剪工具 v2.0 - OpenClaw Skill 版本

**完整的视频混剪解决方案，支持 OpenClaw 框架调用**

---

## ✨ 核心特性

### 视频编辑
- ✅ 多视频拼接与混剪
- ✅ 6+ 种专业转场效果
- ✅ 自动分辨率缩放

### 高级功能
- ✅ 文字叠加与动态字幕
- ✅ 音频淡入淡出处理
- ✅ 自动颜色校正
- ✅ 视频缩略图生成

### 框架集成
- ✅ **OpenClaw Skill** 完全支持
- ✅ 命令行调用
- ✅ Python API 调用
- ✅ REST API 支持 (可选)

---

## 🚀 3 分钟快速开始

### 方式 1：直接使用 Python

```python
from video_mixer import VideoMixer

mixer = VideoMixer(output_path='output.mp4')
mixer.add_clip('video1.mp4')
mixer.add_clip('video2.mp4')
mixer.generate()
```

### 方式 2：使用 OpenClaw Skill Handler

```python
from skill_handler import VideoMixerSkillHandler

handler = VideoMixerSkillHandler()
result = handler.process('mix', {
    'output': 'output.mp4',
    'clips': [
        {'path': 'video1.mp4'},
        {'path': 'video2.mp4'}
    ]
})
print(result.to_json())
```

### 方式 3：通过 OpenClaw 框架

```bash
# 安装 OpenClaw
pip install openclaw

# 注册 skill
openclaw skill register --name video-mixer --path /path/to/goEditVideo

# 调用 skill
openclaw skill call video-mixer mix \
  --output "output.mp4" \
  --clips '[{"path":"video1.mp4"},{"path":"video2.mp4"}]'
```

---

## 📁 项目结构

```
e:\goEditVideo\
│
├── 🔧 核心工具
│   ├── video_mixer.py           主要混剪工具类
│   ├── skill_handler.py         OpenClaw Skill 处理器
│   └── skill.yml                Skill 配置定义
│
├── 📖 文档 (必读)
│   ├── README.md                完整功能文档
│   ├── QUICKSTART.md            5分钟快速指南
│   ├── FILE_GUIDE.md            文件导航
│   ├── OPENCLAW_GUIDE.md        OpenClaw 安装使用
│   └── SETUP_COMPLETE.txt       安装完成说明
│
├── 📝 示例代码
│   ├── example_usage.py         基础示例 (5个)
│   ├── advanced_examples.py     高级示例 (7个)
│   └── openclaw_examples.py     OpenClaw 示例 (6个)
│
├── 🧪 测试
│   └── test_skill.py            自动化测试脚本
│
└── ⚙️ 配置文件
    ├── config_template.json     配置文件模板
    └── requirements.txt         依赖列表
```

---

## 📚 文档导航

| 文档 | 适用场景 | 快速链接 |
|------|---------|---------|
| **QUICKSTART.md** | 新用户、快速上手 | [快速开始](QUICKSTART.md) |
| **README.md** | 完整 API 文档、详细示例 | [完整文档](README.md) |
| **OPENCLAW_GUIDE.md** | 安装 OpenClaw、框架集成 | [OpenClaw](OPENCLAW_GUIDE.md) |
| **FILE_GUIDE.md** | 文件说明、项目结构 | [文件导航](FILE_GUIDE.md) |

---

## 🎯 使用场景

### 场景 1：快速混剪视频

```python
# 基础用法，无需配置
mixer = VideoMixer()
for video_file in ['clip1.mp4', 'clip2.mp4', 'clip3.mp4']:
    mixer.add_clip(video_file, transition='fade')
mixer.generate()
```

### 场景 2：创建 YouTube 视频

```python
# 带文字、音效、色彩处理
mixer = VideoMixer()
mixer.add_clip('intro.mp4')
mixer.add_text_overlay('欢迎订阅', fontsize=48)
mixer.set_audio_fade(fade_in=1.0, fade_out=1.5)
mixer.enable_color_correction(contrast=1.2)
mixer.generate()
mixer.generate_thumbnail('thumb.jpg')
```

### 场景 3：批量处理 (通过 OpenClaw)

```bash
# 使用 Skill 处理多个任务
for video in videos/*.mp4; do
  openclaw skill call video-mixer mix \
    --output "processed/$video" \
    --clips "[{\"path\":\"$video\"}]"
done
```

---

## 🔧 Skill 命令参考

### 1. `mix` - 混剪视频

**必需参数:**
- `output` (string): 输出路径
- `clips` (array): 视频片段列表

**可选参数:**
- `resolution` [宽, 高] - 默认 [1920, 1080]
- `textOverlays` - 文字叠加
- `audioFadeIn` / `audioFadeOut` - 音频淡出
- `colorCorrection` - 颜色校正

### 2. `thumbnail` - 生成缩略图

**必需参数:**
- `videoPath` - 视频路径
- `output` - 输出路径

**可选参数:**
- `timestamp` - 截图时间
- `width` - 缩略图宽度

### 3. `listTransitions` - 获取转场列表

**无参数** - 返回所有支持的转场效果

---

## 💻 系统要求

- **Python**: 3.6+
- **FFmpeg**: 4.0+ (系统级)
- **操作系统**: Windows / macOS / Linux

### 安装依赖

```bash
# 安装 FFmpeg
choco install ffmpeg          # Windows
brew install ffmpeg           # macOS
sudo apt-get install ffmpeg   # Linux

# 验证安装
ffmpeg -version
```

---

## ✅ 功能清单

### 基础混剪
- [x] 多视频拼接
- [x] 自动分辨率缩放
- [x] 6+ 种转场效果

### 高级功能
- [x] 文字叠加
- [x] 音频淡出
- [x] 颜色校正
- [x] 缩略图生成

### 框架集成
- [x] OpenClaw Skill
- [x] 参数验证
- [x] 错误处理
- [x] 响应格式

### 文档和示例
- [x] 完整 API 文档
- [x] 5+ 个基础示例
- [x] 7+ 个高级示例
- [x] 6+ 个 OpenClaw 示例

### 测试和验证
- [x] 单元测试
- [x] 参数验证
- [x] 自动化测试脚本

---

## 🎬 转场效果

| 效果 | 名称 | 用途 |
|------|------|------|
| `fade` | 淡入淡出 | 通用过渡 |
| `wipeleft` | 左滑过渡 | 动态切换 |
| `wiperight` | 右滑过渡 | 动态切换 |
| `zoomin` | 缩放进入 | 聚焦效果 |
| `circleopen` | 圆形展开 | 创意转场 |
| `pixelize` | 像素化 | 特殊效果 |

---

## 📊 性能指标

| 项目 | 数值 |
|------|------|
| 代码行数 | ~800 行 (核心) |
| 支持命令 | 5 个 |
| 支持转场 | 6+ 种 |
| 文档页数 | 8+ 份 |
| 示例代码 | 18+ 个 |

---

## 🚀 安装 OpenClaw

### 标准安装

```bash
pip install openclaw
```

### 验证安装

```bash
openclaw --version
openclaw skill register --name video-mixer --path /path/to/goEditVideo
openclaw skill list
```

---

## 📝 版本信息

- **版本**: 2.0.0
- **发布日期**: 2026年3月24日
- **OpenClaw 兼容**: ✓ 是
- **Python 版本**: 3.6+

### 版本历史

| 版本 | 日期 | 更新 |
|------|------|------|
| 2.0.0 | 2026-03-24 | 添加 OpenClaw Skill 支持、文字、音频、颜色处理 |
| 1.0.0 | 2024-XX-XX | 初版发布，基础混剪功能 |

---

## 🤝 贡献

欢迎改进和反馈！

---

## 📄 许可证

MIT License

---

## 🎓 快速导航

### 我想...

**...快速开始**
→ 查看 [QUICKSTART.md](QUICKSTART.md)

**...完全了解 API**
→ 查看 [README.md](README.md)

**...使用 OpenClaw**
→ 查看 [OPENCLAW_GUIDE.md](OPENCLAW_GUIDE.md)

**...查找具体示例**
→ 查看 [FILE_GUIDE.md](FILE_GUIDE.md)

**...运行测试**
→ 执行 `python test_skill.py --all`

---

## ☎️ 获取帮助

### 常见问题

1. **"FFmpeg 未找到"**
   → 确保 FFmpeg 已安装并在 PATH 中

2. **"Skill 未找到"**
   → 检查 Skill 是否已注册: `openclaw skill list`

3. **"参数错误"**
   → 检查 JSON 格式，使用在线验证工具

### 文档查询

- 快速问题 → [QUICKSTART.md](QUICKSTART.md)
- 技术问题 → [README.md](README.md#常见问题)
- 框架问题 → [OPENCLAW_GUIDE.md](OPENCLAW_GUIDE.md)

---

## 🌟 特色功能

### 智能颜色校正
```python
mixer.enable_color_correction(
    brightness=0.1,    # 增加亮度
    contrast=1.2,      # 增加对比度
    saturation=1.1,    # 增加饱和度
    gamma=1.05         # 微调 gamma
)
```

### 动态文字叠加
```python
mixer.add_text_overlay(
    '精彩内容',
    start_time=2,      # 开始时间
    duration=3,        # 持续时间
    fontsize=48,       # 字体大小
    fontcolor='white', # 字体颜色
    x='center',        # 水平位置
    y='top'            # 垂直位置
)
```

### 音频处理
```python
mixer.set_audio_fade(
    fade_in=1.5,   # 前 1.5 秒淡入
    fade_out=2.0   # 后 2 秒淡出
)
```

---

## 🎉 开始使用！

```bash
# 1. 安装 FFmpeg
# (参考上面的系统要求)

# 2. 运行示例
python example_usage.py

# 3. 尝试高级示例
python advanced_examples.py

# 4. 测试 OpenClaw Skill
python test_skill.py --all

# 5. 使用 OpenClaw
pip install openclaw
openclaw skill register --name video-mixer --path $(pwd)
openclaw skill call video-mixer listTransitions
```

---

**祝你视频编辑愉快！🎬✨**

有任何问题，请查阅相应的文档。
