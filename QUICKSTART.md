# 快速开始指南 - Quick Start Guide

## 🚀 5 分钟快速上手

### 1. 安装依赖

```bash
# 安装 FFmpeg（如果尚未安装）
# Windows
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt-get install ffmpeg
```

### 2. 最简单的例子

创建 `simple_mix.py`：

```python
from video_mixer import VideoMixer

# 创建混剪工具
mixer = VideoMixer(output_path='my_video.mp4')

# 添加视频
mixer.add_clip('video1.mp4')
mixer.add_clip('video2.mp4')
mixer.add_clip('video3.mp4')

# 生成视频
mixer.generate()
```

运行：
```bash
python simple_mix.py
```

---

## 📝 常用功能速查

### 添加转场效果

```python
mixer.add_clip('video1.mp4', transition='fade', transition_duration=1.0)
mixer.add_clip('video2.mp4', transition='wipeleft', transition_duration=1.5)
mixer.add_clip('video3.mp4', transition='zoomin', transition_duration=1.0)
```

**可用转场：** `fade`, `wipeleft`, `wiperight`, `zoomin`, `circleopen`, `pixelize`

### 添加文字

```python
mixer.add_text_overlay('标题文字', start_time=0, duration=3, fontsize=48)
mixer.add_text_overlay('底部字幕', start_time=5, duration=2, y='bottom')
```

### 音频淡出

```python
mixer.set_audio_fade(fade_in=1.0, fade_out=2.0)
```

### 颜色校正

```python
mixer.enable_color_correction(brightness=0.1, contrast=1.2, saturation=1.1)
```

### 生成缩略图

```python
mixer.generate_thumbnail('thumbnail.jpg', timestamp=5)
```

---

## 🎬 场景化模板

### 模板 1：社交媒体视频

```python
from video_mixer import VideoMixer

mixer = VideoMixer(output_path='social.mp4', resolution=(1080, 1920))

mixer.add_clip('clip1.mp4', transition='fade', transition_duration=0.5)
mixer.add_clip('clip2.mp4', transition='zoomin', transition_duration=0.5)

mixer.add_text_overlay('快速混剪', start_time=0, duration=1)
mixer.add_text_overlay('点赞👍', start_time=2, duration=1)

mixer.set_audio_fade(fade_in=0.5, fade_out=0.5)
mixer.generate()
```

### 模板 2：YouTube 视频

```python
mixer = VideoMixer(output_path='youtube.mp4')

mixer.add_clip('intro.mp4', transition='fade')
mixer.add_clip('content.mp4', transition='wipeleft')
mixer.add_clip('outro.mp4', transition='fade')

mixer.add_text_overlay('🎬 欢迎订阅', start_time=0, duration=2, fontsize=48)
mixer.add_text_overlay('❤ 点赞和订阅', start_time=8, duration=2, y='bottom')

mixer.enable_color_correction(brightness=0.05, contrast=1.2)
mixer.set_audio_fade(fade_in=1.0, fade_out=1.5)

mixer.generate()
mixer.generate_thumbnail('thumb.jpg', timestamp=2)
```

### 模板 3：电影预告片

```python
mixer = VideoMixer(output_path='trailer.mp4')

scenes = [
    ('scene1.mp4', 'fade', 1.5),
    ('scene2.mp4', 'circleopen', 2.0),
    ('scene3.mp4', 'wipeleft', 1.5),
]

for path, trans, dur in scenes:
    mixer.add_clip(path, transition=trans, transition_duration=dur)

mixer.add_text_overlay('即将上映', start_time=0, duration=2, fontsize=56)
mixer.enable_color_correction(brightness=0.05, contrast=1.3, saturation=1.2)

mixer.generate()
```

---

## 💾 配置文件方式

### 保存配置

```python
mixer.save_config('my_config.json')
```

### 加载配置并生成

```python
from video_mixer import VideoMixer

mixer = VideoMixer.load_config('my_config.json')
mixer.generate()
```

---

## 🔧 调试与问题排查

### 检查 FFmpeg 是否安装

```bash
ffmpeg -version
ffprobe -version
```

### 查看生成的 FFmpeg 命令

代码会在运行时打印完整的 FFmpeg 命令，可复制到终端直接运行。

### 常见错误

| 错误 | 解决方案 |
|------|--------|
| `ffmpeg not found` | 安装 FFmpeg |
| `FileNotFoundError` | 检查视频文件路径 |
| `Invalid transition` | 检查转场效果名称 |
| `Permission denied` | 检查输出目录权限 |

---

## 📚 更多资源

- **完整文档**：[README.md](README.md)
- **详细示例**：[advanced_examples.py](advanced_examples.py)
- **基础示例**：[example_usage.py](example_usage.py)

---

## ⚡ 性能优化提示

### 处理速度优化

```python
# 1. 降低分辨率（更快）
mixer = VideoMixer(resolution=(1280, 720))

# 2. 缩短转场时长
mixer.add_clip('video.mp4', transition='fade', transition_duration=0.5)

# 3. 禁用不需要的功能
mixer.generate(transition_enabled=False, audio_enabled=False)
```

### 输出质量优化

改 `video_mixer.py` 的 `preset` 参数：
```python
# 在 generate() 方法中
cmd.extend(['-c:v', 'libx264', '-preset', 'slow'])  # slow, medium (default), fast
```

---

## 🎓 学习资源

### FFmpeg 相关

- [FFmpeg 官方文档](https://ffmpeg.org/documentation.html)
- [XFade 滤镜](https://ffmpeg.org/ffmpeg-filters.html#xfade)
- [Drawtext 滤镜](https://ffmpeg.org/ffmpeg-filters.html#drawtext-1)

### 视频剪辑技巧

- 卡点剪辑：与音乐节拍同步
- 蒙太奇：快速切割营造紧张感
- 色彩分级：使用颜色校正统一风格
- 叠化过渡：自然的场景切换

---

## 🎯 下一步

1. **修改示例**：根据你的视频调整路径和参数
2. **尝试不同转场**：`fade`, `wipeleft`, `zoomin` 等
3. **添加文字**：使用 `add_text_overlay()` 添加字幕
4. **保存配置**：用 `save_config()` 保存常用设置

祝你视频编辑愉快！🎬✨
