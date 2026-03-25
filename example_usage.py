#!/usr/bin/env python3
"""
视频混剪使用示例 - 快速开始指南
"""

from video_mixer import VideoMixer


def example_basic_mixing():
    """基础混剪示例"""
    print("=== 基础混剪示例 ===\n")
    
    # 创建混剪工具，设置输出分辨率为 1920x1080
    mixer = VideoMixer(
        output_path='output_basic.mp4',
        resolution=(1920, 1080)
    )
    
    # 添加视频片段，设置转场效果
    mixer.add_clip(
        'video1.mp4',
        duration=10,  # 可选：指定片段时长(秒)
        transition='fade',  # 淡入淡出
        transition_duration=1.0  # 转场时长 1 秒
    )
    
    mixer.add_clip(
        'video2.mp4',
        transition='wipeleft',  # 从左向右划过
        transition_duration=1.5
    )
    
    mixer.add_clip(
        'video3.mp4',
        transition='zoomin',  # 缩放进入
        transition_duration=1.0
    )
    
    # 生成混剪视频
    # transition_enabled=True: 使用转场效果
    # audio_enabled=True: 保留音频
    mixer.generate(transition_enabled=True, audio_enabled=True)


def example_custom_resolution():
    """自定义分辨率示例"""
    print("=== 自定义分辨率示例 ===\n")
    
    # 创建 1280x720 分辨率的混剪
    mixer = VideoMixer(
        output_path='output_720p.mp4',
        resolution=(1280, 720)
    )
    
    mixer.add_clip('clip1.mp4', transition='pixelize', transition_duration=0.8)
    mixer.add_clip('clip2.mp4', transition='circleopen', transition_duration=1.0)
    
    mixer.generate()


def example_simple_concat():
    """简单拼接示例（无转场）"""
    print("=== 简单拼接示例 ===\n")
    
    mixer = VideoMixer(output_path='output_concat.mp4')
    
    mixer.add_clip('video1.mp4')
    mixer.add_clip('video2.mp4')
    mixer.add_clip('video3.mp4')
    
    # transition_enabled=False: 不使用转场，直接拼接
    mixer.generate(transition_enabled=False, audio_enabled=True)


def example_with_config():
    """保存和加载配置示例"""
    print("=== 配置管理示例 ===\n")
    
    # 创建混剪
    mixer = VideoMixer(output_path='output_with_config.mp4')
    mixer.add_clip('video1.mp4', transition='fade', transition_duration=1.0)
    mixer.add_clip('video2.mp4', transition='wipeleft', transition_duration=1.2)
    
    # 保存配置到 JSON 文件
    mixer.save_config('mixing_config.json')
    
    # 稍后可以从配置文件加载
    # mixer = VideoMixer.load_config('mixing_config.json')
    # mixer.generate()


def example_different_transitions():
    """展示不同转场效果的示例"""
    print("=== 不同转场效果示例 ===\n")
    
    transitions_to_use = [
        ('fade', 1.0),           # 淡入淡出
        ('wipeleft', 1.0),       # 从左向右划过
        ('wiperight', 1.0),      # 从右向左划过
        ('zoomin', 1.2),         # 缩放进入
        ('circleopen', 1.0),     # 圆形展开
        ('pixelize', 0.8),       # 像素化
    ]
    
    mixer = VideoMixer(output_path='output_effects.mp4')
    
    # 添加多个视频片段，每个使用不同的转场
    video_files = ['video1.mp4', 'video2.mp4', 'video3.mp4', 'video4.mp4']
    
    for i, video_file in enumerate(video_files):
        transition_type, duration = transitions_to_use[i % len(transitions_to_use)]
        mixer.add_clip(video_file, transition=transition_type, transition_duration=duration)
    
    mixer.generate()


if __name__ == '__main__':
    """
    运行此脚本前，请确保：
    1. 已安装 FFmpeg 和 FFprobe
    2. 视频文件存在于当前目录或指定正确的路径
    
    快速测试：
    python example_usage.py
    """
    
    # 根据需要取消注释下面的示例
    
    # example_basic_mixing()              # 基础混剪
    # example_custom_resolution()         # 自定义分辨率
    # example_simple_concat()             # 简单拼接
    # example_with_config()               # 配置管理
    # example_different_transitions()     # 不同转场效果
    
    print("\n" + "="*60)
    print("示例脚本已创建！")
    print("="*60)
    print("\n请根据您的需要选择示例，然后：")
    print("1. 修改视频文件路径")
    print("2. 取消注释对应的示例函数")
    print("3. 运行: python example_usage.py\n")
    print("常见命令:")
    print("  python video_mixer.py demo      - 查看演示")
    print("  python video_mixer.py help      - 显示帮助\n")
