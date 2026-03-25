#!/usr/bin/env python3
"""
OpenClaw 视频混剪 Skill 完整示例
展示如何通过 OpenClaw 调用视频混剪工具
"""

import json
import sys
from skill_handler import VideoMixerSkillHandler


def example_1_basic_mixing():
    """例子 1: 基础混剪"""
    print("\n" + "="*70)
    print("例子 1: 基础混剪")
    print("="*70)
    
    handler = VideoMixerSkillHandler()
    
    params = {
        'output': 'example1_output.mp4',
        'clips': [
            {
                'path': 'video1.mp4',
                'transition': 'fade',
                'transitionDuration': 1.0
            },
            {
                'path': 'video2.mp4',
                'transition': 'wipeleft',
                'transitionDuration': 1.5
            },
            {
                'path': 'video3.mp4',
                'transition': 'zoomin',
                'transitionDuration': 1.0
            }
        ]
    }
    
    print("\n命令: mix")
    print(f"参数:\n{json.dumps(params, ensure_ascii=False, indent=2)}")
    
    response = handler.process('mix', params)
    
    print(f"\n响应:\n{response.to_json()}")
    print(f"\n状态: {'✓ 成功' if response.success else '✗ 失败'}")
    
    return response.success


def example_2_with_text_overlay():
    """例子 2: 带文字叠加的混剪"""
    print("\n" + "="*70)
    print("例子 2: 带文字叠加的混剪")
    print("="*70)
    
    handler = VideoMixerSkillHandler()
    
    params = {
        'output': 'example2_output.mp4',
        'resolution': [1920, 1080],
        'clips': [
            {
                'path': 'video1.mp4',
                'transition': 'fade',
                'transitionDuration': 1.0
            },
            {
                'path': 'video2.mp4',
                'transition': 'wipeleft',
                'transitionDuration': 1.5
            }
        ],
        'textOverlays': [
            {
                'text': '欢迎观看',
                'startTime': 0,
                'duration': 3,
                'fontsize': 48,
                'fontcolor': 'white',
                'x': 'center',
                'y': 'center'
            },
            {
                'text': '感谢订阅！',
                'startTime': 5,
                'duration': 2,
                'fontsize': 36,
                'fontcolor': 'yellow',
                'x': 'center',
                'y': 'bottom'
            }
        ]
    }
    
    print("\n命令: mix")
    print(f"参数:\n{json.dumps(params, ensure_ascii=False, indent=2)}")
    
    response = handler.process('mix', params)
    
    print(f"\n响应:\n{response.to_json()}")
    print(f"\n状态: {'✓ 成功' if response.success else '✗ 失败'}")
    
    return response.success


def example_3_full_features():
    """例子 3: 使用所有功能的完整示例"""
    print("\n" + "="*70)
    print("例子 3: 完整功能示例")
    print("="*70)
    
    handler = VideoMixerSkillHandler()
    
    params = {
        'output': 'example3_output.mp4',
        'resolution': [1920, 1080],
        'clips': [
            {
                'path': 'video1.mp4',
                'transition': 'fade',
                'transitionDuration': 1.0
            },
            {
                'path': 'video2.mp4',
                'transition': 'wipeleft',
                'transitionDuration': 1.5
            },
            {
                'path': 'video3.mp4',
                'transition': 'circleopen',
                'transitionDuration': 1.2
            },
            {
                'path': 'video4.mp4',
                'transition': 'zoomin',
                'transitionDuration': 1.0
            }
        ],
        'textOverlays': [
            {
                'text': '标题：精彩混剪',
                'startTime': 0,
                'duration': 4,
                'fontsize': 56,
                'fontcolor': 'white',
                'x': 'center',
                'y': 'top'
            },
            {
                'text': '第一部分',
                'startTime': 1,
                'duration': 3,
                'fontsize': 36,
                'fontcolor': 'yellow',
                'x': 'left',
                'y': 'center'
            },
            {
                'text': '字幕：精彩继续...',
                'startTime': 7,
                'duration': 5,
                'fontsize': 28,
                'fontcolor': 'white',
                'x': 'center',
                'y': 'bottom'
            },
            {
                'text': '结束感谢观看！',
                'startTime': 10,
                'duration': 3,
                'fontsize': 48,
                'fontcolor': 'lime',
                'x': 'center',
                'y': 'center'
            }
        ],
        'audioFadeIn': 1.5,
        'audioFadeOut': 2.0,
        'colorCorrection': {
            'enabled': True,
            'brightness': 0.1,
            'contrast': 1.25,
            'saturation': 1.15,
            'gamma': 1.05
        }
    }
    
    print("\n命令: mix")
    print(f"参数:\n{json.dumps(params, ensure_ascii=False, indent=2)}")
    
    response = handler.process('mix', params)
    
    print(f"\n响应:\n{response.to_json()}")
    print(f"\n状态: {'✓ 成功' if response.success else '✗ 失败'}")
    
    return response.success


