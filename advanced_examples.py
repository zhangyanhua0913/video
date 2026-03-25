#!/usr/bin/env python3
"""
高级视频混剪示例 - 展示文字、音频、颜色校正和缩略图功能
"""

from video_mixer import VideoMixer


def example_with_text_overlay():
    """包含文字叠加的混剪示例"""
    print("=== 文字叠加示例 ===\n")
    
    mixer = VideoMixer(output_path='output_with_text.mp4')
    
    mixer.add_clip('video1.mp4', transition='fade', transition_duration=1.0)
    mixer.add_clip('video2.mp4', transition='wipeleft', transition_duration=1.5)
    mixer.add_clip('video3.mp4', transition='zoomin', transition_duration=1.0)
    
    # 添加文字叠加
    mixer.add_text_overlay(
        '欢迎观看',
        start_time=0,
        duration=3,
        fontsize=48,
        fontcolor='white',
        x='center',
        y='center'
    )
    
    mixer.add_text_overlay(
        '精彩内容',
        start_time=5,
        duration=3,
        fontsize=36,
        fontcolor='yellow',
        x='center',
        y='top'
    )
    
    mixer.add_text_overlay(
        '感谢观看！',
        start_time=8,
        duration=2,
        fontsize=40,
        fontcolor='white',
        x='center',
        y='bottom'
    )
    
    mixer.generate(transition_enabled=True, audio_enabled=True)


def example_with_audio_fade():
    """包含音频淡入淡出的混剪示例"""
    print("=== 音频淡入淡出示例 ===\n")
    
    mixer = VideoMixer(output_path='output_with_audio_fade.mp4')
    
    mixer.add_clip('video1.mp4', transition='fade', transition_duration=1.0)
    mixer.add_clip('video2.mp4', transition='wipeleft', transition_duration=1.5)
    mixer.add_clip('video3.mp4', transition='zoomin', transition_duration=1.0)
    
    # 设置音频淡入淡出
    mixer.set_audio_fade(
        fade_in=2.0,    # 前 2 秒音频从无到全音量
        fade_out=3.0    # 后 3 秒音频从全音量到无
    )
    
    mixer.generate()


def example_with_color_correction():
    """包含颜色校正的混剪示例"""
    print("=== 颜色校正示例 ===\n")
    
    mixer = VideoMixer(output_path='output_with_color_correction.mp4')
    
    mixer.add_clip('video1.mp4', transition='fade', transition_duration=1.0)
    mixer.add_clip('video2.mp4', transition='wipeleft', transition_duration=1.5)
    mixer.add_clip('video3.mp4', transition='zoomin', transition_duration=1.0)
    
    # 启用颜色校正
    mixer.enable_color_correction(
        brightness=0.15,   # 增加亮度
        contrast=1.3,      # 增加对比度
        saturation=1.2,    # 增加饱和度
        gamma=1.1          # 调整 gamma
    )
    
    mixer.generate()


def example_full_featured():
    """包含所有功能的完整示例"""
    print("=== 完整功能示例 ===\n")
    
    mixer = VideoMixer(output_path='output_full_featured.mp4', resolution=(1920, 1080))
    
    # 添加视频片段
    mixer.add_clip('video1.mp4', transition='fade', transition_duration=1.0)
    mixer.add_clip('video2.mp4', transition='wipeleft', transition_duration=1.5)
    mixer.add_clip('video3.mp4', transition='circleopen', transition_duration=1.2)
    mixer.add_clip('video4.mp4', transition='zoomin', transition_duration=1.0)
    
    # 添加多个文字叠加
    mixer.add_text_overlay(
        '标题：精彩混剪',
        start_time=0,
        duration=4,
        fontsize=56,
        fontcolor='white',
        x='center',
        y='top'
    )
    
    mixer.add_text_overlay(
        '第一部分',
        start_time=1,
        duration=3,
        fontsize=36,
        fontcolor='yellow',
        x='left',
        y='center'
    )
    
    mixer.add_text_overlay(
        '第二部分',
        start_time=4,
        duration=3,
        fontsize=36,
        fontcolor='cyan',
        x='center',
        y='center'
    )
    
    mixer.add_text_overlay(
        '字幕：精彩继续...',
        start_time=7,
        duration=5,
        fontsize=28,
        fontcolor='white',
        x='center',
        y='bottom'
    )
    
    mixer.add_text_overlay(
        '结束感谢观看！',
        start_time=10,
        duration=3,
        fontsize=48,
        fontcolor='lime',
        x='center',
        y='center'
    )
    
    # 设置音频效果
    mixer.set_audio_fade(fade_in=1.5, fade_out=2.0)
    
    # 启用颜色校正
    mixer.enable_color_correction(
        brightness=0.1,
        contrast=1.25,
        saturation=1.15,
        gamma=1.05
    )
    
    # 生成视频
    mixer.generate(transition_enabled=True, audio_enabled=True)
    
    # 生成缩略图
    mixer.generate_thumbnail('output_full_featured_thumb.jpg', timestamp=5)
    
    # 保存配置
    mixer.save_config('full_featured_config.json')


