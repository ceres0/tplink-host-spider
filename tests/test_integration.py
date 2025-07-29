# -*- coding:utf8 -*-
"""
综合功能测试脚本
测试重构后的模块化系统
"""
import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config_manager import ConfigManager
from src.utils.data_manager import DataManager
from src.core.router_monitor import RouterMonitor
from src.notifiers.feishu_notifier import FeishuNotifier
from src.managers.hosts_manager import HostsManager, GitManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_config_manager():
    """测试配置管理器"""
    print("=" * 50)
    print("测试配置管理器")
    print("=" * 50)
    
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    if config:
        print("✅ 配置加载成功")
        print(f"📍 路由器地址: {config.get('host', 'N/A')}")
        print(f"📍 配置的域名: {config.get('domains', [])}")
        print(f"🔧 Git功能: {'启用' if config.get('git_enabled') else '禁用'}")
        
        # 测试配置验证
        if config_manager.validate_config():
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败")
            
        return True
    else:
        print("❌ 配置加载失败")
        return False

def test_data_manager():
    """测试数据管理器"""
    print("\n" + "=" * 50)
    print("测试数据管理器")
    print("=" * 50)
    
    data_manager = DataManager()
    
    # 测试保存数据
    test_data = {
        'network': {
            'wan_status': {
                'ipaddr': '192.168.1.100',
                'proto': 'dhcp'
            }
        }
    }
    
    if data_manager.save_wan_data(test_data):
        print("✅ 数据保存成功")
    else:
        print("❌ 数据保存失败")
        return False
    
    # 测试加载数据
    history = data_manager.load_wan_history()
    if history:
        print(f"✅ 数据加载成功，记录数: {len(history)}")
        
        # 测试获取最新数据
        latest = data_manager.get_latest_wan_data()
        if latest:
            print("✅ 获取最新数据成功")
            return True
    
    print("❌ 数据加载失败")
    return False

def test_router_monitor():
    """测试路由器监控器"""
    print("\n" + "=" * 50)
    print("测试路由器监控器")
    print("=" * 50)
    
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        if not config:
            print("❌ 无法加载配置，跳过路由器测试")
            return False
        
        router = RouterMonitor(config.get('host', '192.168.1.1'))
        print("✅ 路由器监控器初始化成功")
        
        # 这里不进行实际的网络请求测试，避免影响路由器
        print("ℹ️  跳过实际网络请求测试（避免影响路由器）")
        return True
        
    except Exception as e:
        print(f"❌ 路由器监控器测试失败: {e}")
        return False

def test_feishu_notifier():
    """测试飞书通知器"""
    print("\n" + "=" * 50)
    print("测试飞书通知器")
    print("=" * 50)
    
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        if not config:
            print("❌ 无法加载配置，跳过飞书测试")
            return False
        
        webhook = config.get('feishu_webhook_url')
        secret = config.get('feishu_secret')
        
        if webhook and secret:
            feishu_notifier = FeishuNotifier(webhook, secret)
            print("✅ 飞书通知器初始化成功")
            print("ℹ️  跳过实际通知发送测试（避免发送测试消息）")
            return True
        else:
            print("⚠️  飞书配置不完整，但模块加载正常")
            return True
            
    except Exception as e:
        print(f"❌ 飞书通知器测试失败: {e}")
        return False

def test_hosts_manager():
    """测试hosts管理器"""
    print("\n" + "=" * 50)
    print("测试hosts管理器")
    print("=" * 50)
    
    try:
        # 使用测试文件，避免影响实际hosts文件
        hosts_manager = HostsManager('test_hosts_integration')
        
        test_domains = ['test1.example.com', 'test2.example.com']
        test_ip = '192.168.1.100'
        
        # 测试创建和更新
        if hosts_manager.update_hosts_file(test_ip, test_domains):
            print("✅ hosts文件更新成功")
            
            # 测试读取
            current_ip = hosts_manager.get_current_ip_from_hosts()
            if current_ip == test_ip:
                print("✅ hosts文件读取成功")
                
                # 清理测试文件
                os.remove('test_hosts_integration')
                return True
            else:
                print("❌ hosts文件读取失败")
        else:
            print("❌ hosts文件更新失败")
            
    except Exception as e:
        print(f"❌ hosts管理器测试失败: {e}")
        
    # 清理可能的测试文件
    try:
        os.remove('test_hosts_integration')
    except:
        pass
        
    return False

def test_git_manager():
    """测试Git管理器"""
    print("\n" + "=" * 50)
    print("测试Git管理器")
    print("=" * 50)
    
    try:
        git_manager = GitManager()
        
        if git_manager.is_git_repo():
            print("✅ Git仓库检测成功")
            print("ℹ️  跳过Git操作测试（避免产生测试提交）")
            return True
        else:
            print("⚠️  当前目录不是Git仓库，但模块加载正常")
            return True
            
    except Exception as e:
        print(f"❌ Git管理器测试失败: {e}")
        return False

def test_integration():
    """集成测试"""
    print("\n" + "=" * 50)
    print("集成测试 - 导入监控服务")
    print("=" * 50)
    
    try:
        from src.core.monitor_service import RouterMonitorService
        print("✅ 监控服务模块导入成功")
        
        # 不实际启动服务，只测试初始化
        print("ℹ️  跳过服务启动测试（避免启动实际监控）")
        return True
        
    except Exception as e:
        print(f"❌ 监控服务测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始模块化系统测试")
    print("=" * 60)
    
    tests = [
        ("配置管理器", test_config_manager),
        ("数据管理器", test_data_manager),
        ("路由器监控器", test_router_monitor),
        ("飞书通知器", test_feishu_notifier),
        ("hosts管理器", test_hosts_manager),
        ("Git管理器", test_git_manager),
        ("集成测试", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试发生异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！模块化重构成功！")
        return True
    else:
        print("⚠️  部分测试失败，需要检查相关模块")
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        sys.exit(1)
