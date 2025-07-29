# -*- coding:utf8 -*-
import json
import time
import os
from datetime import datetime
import logging
from main import load_config, save_config, save_wan_data
from router_monitor import RouterMonitor
from feishu_notifier import FeishuNotifier

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('router_monitor_test.log'),
        logging.StreamHandler()
    ]
)


def test_monitor_wan_status(iterations=3):
    """测试版监控WAN状态的函数，只运行指定次数"""
    logging.info(f"开始测试监控WAN状态，将运行 {iterations} 次，每次间隔10秒...")

    # 初始化路由器监控器和飞书通知器
    config = load_config()
    if not config:
        logging.error("无法加载配置文件，测试退出")
        return

    router = RouterMonitor(config.get('host', '192.168.1.1'))

    # 初始化飞书通知器（用于测试）
    feishu_webhook = config.get('feishu_webhook_url')
    feishu_secret = config.get('feishu_secret')

    feishu_notifier = None
    if feishu_webhook and feishu_secret and feishu_webhook != "https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-url":
        feishu_notifier = FeishuNotifier(feishu_webhook, feishu_secret)
        logging.info("飞书通知器已初始化（测试模式）")
    else:
        logging.warning("飞书配置为默认值或不完整，将不会发送通知")

    last_ip = None  # 记录上次的IP地址

    for i in range(iterations):
        try:
            logging.info(f"第 {i+1}/{iterations} 次获取WAN状态...")
            wan_data = router.get_wan_status_with_auth(config)

            if wan_data:
                # 保存数据到文件
                save_wan_data(wan_data)

                # 提取当前IP地址
                current_ip = router.extract_wan_ip(wan_data)

                if current_ip:
                    logging.info(f"当前WAN口IP: {current_ip}")

                    # 测试IP变化检测
                    if last_ip is not None and last_ip != current_ip:
                        logging.info(f"检测到IP变化: {last_ip} -> {current_ip}")

                        # 测试飞书通知（如果配置了）
                        if feishu_notifier:
                            logging.info("测试发送飞书通知...")
                            feishu_notifier.send_ip_change_notification(
                                last_ip, current_ip)
                    elif i == 0 and feishu_notifier:
                        # 第一次运行时发送测试通知
                        logging.info("发送测试启动通知...")
                        feishu_notifier.send_startup_notification(current_ip)

                    last_ip = current_ip

                    # 更新配置文件
                    save_config(config)
                else:
                    logging.warning("无法提取WAN口IP地址")

                # 记录关键信息
                if wan_data.get('network') and wan_data['network'].get('wan_status'):
                    wan_status = wan_data['network']['wan_status']
                    proto = wan_status.get('proto', 'unknown')
                    logging.info(f"WAN状态: {proto}")
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
