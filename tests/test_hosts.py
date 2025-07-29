#!/usr/bin/env python3
# -*- coding:utf8 -*-
"""
hosts管理功能测试脚本
"""
import json
import logging
from hosts_manager import HostsManager, GitManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_hosts_manager():
    """测试hosts管理器功能"""
    print("=" * 50)
    print("测试hosts管理器功能")
    print("=" * 50)
    
    # 初始化hosts管理器
    hosts_manager = HostsManager('test_hosts')
    
    # 测试域名列表
    test_domains = [
        "example.com",
        "www.example.com",
        "api.example.com",
        "home.mydomain.com"
    ]
    
    # 创建hosts文件
    print("\n1. 创建初始hosts文件...")
    if hosts_manager.create_hosts_file(test_domains):
        print("✓ hosts文件创建成功")
    else:
        print("✗ hosts文件创建失败")
        return
    
    # 更新IP地址
    test_ip = "192.168.1.100"
    print(f"\n2. 更新hosts文件，设置IP为: {test_ip}")
    if hosts_manager.update_hosts_file(test_ip, test_domains):
        print("✓ hosts文件更新成功")
    else:
        print("✗ hosts文件更新失败")
    
    # 读取当前IP
    print("\n3. 从hosts文件读取当前IP...")
    current_ip = hosts_manager.get_current_ip_from_hosts()
    if current_ip:
        print(f"✓ 当前IP: {current_ip}")
    else:
        print("✗ 无法读取当前IP")
    
    # 测试相同IP更新（应该不会更新）
    print(f"\n4. 尝试用相同IP更新hosts文件: {test_ip}")
    updated = hosts_manager.update_hosts_file(test_ip, test_domains)
    if not updated:
        print("✓ 相同IP跳过更新（正确行为）")
    else:
        print("✗ 相同IP也进行了更新（不应该发生）")
    
    # 测试新IP更新
    new_ip = "192.168.1.200"
    print(f"\n5. 更新hosts文件，设置新IP为: {new_ip}")
    if hosts_manager.update_hosts_file(new_ip, test_domains):
        print("✓ hosts文件更新成功")
    else:
        print("✗ hosts文件更新失败")
    
    # 显示文件内容
    print("\n6. hosts文件内容:")
    try:
        with open('test_hosts', 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
    except Exception as e:
        print(f"✗ 无法读取hosts文件: {e}")

def test_git_manager():
    """测试Git管理器功能"""
    print("\n" + "=" * 50)
    print("测试Git管理器功能")
    print("=" * 50)
    
    git_manager = GitManager()
    
    # 检查是否为Git仓库
    print("\n1. 检查Git仓库状态...")
    if git_manager.is_git_repo():
        print("✓ 当前目录是Git仓库")
    else:
        print("! 当前目录不是Git仓库，将初始化...")
        if git_manager.init_git_repo():
            print("✓ Git仓库初始化成功")
        else:
            print("✗ Git仓库初始化失败")
            return
    
    # 设置Git配置
    print("\n2. 设置Git用户配置...")
    git_manager.set_git_config("Test User", "test@example.com")
    print("✓ Git用户配置已设置")
    
    # 测试添加和提交
    print("\n3. 测试Git添加和提交...")
    commit_message = "Test commit: Add test hosts file"
    if git_manager.add_and_commit('test_hosts', commit_message):
        print("✓ Git提交成功")
    else:
        print("✗ Git提交失败")

def test_integration():
    """测试集成功能"""
    print("\n" + "=" * 50)
    print("测试集成功能")
    print("=" * 50)
    
    # 加载配置
    try:
        with open('router_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        print("✓ 配置文件加载成功")
    except Exception as e:
        print(f"✗ 配置文件加载失败: {e}")
        return
    
    # 显示相关配置
    print(f"Git功能启用: {config.get('git_enabled', False)}")
    print(f"配置的域名: {config.get('domains', [])}")
    print(f"Git用户: {config.get('git_name', 'Unknown')} <{config.get('git_email', 'unknown@example.com')}>")

if __name__ == '__main__':
    try:
        test_hosts_manager()
        test_git_manager()
        test_integration()
        
        print("\n" + "=" * 50)
        print("测试完成！")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
