# 视频混剪工具 (Video Mixing Tool)

一个强大的 Python 工具，用于视频混剪、转场效果、文字叠加、音频处理和颜色校正。

## 功能特性

✨ **核心功能**
- 多个视频拼接与混剪
- 丰富的转场效果（6+ 种）
- **新增** 文字叠加与动态字幕
- **新增** 音频淡入淡出效果
- **新增** 自动颜色校正
- **新增** 视频缩略图生成
- 自动视频缩放到统一分辨率
- 配置保存与加载

🎬 **支持的转场效果**
| 转场类型 | 描述 |
|---------|------|
| `fade` | 淡入淡出 |
| `wipeleft` | 从左向右划过 |
| `wiperight` | 从右向左划过 |
| `zoomin` | 缩放进入 |
| `circleopen` | 圆形展开 |
| `pixelize` | 像素化 |

## 系统要求

- Python 3.6+
- FFmpeg 和 FFprobe
- 足够的磁盘空间用于输出视频

### 安装依赖

```bash
# Windows
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt-get install ffmpeg
```

## 快速开始

### 1. 基础使用

```python
from video_mixer import VideoMixer

# 创建混剪工具
mixer = VideoMixer(output_path='output.mp4', resolution=(1920, 1080))

# 添加视频片段
mixer.add_clip('video1.mp4', transition='fade', transition_duration=1.0)
mixer.add_clip('video2.mp4', transition='wipeleft', transition_duration=1.5)
mixer.add_clip('video3.mp4', transition='zoomin', transition_duration=1.0)

# 生成混剪视频
mixer.generate(transition_enabled=True, audio_enabled=True)
```

### 2. 新增功能：文字叠加

```python
mixer = VideoMixer(output_path='video_with_text.mp4')

mixer.add_clip('video1.mp4', transition='fade')
mixer.add_clip('video2.mp4', transition='wipeleft')

# 添加文字叠加
mixer.add_text_overlay(
    '欢迎观看',
    start_time=0,
    duration=3,
    fontsize=48,
    fontcolor='white',
    x='center',  # left, center, right
    y='center'   # top, center, bottom
)

mixer.add_text_overlay(
    '感谢订阅！',
    start_time=5,
    duration=2,
    fontsize=36,
    fontcolor='yellow',
    y='bottom'
)

mixer.generate()
```

### 3. 新增功能：音频淡入淡出

```python
mixer = VideoMixer(output_path='video_with_audio_fade.mp4')

mixer.add_clip('video1.mp4')
mixer.add_clip('video2.mp4')

# 设置音频淡入淡出
mixer.set_audio_fade(
    fade_in=1.5,   # 前 1.5 秒淡入
    fade_out=2.0   # 后 2 秒淡出
)

mixer.generate()
```

### 4. 新增功能：颜色校正

```python
mixer = VideoMixer(output_path='video_corrected.mp4')

mixer.add_clip('video1.mp4')
mixer.add_clip('video2.mp4')

# 启用颜色校正
mixer.enable_color_correction(
    brightness=0.15,   # 亮度增加 15%
    contrast=1.3,      # 对比度增加 30%
    saturation=1.2,    # 饱和度增加 20%
    gamma=1.1          # Gamma 校正
)

mixer.generate()
```

### 5. 新增功能：生成缩略图

```python
mixer = VideoMixer(output_path='my_video.mp4')

mixer.add_clip('video1.mp4')
mixer.add_clip('video2.mp4')

# 生成视频
mixer.generate()

# 生成缩略图（在第 5 秒处）
mixer.generate_thumbnail(
    output_path='thumbnail.jpg',
    timestamp=5,
    width=320  # 缩略图宽度
)
```

### 6. 使用配置文件

```python
from video_mixer import VideoMixer

# 从配置文件加载
mixer = VideoMixer.load_config('config.json')

# 生成视频
mixer.generate()
```

## API 文档

### VideoMixer 类

#### 构造方法

```python
VideoMixer(output_path: str = 'output.mp4', resolution: tuple = (1920, 1080))
```

**参数：**
- `output_path` (str): 输出视频文件路径，默认为 `output.mp4`
- `resolution` (tuple): 输出分辨率 (宽, 高)，默认为 (1920, 1080)

#### 方法

##### add_clip()

```python
add_clip(file_path: str, duration: float = None, 
         transition: str = 'fade', transition_duration: float = 1.0) -> None
```

添加一个视频片段。

**参数：**
- `file_path` (str): **必需** - 视频文件路径
- `duration` (float): 可选 - 片段时长（秒），不指定则使用完整视频
- `transition` (str): 转场效果，默认为 `fade`
- `transition_duration` (float): 转场时长（秒），默认为 1.0

