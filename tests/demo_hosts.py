#!/usr/bin/env python3
# -*- coding:utf8 -*-
"""
hosts管理功能演示脚本
这个脚本模拟IP变化，展示hosts文件更新和Git推送功能
"""
import json
import time
import logging
from hosts_manager import HostsManager, GitManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_config():
    """加载配置文件"""
    try:
        with open('router_config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"加载配置文件失败: {e}")
        return None

def demo_hosts_management():
    """演示hosts管理功能"""
    print("=" * 60)
    print("Hosts管理功能演示")
    print("=" * 60)
    
    # 加载配置
    config = load_config()
    if not config:
        print("❌ 无法加载配置文件")
        return
    
    print(f"✅ 配置加载成功")
    print(f"📍 配置的域名: {config.get('domains', [])}")
    print(f"🔧 Git功能: {'启用' if config.get('git_enabled') else '禁用'}")
    
    # 初始化hosts管理器
    hosts_manager = HostsManager('hosts')
    domain_list = config.get('domains', ['example.com'])
    
    # 初始化Git管理器
    git_manager = GitManager()
    git_enabled = config.get('git_enabled', False)
    
    if git_enabled:
        if not git_manager.is_git_repo():
            print("🔧 初始化Git仓库...")
            git_manager.init_git_repo()
        
        git_name = config.get('git_name', 'Router Monitor')
        git_email = config.get('git_email', 'router@monitor.local')
        git_manager.set_git_config(git_name, git_email)
        print(f"🔧 Git用户配置: {git_name} <{git_email}>")
    
    # 模拟IP变化序列
    ip_sequence = [
        "192.168.1.100",
        "192.168.1.101", 
        "192.168.1.102",
        "192.168.1.103"
    ]
    
    print(f"\n🚀 开始模拟IP变化...")
    
    for i, new_ip in enumerate(ip_sequence, 1):
        print(f"\n--- 第{i}次IP变化 ---")
        print(f"🌐 新IP地址: {new_ip}")
        
        # 更新hosts文件
        if hosts_manager.update_hosts_file(new_ip, domain_list):
            print("✅ hosts文件已更新")
            
            # 显示文件内容摘要
            current_ip = hosts_manager.get_current_ip_from_hosts()
            print(f"📄 hosts文件当前IP: {current_ip}")
            
            # 如果启用了Git，提交并推送更改
            if git_enabled:
                print("📤 正在提交到Git...")
                commit_message = f"Update hosts file with new WAN IP: {new_ip}"
                if git_manager.add_and_commit('hosts', commit_message):
                    print("✅ Git提交成功")
                    
                    # 这里通常会推送到远程仓库，但为了演示我们跳过
                    print("ℹ️  如果配置了远程仓库，会自动推送更改")
                else:
                    print("❌ Git提交失败")
            else:
                print("ℹ️  Git功能未启用，跳过版本控制")
        else:
            print("ℹ️  hosts文件无需更新（IP未变化）")
        
        # 短暂暂停，模拟实际使用场景
        if i < len(ip_sequence):
            print("⏱️  等待3秒...")
            time.sleep(3)
    
    print(f"\n🎉 演示完成！")
    print(f"📂 请查看生成的hosts文件内容")
    
    # 显示最终的hosts文件内容
    try:
        print(f"\n📄 最终hosts文件内容:")
        print("-" * 40)
        with open('hosts', 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        print("-" * 40)
    except Exception as e:
        print(f"❌ 无法显示hosts文件内容: {e}")

if __name__ == '__main__':
    try:
        demo_hosts_management()
        
    except KeyboardInterrupt:
        print("\n🛑 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
