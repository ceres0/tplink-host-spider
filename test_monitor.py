# -*- coding:utf8 -*-
from main import *
import requests
import json
import time
import os
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('router_monitor_test.log'),
        logging.StreamHandler()
    ]
)

# 导入主程序的所有函数


def test_monitor_wan_status(iterations=3):
    """测试版监控WAN状态的函数，只运行指定次数"""
    logging.info(f"开始测试监控WAN状态，将运行 {iterations} 次，每次间隔10秒...")

    for i in range(iterations):
        try:
            logging.info(f"第 {i+1}/{iterations} 次获取WAN状态...")
            wan_data = get_wan_status_with_auth()

            if wan_data:
                # 保存数据到文件
                save_wan_data(wan_data)

                # 记录关键信息
                if wan_data.get('network') and wan_data['network'].get('wan_status'):
                    wan_status = wan_data['network']['wan_status']
                    proto = wan_status.get('proto', 'unknown')
                    ipaddr = wan_status.get('ipaddr', 'unknown')
                    logging.info(f"WAN状态: {proto}, IP: {ipaddr}")
                else:
                    logging.warning("WAN状态数据格式异常")
            else:
                logging.error("获取WAN状态失败")

        except Exception as e:
            logging.error(f"监控过程中发生错误: {e}")

        # 如果不是最后一次，等待10秒
        if i < iterations - 1:
            logging.info("等待10秒后进行下次获取...")
            time.sleep(10)

    logging.info("测试监控完成!")


if __name__ == '__main__':
    try:
        # 初始化配置
        config = load_config()
        save_config(config)

        # 开始测试监控
        test_monitor_wan_status()

    except KeyboardInterrupt:
        logging.info("程序被用户中断")
    except Exception as e:
        logging.error(f"程序发生异常: {e}")