def example_youtube_intro():
    """YouTube 视频开场示例"""
    print("=== YouTube 开场示例 ===\n")
    
    mixer = VideoMixer(output_path='youtube_intro.mp4', resolution=(1920, 1080))
    
    # 开场视频
    mixer.add_clip('intro.mp4', transition='fade', transition_duration=1.0)
    mixer.add_clip('content1.mp4', transition='wipeleft', transition_duration=1.0)
    mixer.add_clip('content2.mp4', transition='fade', transition_duration=1.0)
    
    # 频道标识与字幕
    mixer.add_text_overlay(
        '🎬 欢迎来到我的频道',
        start_time=0,
        duration=3,
        fontsize=48,
        fontcolor='white',
        x='center',
        y='center'
    )
    
    mixer.add_text_overlay(
        '今天分享：视频混剪技巧',
        start_time=2,
        duration=2,
        fontsize=40,
        fontcolor='yellow',
        x='center',
        y='top'
    )
    
    mixer.add_text_overlay(
        '❤ 喜欢记得点赞和订阅！',
        start_time=8,
        duration=2,
        fontsize=36,
        fontcolor='red',
        x='center',
        y='bottom'
    )
    
    # 音频和色彩增强
    mixer.set_audio_fade(fade_in=1.0, fade_out=1.5)
    mixer.enable_color_correction(brightness=0.05, contrast=1.2, saturation=1.1)
    
    mixer.generate()
    
    # 生成缩略图用于视频列表
    mixer.generate_thumbnail('youtube_intro_thumb.jpg', timestamp=2, width=320)


def example_social_media_video():
    """社交媒体竖屏视频示例"""
    print("=== 社交媒体竖屏视频示例 ===\n")
    
    # 竖屏分辨率
    mixer = VideoMixer(output_path='social_media.mp4', resolution=(1080, 1920))
    
    # 添加短片段
    mixer.add_clip('clip1.mp4', transition='fade', transition_duration=0.5)
    mixer.add_clip('clip2.mp4', transition='zoomin', transition_duration=0.5)
    mixer.add_clip('clip3.mp4', transition='wipeleft', transition_duration=0.5)
    mixer.add_clip('clip4.mp4', transition='fade', transition_duration=0.5)
    
    # 快速节奏的文字
    mixer.add_text_overlay('快速混剪', start_time=0, duration=1, fontsize=32)
    mixer.add_text_overlay('多镜头切割', start_time=1, duration=1, fontsize=32)
    mixer.add_text_overlay('音乐同步', start_time=2, duration=1, fontsize=32)
    mixer.add_text_overlay('转发点赞 👍', start_time=3, duration=1.5, fontsize=32)
    
    # 快速音频淡出
    mixer.set_audio_fade(fade_in=0.5, fade_out=0.5)
    
    mixer.generate()


def example_load_and_modify_config():
    """加载配置文件并修改示例"""
    print("=== 配置文件修改示例 ===\n")
    
    # 从现有配置加载
    mixer = VideoMixer.load_config('full_featured_config.json')
    
    # 修改输出路径
    mixer.output_path = 'output_modified.mp4'
    
    # 修改颜色校正参数
    mixer.enable_color_correction(brightness=0.2, contrast=1.3, saturation=1.2)
    
    # 生成新的视频
    mixer.generate()
    
    # 保存修改后的配置
    mixer.save_config('modified_config.json')


if __name__ == '__main__':
    """
    运行此脚本前，请确保：
    1. 已安装 FFmpeg 和 FFprobe
    2. 视频文件存在于当前目录
    3. 已正确安装依赖
    """
    
    print("╔════════════════════════════════════════════════════╗")
    print("║         高级混剪示例 - Advanced Examples           ║")
    print("╚════════════════════════════════════════════════════╝\n")
    
    # 根据需要取消注释下面的示例
    
    # example_with_text_overlay()              # 文字叠加
    # example_with_audio_fade()                # 音频淡出
    # example_with_color_correction()          # 颜色校正
    # example_full_featured()                  # 完整功能
    # example_youtube_intro()                  # YouTube 开场
    # example_social_media_video()             # 社交媒体视频
    # example_load_and_modify_config()         # 配置修改
    
    print("\n高级示例代码已就绪！")
    print("\n使用步骤：")
    print("1. 修改视频文件路径")
    print("2. 取消注释要运行的示例函数")
    print("3. 运行: python advanced_examples.py\n")
    print("示例列表：")
    print("  ✓ example_with_text_overlay()        - 文字叠加")
    print("  ✓ example_with_audio_fade()          - 音频淡入淡出")
    print("  ✓ example_with_color_correction()    - 颜色校正")
    print("  ✓ example_full_featured()            - 完整功能演示")
    print("  ✓ example_youtube_intro()            - YouTube 开场")
    print("  ✓ example_social_media_video()       - 社交媒体视频")
    print("  ✓ example_load_and_modify_config()   - 配置修改\n")