**异常：**
- `FileNotFoundError`: 文件不存在
- `ValueError`: 转场效果不支持

**示例：**
```python
mixer.add_clip('video1.mp4')
mixer.add_clip('video2.mp4', duration=10, transition='wipeleft', transition_duration=1.5)
```

##### add_text_overlay() ⭐ **新增**

```python
add_text_overlay(text: str, start_time: float = 0, duration: float = 5,
                x: str = 'center', y: str = 'center', fontsize: int = 24,
                fontcolor: str = 'white', font_path: str = None) -> None
```

添加文字叠加层。

**参数：**
- `text` (str): **必需** - 显示的文本
- `start_time` (float): 文本开始时间（秒），默认为 0
- `duration` (float): 文本显示时长（秒），默认为 5
- `x` (str): 水平位置 (`left`, `center`, `right` 或像素值)，默认为 `center`
- `y` (str): 垂直位置 (`top`, `center`, `bottom` 或像素值)，默认为 `center`
- `fontsize` (int): 字体大小，默认为 24
- `fontcolor` (str): 字体颜色 (`white`, `black`, `red` 等或 16 进制颜色)，默认为 `white`
- `font_path` (str): 自定义字体文件路径

**示例：**
```python
mixer.add_text_overlay('欢迎', start_time=0, duration=3, fontsize=48)
mixer.add_text_overlay('结束', start_time=10, duration=2, y='bottom', fontcolor='yellow')
```

##### set_audio_fade() ⭐ **新增**

```python
set_audio_fade(fade_in: float = 0, fade_out: float = 0) -> None
```

设置音频淡入淡出效果。

**参数：**
- `fade_in` (float): 音频淡入时长（秒），0 表示不淡入，默认为 0
- `fade_out` (float): 音频淡出时长（秒），0 表示不淡出，默认为 0

**示例：**
```python
mixer.set_audio_fade(fade_in=1.5, fade_out=2.0)
```

##### enable_color_correction() ⭐ **新增**

```python
enable_color_correction(brightness: float = 0, contrast: float = 1,
                       saturation: float = 1, gamma: float = 1) -> None
```

启用自动颜色校正。

**参数：**
- `brightness` (float): 亮度调整，范围 -1.0 到 1.0，默认为 0
- `contrast` (float): 对比度，范围 0.0 到 2.0，默认为 1
- `saturation` (float): 饱和度，范围 0.0 到 2.0，默认为 1
- `gamma` (float): Gamma 校正，范围 0.5 到 2.0，默认为 1

**示例：**
```python
mixer.enable_color_correction(brightness=0.1, contrast=1.2, saturation=1.1)
```

##### generate_thumbnail() ⭐ **新增**

```python
generate_thumbnail(output_path: str = 'thumbnail.jpg', 
                  timestamp: float = None, width: int = 320) -> bool
```

生成视频缩略图。

**参数：**
- `output_path` (str): 缩略图输出路径，默认为 `thumbnail.jpg`
- `timestamp` (float): 截图时间点（秒），默认为视频中间
- `width` (int): 缩略图宽度（像素），默认为 320

**返回值：**
- True: 缩略图生成成功
- False: 缩略图生成失败

**示例：**
```python
mixer.generate_thumbnail('thumb.jpg', timestamp=5, width=320)
```

##### generate()

```python
generate(transition_enabled: bool = True, audio_enabled: bool = True) -> bool
```

生成最终的混剪视频。

**参数：**
- `transition_enabled` (bool): 是否使用转场效果，默认为 True
- `audio_enabled` (bool): 是否保留音频，默认为 True

**返回值：**
- True: 混剪成功
- False: 混剪失败

**示例：**
```python
success = mixer.generate(transition_enabled=True, audio_enabled=True)
if success:
    print("混剪完成！")
```

##### save_config()

```python
save_config(config_path: str) -> None
```

将混剪配置保存为 JSON 文件。

**参数：**
- `config_path` (str): 配置文件保存路径

**示例：**
```python
mixer.save_config('my_mixing_config.json')
```

##### load_config() (类方法)

```python
@classmethod
load_config(cls, config_path: str) -> 'VideoMixer'
```

从 JSON 配置文件加载混剪设置。

**参数：**
- `config_path` (str): 配置文件路径

**返回值：**
- VideoMixer 实例

**示例：**
```python
mixer = VideoMixer.load_config('my_mixing_config.json')
mixer.generate()
```

## 配置文件格式

配置文件采用 JSON 格式，示例如下：

