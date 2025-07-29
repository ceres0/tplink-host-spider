# -*- coding:utf8 -*-
"""
TP-LINK 路由器监控系统主程序
重构版本 - 模块化设计
"""
import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.monitor_service import RouterMonitorService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/router_monitor.log'),
        logging.StreamHandler()
    ]
)

def main():
    """主函数"""
    try:
        # 确保日志目录存在
        os.makedirs('logs', exist_ok=True)
        
        # 创建监控服务
        monitor_service = RouterMonitorService()
        
        # 开始监控
        monitor_service.monitor_wan_status()
        
    except KeyboardInterrupt:
        logging.info("程序被用户中断")
    except Exception as e:
        logging.error(f"程序发生异常: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