def example_4_thumbnail():
    """例子 4: 生成缩略图"""
    print("\n" + "="*70)
    print("例子 4: 生成缩略图")
    print("="*70)
    
    handler = VideoMixerSkillHandler()
    
    params = {
        'videoPath': 'example3_output.mp4',
        'output': 'example3_thumbnail.jpg',
        'timestamp': 5,
        'width': 320
    }
    
    print("\n命令: thumbnail")
    print(f"参数:\n{json.dumps(params, ensure_ascii=False, indent=2)}")
    
    response = handler.process('thumbnail', params)
    
    print(f"\n响应:\n{response.to_json()}")
    print(f"\n状态: {'✓ 成功' if response.success else '✗ 失败'}")
    
    return response.success


def example_5_list_transitions():
    """例子 5: 获取转场效果列表"""
    print("\n" + "="*70)
    print("例子 5: 获取转场效果列表")
    print("="*70)
    
    handler = VideoMixerSkillHandler()
    
    print("\n命令: listTransitions")
    print("参数: 无")
    
    response = handler.process('listTransitions', {})
    
    print(f"\n响应:\n{response.to_json()}")
    print(f"\n状态: {'✓ 成功' if response.success else '✗ 失败'}")
    
    return response.success


def example_6_save_and_load_config():
    """例子 6: 保存和加载配置"""
    print("\n" + "="*70)
    print("例子 6: 保存和加载配置")
    print("="*70)
    
    handler = VideoMixerSkillHandler()
    
    # 保存配置
    print("\n--- 保存配置 ---")
    
    config = {
        'resolution': [1920, 1080],
        'output_path': 'saved_config_output.mp4',
        'clips': [
            {
                'path': 'video1.mp4',
                'transition': 'fade',
                'transitionDuration': 1.0
            },
            {
                'path': 'video2.mp4',
                'transition': 'wipeleft',
                'transitionDuration': 1.5
            }
        ],
        'textOverlays': [
            {
                'text': '保存的配置',
                'startTime': 0,
                'duration': 3,
                'fontsize': 48
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
    }
    
    save_params = {
        'config': config,
        'output': 'example_config.json'
    }
    
    print(f"保存到: example_config.json")
    save_response = handler.process('saveConfig', save_params)
    print(f"结果: {'✓ 成功' if save_response.success else '✗ 失败'}")
    
    # 加载配置
    print("\n--- 加载配置 ---")
    
    load_params = {
        'configPath': 'example_config.json'
    }
    
    print(f"从: example_config.json")
    load_response = handler.process('loadConfig', load_params)
    
    if load_response.success:
        print("✓ 配置加载成功")
        print(f"加载的配置:\n{json.dumps(load_response.output, ensure_ascii=False, indent=2)}")
    else:
        print(f"✗ 加载失败: {load_response.message}")
    
    return save_response.success and load_response.success


def main():
    """主函数"""
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║         OpenClaw 视频混剪 Skill 完整示例                        ║")
    print("║         Video Mixer Skill Complete Examples                  ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")
    
    print("注意: 这些示例展示如何调用 skill，但需要真实的视频文件才能实际执行。")
    print("如果你没有视频文件，可以查看输出中的命令和参数格式。\n")
    
    results = {}
    
    # 运行示例
    results['基础混剪'] = example_1_basic_mixing()
    results['文字叠加'] = example_2_with_text_overlay()
    results['完整功能'] = example_3_full_features()
    results['缩略图'] = example_4_thumbnail()
    results['转场列表'] = example_5_list_transitions()
    results['配置管理'] = example_6_save_and_load_config()
    
    # 显示总结
    print("\n" + "="*70)
    print("示例执行总结")
    print("="*70)
    
    for example_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {example_name:20} {status}")
    
    print("\n" + "="*70)
    print("提示:")
    print("- 上面的示例展示了如何通过 OpenClaw 调用各个命令")
    print("- 如果有真实的视频文件，可以修改参数并实际运行")
    print("- 查看 OPENCLAW_GUIDE.md 了解如何安装和使用 OpenClaw")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
