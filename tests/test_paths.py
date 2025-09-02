#!/usr/bin/env python3
# -*- coding:utf8 -*-
"""
路径测试脚本
用于验证项目中的路径解析是否正确工作
"""
import sys
import os

# 添加src目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)

try:
    from utils.path_utils import get_project_root, get_absolute_path, ensure_dir_exists
    
    print("="*60)
    print("TP-LINK 路由器监控项目 - 路径测试")
    print("="*60)
    
    print(f"当前工作目录: {os.getcwd()}")
    print(f"项目根目录: {get_project_root()}")
    print()
    
    print("关键文件路径:")
    paths = {
        "配置文件": get_absolute_path('config/router_config.json'),
        "日志文件": get_absolute_path('logs/router_monitor.log'),
        "数据文件": get_absolute_path('data/wan_status_data.json'),
        "hosts文件": get_absolute_path('hosts'),
        "主程序": get_absolute_path('src/main.py'),
    }
    
    for name, path in paths.items():
        exists = "✓" if os.path.exists(path) else "✗"
        print(f"  {name}: {path} {exists}")
    
    print()
    print("测试从不同目录运行程序:")
    
    # 测试目录列表
    test_dirs = [
        project_root,
        os.path.join(project_root, 'src'),
        os.path.join(project_root, 'scripts'),
        '/tmp'
    ]
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            original_cwd = os.getcwd()
            try:
                os.chdir(test_dir)
                resolved_root = get_project_root()
                status = "✓" if resolved_root == get_project_root() else "✗"
                print(f"  从 {test_dir}: {resolved_root} {status}")
            finally:
                os.chdir(original_cwd)
    
    print()
    print("路径解析测试完成！所有路径都应该指向同一个项目根目录。")
    
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保从项目根目录运行此脚本")
except Exception as e:
    print(f"测试过程中发生错误: {e}")