```json
{
  "resolution": [1920, 1080],
  "output_path": "output.mp4",
  "clips": [
    {
      "path": "video1.mp4",
      "duration": null,
      "transition": "fade",
      "transition_duration": 1.0
    },
    {
      "path": "video2.mp4",
      "duration": null,
      "transition": "wipeleft",
      "transition_duration": 1.5
    }
  ],
  "text_overlays": [
    {
      "text": "欢迎观看",
      "start_time": 0,
      "duration": 3,
      "x": "center",
      "y": "center",
      "fontsize": 48,
      "fontcolor": "white",
      "font_path": null
    }
  ],
  "audio_fade_in": 1.0,
  "audio_fade_out": 2.0,
  "color_correction": {
    "enabled": true,
    "brightness": 0.1,
    "contrast": 1.2,
    "saturation": 1.1,
    "gamma": 1.0
  }
}
```

**字段说明：**
- `resolution`: 输出分辨率 [宽, 高]
- `output_path`: 输出视频路径
- `clips`: 视频片段列表
  - `path`: 视频文件路径
  - `duration`: 片段时长（秒），null 表示使用完整视频
  - `transition`: 转场效果
  - `transition_duration`: 转场时长（秒）
- `text_overlays`: 文字叠加列表（新增）
  - `text`: 显示的文本
  - `start_time`: 开始时间（秒）
  - `duration`: 显示时长（秒）
  - `x`, `y`: 位置
  - `fontsize`: 字体大小
  - `fontcolor`: 字体颜色
  - `font_path`: 自定义字体路径
- `audio_fade_in`: 音频淡入时长（秒）（新增）
- `audio_fade_out`: 音频淡出时长（秒）（新增）
- `color_correction`: 颜色校正设置（新增）
  - `enabled`: 是否启用
  - `brightness`: 亮度
  - `contrast`: 对比度
  - `saturation`: 饱和度
  - `gamma`: Gamma 值

## 完整示例

### 示例 1：创建社交媒体视频

```python
from video_mixer import VideoMixer

# 创建适合 TikTok/短视频的竖屏视频
mixer = VideoMixer(
    output_path='social_media.mp4',
    resolution=(1080, 1920)  # 竖屏
)

mixer.add_clip('clip1.mp4', transition='fade', transition_duration=0.5)
mixer.add_clip('clip2.mp4', transition='zoomin', transition_duration=0.7)
mixer.add_clip('clip3.mp4', transition='wipeleft', transition_duration=0.6)

# 添加快速文字
mixer.add_text_overlay('快速混剪', start_time=0, duration=1)
mixer.add_text_overlay('转发点赞 👍', start_time=2, duration=1.5)

mixer.set_audio_fade(fade_in=0.5, fade_out=0.5)
mixer.generate()
```

### 示例 2：电影预告片混剪

```python
mixer = VideoMixer(
    output_path='trailer.mp4',
    resolution=(1920, 1080)
)

# 使用较长的转场时间创建专业效果
clips = [
    ('scene1.mp4', 'fade', 1.5),
    ('scene2.mp4', 'circleopen', 2.0),
    ('scene3.mp4', 'wipeleft', 1.5),
    ('scene4.mp4', 'zoomin', 1.8),
]

for clip_path, transition, duration in clips:
    mixer.add_clip(clip_path, transition=transition, transition_duration=duration)

# 添加标题
mixer.add_text_overlay('即将上映', start_time=0, duration=2, fontsize=56)
mixer.add_text_overlay('敬请期待', start_time=8, duration=2, fontsize=48)

# 颜色校正增强
mixer.enable_color_correction(brightness=0.05, contrast=1.3, saturation=1.2)

mixer.set_audio_fade(fade_in=1.0, fade_out=2.0)
mixer.generate()

# 生成缩略图
mixer.generate_thumbnail('trailer_thumb.jpg', timestamp=3)
```

### 示例 3：YouTube 视频开场

```python
mixer = VideoMixer(output_path='youtube_video.mp4')

mixer.add_clip('intro.mp4', transition='fade', transition_duration=1.0)
mixer.add_clip('content.mp4', transition='wipeleft', transition_duration=1.0)

# 频道标识与字幕
mixer.add_text_overlay(
    '🎬 欢迎来到我的频道',
    start_time=0,
    duration=3,
    fontsize=48,
    x='center',
    y='center'
)

mixer.add_text_overlay(
    '❤ 喜欢记得点赞和订阅！',
    start_time=8,
    duration=2,
    fontsize=36,
    x='center',
    y='bottom',
    fontcolor='red'
)

mixer.set_audio_fade(fade_in=1.0, fade_out=1.5)
mixer.enable_color_correction(brightness=0.05, contrast=1.2, saturation=1.1)
mixer.generate()

# 生成视频封面
mixer.generate_thumbnail('youtube_thumb.jpg', timestamp=2, width=320)
```

