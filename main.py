# -*- coding:utf8 -*-
import json
import time
import os
from datetime import datetime
import logging
from router_monitor import RouterMonitor
from feishu_notifier import FeishuNotifier

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('router_monitor.log'),
        logging.StreamHandler()
    ]
)

# 配置文件路径
CONFIG_FILE = 'router_config.json'
WAN_DATA_FILE = 'wan_status_data.json'


def load_config():
    """加载配置文件"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"加载配置文件失败: {e}")


def save_config(config):
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        logging.info("配置已保存到文件")
    except Exception as e:
        logging.error(f"保存配置文件失败: {e}")


def save_wan_data(data):
    """保存WAN口数据到文件"""
    try:
        # 读取现有数据
        wan_history = []
        if os.path.exists(WAN_DATA_FILE):
            with open(WAN_DATA_FILE, 'r', encoding='utf-8') as f:
                wan_history = json.load(f)

        # 添加时间戳
        current_data = {
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        wan_history.append(current_data)

        # 保留最近10条记录
        if len(wan_history) > 10:
            wan_history = wan_history[-10:]

        # 保存到文件
        with open(WAN_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(wan_history, f, indent=4, ensure_ascii=False)

        logging.info(f"WAN口数据已保存，总记录数: {len(wan_history)}")
    except Exception as e:
        logging.error(f"保存WAN口数据失败: {e}")


def monitor_wan_status():
    """监控WAN状态的主函数，当IP变化时发送飞书通知"""
    logging.info("开始监控WAN状态，每分钟获取一次数据...")

    # 初始化路由器监控器
    config = load_config()
    if not config:
        logging.error("无法加载配置文件，程序退出")
        return

    router = RouterMonitor(config.get('host', '192.168.1.1'))

    # 初始化飞书通知器
    feishu_webhook = config.get('feishu_webhook_url')
    feishu_secret = config.get('feishu_secret')

    feishu_notifier = None
    if feishu_webhook and feishu_secret:
        feishu_notifier = FeishuNotifier(feishu_webhook, feishu_secret)
        logging.info("飞书通知器已初始化")
    else:
        logging.warning("飞书配置不完整，将不会发送通知")

    last_ip = None  # 记录上次的IP地址
    startup_notification_sent = False  # 记录是否已发送启动通知

    while True:
        try:
            logging.info("正在获取WAN状态...")
            wan_data = router.get_wan_status_with_auth(config)

            if wan_data:
                # 保存数据到文件
                save_wan_data(wan_data)

                # 提取当前IP地址
                current_ip = router.extract_wan_ip(wan_data)

                if current_ip:
                    logging.info(f"当前WAN口IP: {current_ip}")

                    # 发送启动通知（仅第一次）
                    if not startup_notification_sent and feishu_notifier:
                        feishu_notifier.send_startup_notification(current_ip)
                        startup_notification_sent = True

                    # 检查IP是否发生变化
                    if last_ip is not None and last_ip != current_ip:
                        logging.info(f"检测到IP变化: {last_ip} -> {current_ip}")

                        # 发送飞书通知
                        if feishu_notifier:
                            feishu_notifier.send_ip_change_notification(
                                last_ip, current_ip)

                    # 更新上次IP
                    last_ip = current_ip

                    # 更新配置文件（保存最新的stok等信息）
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

        # 等待60秒
        logging.info("等待60秒后进行下次获取...")
        time.sleep(60)


if __name__ == '__main__':
    try:
        # 初始化配置
        config = load_config()
        save_config(config)

        # 开始监控
        monitor_wan_status()

    except KeyboardInterrupt:
        logging.info("程序被用户中断")
    except Exception as e:
        logging.error(f"程序发生异常: {e}")
