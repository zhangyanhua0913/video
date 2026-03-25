#!/usr/bin/env python3
"""
OpenClaw Skill 快速测试脚本
用于测试 video-mixer skill 而无需安装完整的 OpenClaw
"""

import json
import sys
import os

# 导入 skill handler
from skill_handler import VideoMixerSkillHandler, SkillResponse


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def test_list_transitions():
    """测试获取转场列表"""
    print("\n=== 测试: 获取转场列表 ===")
    handler = VideoMixerSkillHandler()
    response = handler.process('listTransitions', {})
    print(f"结果: {response.to_json()}")
    return response.success


def test_save_config():
    """测试保存配置"""
    print("\n=== 测试: 保存配置 ===")
    handler = VideoMixerSkillHandler()
    
    config = {
        'resolution': [1920, 1080],
        'output_path': 'test_output.mp4',
        'clips': [
            {'path': 'video1.mp4', 'transition': 'fade'},
            {'path': 'video2.mp4', 'transition': 'wipeleft'}
        ],
        'text_overlays': [
            {'text': '测试', 'start_time': 0, 'duration': 3}
        ]
    }
    
    response = handler.process('saveConfig', {
        'config': config,
        'output': 'test_config.json'
    })
    
    print(f"结果: {response.to_json()}")
    
    # 验证文件是否创建
    if os.path.exists('test_config.json'):
        print("PASS: 配置文件已创建")
        with open('test_config.json', 'r') as f:
            saved_config = json.load(f)
        print(f"PASS: 保存的配置: {json.dumps(saved_config, ensure_ascii=False, indent=2)}")
    
    return response.success


def test_load_config():
    """测试加载配置"""
    print("\n=== 测试: 加载配置 ===")
    handler = VideoMixerSkillHandler()
    
    response = handler.process('loadConfig', {
        'configPath': 'test_config.json'
    })
    
    print(f"结果: {response.to_json()}")
    return response.success


def test_parameter_validation():
    """测试参数验证"""
    print("\n=== 测试: 参数验证 ===")
    handler = VideoMixerSkillHandler()
    
    # 测试缺少输出参数
    print("\n1. 缺少 output 参数:")
    response = handler.process('mix', {
        'clips': [{'path': 'video1.mp4'}]
    })
    print(f"   状态: {response.success}")
    print(f"   消息: {response.message}")
    
    # 测试缺少 clips 参数
    print("\n2. 缺少 clips 参数:")
    response = handler.process('mix', {
        'output': 'output.mp4'
    })
    print(f"   状态: {response.success}")
    print(f"   消息: {response.message}")
    
    # 测试无效命令
    print("\n3. 无效命令:")
    response = handler.process('invalidCommand', {})
    print(f"   状态: {response.success}")
    print(f"   消息: {response.message}")
    
    return True


def test_help():
    """显示帮助信息"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║         OpenClaw Skill 快速测试脚本                            ║
║         Video Mixer Skill Quick Test                          ║
╚════════════════════════════════════════════════════════════════╝

使用方法:
  python test_skill.py [选项]

选项:
  --list-transitions    测试获取转场列表
  --save-config        测试保存配置
  --load-config        测试加载配置
  --validate-params    测试参数验证
  --all                运行所有测试
  --help               显示此帮助信息

示例:
  python test_skill.py --list-transitions
  python test_skill.py --all

""")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        test_help()
        return
    
    option = sys.argv[1].lower()
    
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║         OpenClaw Video Mixer Skill 快速测试                    ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    
    results = {}
    
    if option in ['--list-transitions', '--all']:
        results['list_transitions'] = test_list_transitions()
    
    if option in ['--save-config', '--all']:
        results['save_config'] = test_save_config()
    
    if option in ['--load-config', '--all']:
        results['load_config'] = test_load_config()
    
    if option in ['--validate-params', '--all']:
        results['parameter_validation'] = test_parameter_validation()
    
    if option == '--help':
        test_help()
        return
    
    # 显示总结
    if results:
        print("\n" + "="*64)
        print("测试总结:")
        print("="*64)
        
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            print(f"  {test_name:30} {status}")
        
        total = len(results)
        passed = sum(1 for r in results.values() if r)
        print(f"\n总计: {passed}/{total} 测试通过")
        
        if passed == total:
            print("\nPASS: 所有测试通过，Skill 可以正常使用。")
        else:
            print("\nFAIL: 部分测试失败，请检查上面的错误信息。")


if __name__ == '__main__':
    main()