### 示例 4：直播回放混剪

```python
# 简单拼接多个直播片段，无转场
mixer = VideoMixer(output_path='livestream_compilation.mp4')

for i in range(1, 6):
    mixer.add_clip(f'stream_part_{i}.mp4')

# 快速处理，无转场
mixer.generate(transition_enabled=False, audio_enabled=True)
```

### 示例 5：完整功能展示

```python
mixer = VideoMixer(output_path='full_feature_demo.mp4', resolution=(1920, 1080))

# 添加视频片段
mixer.add_clip('video1.mp4', transition='fade', transition_duration=1.0)
mixer.add_clip('video2.mp4', transition='wipeleft', transition_duration=1.5)
mixer.add_clip('video3.mp4', transition='circleopen', transition_duration=1.2)

# 添加多个文字叠加
mixer.add_text_overlay('标题', start_time=0, duration=4, fontsize=56)
mixer.add_text_overlay('字幕1', start_time=2, duration=3, fontsize=36, y='bottom')
mixer.add_text_overlay('字幕2', start_time=5, duration=3, fontsize=36, fontcolor='yellow')

# 设置音频效果
mixer.set_audio_fade(fade_in=1.5, fade_out=2.0)

# 启用颜色校正
mixer.enable_color_correction(
    brightness=0.1,
    contrast=1.25,
    saturation=1.15
)

# 生成视频
mixer.generate(transition_enabled=True, audio_enabled=True)

# 生成缩略图
mixer.generate_thumbnail('demo_thumb.jpg', timestamp=3)

# 保存配置
mixer.save_config('demo_config.json')
```

## 常见问题

### Q: 如何获取视频的实际时长？

自动获取。工具会使用 ffprobe 自动检测视频时长。

### Q: 文字颜色有哪些选项？

支持标准颜色名称和十六进制颜色码：
- 标准颜色：`white`, `black`, `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`
- 十六进制：`#FF0000` (红色)、`#00FF00` (绿色) 等

### Q: 如何使用自定义字体？

```python
mixer.add_text_overlay(
    '自定义字体文字',
    font_path='/path/to/font.ttf',
    fontsize=48
)
```

### Q: 如何调整转场的起点？

通过修改 `transition_duration` 和 `duration` 参数调整。转场的开始位置为：
```
offset = duration - transition_duration
```

### Q: 如何处理不同分辨率的视频？

工具会自动缩放所有输入视频到指定的输出分辨率。使用 `resolution` 参数设置目标分辨率。

### Q: 能否保留所有视频的音频？

当前版本使用第一个视频的音频。如需更复杂的音频混音，建议自定义 FFmpeg 滤镜链。

### Q: 文字叠加支持动画吗？

当前版本支持静态文字叠加。可通过调整 `start_time` 和 `duration` 参数创建文字出现和消失的效果。

### Q: 能否使用多种颜色校正？

支持。`enable_color_correction()` 方法可同时调整多个参数：
```python
mixer.enable_color_correction(
    brightness=0.15,
    contrast=1.3,
    saturation=1.2,
    gamma=1.1
)
```

## 命令行使用

```bash
# 显示演示信息
python video_mixer.py demo

# 显示帮助信息
python video_mixer.py help

# 运行示例
python example_usage.py
```

## 性能优化建议

1. **分辨率选择**：
   - 1920x1080: 标准 Full HD
   - 1280x720: 更快的处理速度
   - 3840x2160: 4K（需要更多时间和磁盘空间）

2. **转场时长**：
   - 短转场（0.5-1.0 秒）：快节奏视频
   - 中等转场（1.0-1.5 秒）：标准视频
   - 长转场（2.0+ 秒）：专业/电影级

3. **编码预设**：
   - `ultrafast`: 最快，质量最低
   - `fast`: 快速处理
   - `medium`: 平衡（默认）
   - `slow`: 更好的质量
   - `veryslow`: 最佳质量

## 许可证

MIT License

## 更新日志

### v2.0 (2026) ⭐ **新版本**
- ✨ 添加文字叠加功能
- ✨ 添加音频淡入淡出效果
- ✨ 添加自动颜色校正
- ✨ 添加视频缩略图生成
- 🔧 改进配置文件格式以支持新功能
- 📚 完整的 API 文档和高级示例

### v1.0 (2024)
- ✨ 首个版本发布
- ✨ 支持多视频混剪和转场效果
- ✨ 配置文件支持
- ✨ 自动分辨率缩放

## 反馈与建议

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件
- Pull Request

---

**祝您视频编辑愉快！** 🎬✨
