# -*- coding:utf8 -*-
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
        logging.FileHandler('router_monitor.log'),
        logging.StreamHandler()
    ]
)

# 配置文件路径
CONFIG_FILE = 'router_config.json'
WAN_DATA_FILE = 'wan_status_data.json'


def encrypt_pwd(password):  # 加密提交后的密码，可以把自己的密码提交到这个方法，再跟TP-LINK页面中实际提交的密码值做比对
    input1 = "RDpbLfCPsJZ7fiv"
    input3 = "yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW"
    len1 = len(input1)
    len2 = len(password)
    dictionary = input3
    lenDict = len(dictionary)
    output = ''
    if len1 > len2:
        length = len1
    else:
        length = len2
    index = 0
    while index < length:
        # 十六进制数 0xBB 的十进制为 187
        cl = 187
        cr = 187
        if index >= len1:
            # ord() 函数返回字符的整数表示
            cr = ord(password[index])
        elif index >= len2:
            cl = ord(input1[index])
        else:
            cl = ord(input1[index])
            cr = ord(password[index])
        index += 1
        # chr() 函数返回整数对应的字符
        output = output + chr(ord(dictionary[cl ^ cr]) % lenDict)
    return output


def login(password='', encrypt_password=None):  # 提交登录请求的方法
    if not encrypt_password:
        encrypt_password = encrypt_pwd(password)
    # encrypt_password = encrypt_pwd(password)
    url = 'http://192.168.1.1/'
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    payload = '{"method":"do","login":{"password":"%s"}}' % encrypt_password
    response = requests.post(url, data=payload, headers=headers)
    response_body = json.loads(response.text)
    return response_body


def get_all_host(encrypt_password=None):  # 获取所有主机信息
    stok = login(encrypt_password=encrypt_password).get('stok')
    payload = '{"hosts_info":{"table":"host_info"},"method":"get"}'
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    url = '%sstok=%s/ds' % ('http://192.168.1.1/', stok)
    response = requests.post(url, data=payload, headers=headers)
    return response.text


def get_wan_status_with_auth():
    """获取WAN状态，带智能身份验证"""
    config = load_config()

    def try_get_wan_status(host, stok):
        """尝试使用给定的stok获取WAN状态"""
        payload = '{"network":{"name":["wan_status"]},"method":"get"}'
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        url = f'http://{host}/stok={stok}/ds'

        try:
            response = requests.post(
                url, data=payload, headers=headers, timeout=10)
            response_data = json.loads(response.text)
            return response_data
        except Exception as e:
            logging.error(f"请求WAN状态失败: {e}")
            return None

    # 如果有保存的stok，先尝试使用
    if config.get('stok'):
        logging.info("尝试使用保存的stok获取WAN状态")
        response_data = try_get_wan_status(config['host'], config['stok'])

        if response_data and response_data.get('error_code') != -40401:
            # stok有效，返回数据
            return response_data
        else:
            logging.warning("保存的stok已失效，需要重新登录")

    # stok无效或不存在，重新登录
    logging.info("正在重新登录...")
    try:
        if not config.get('encrypt_password'):
            if not config.get('password'):
                logging.error("配置中没有 WIFI 密码，无法登录")
                return None
            config['encrypt_password'] = encrypt_pwd(config['password'])
        login_response = login(encrypt_password=config['encrypt_password'])
        if login_response and 'stok' in login_response:
            new_stok = login_response['stok']
            logging.info("重新登录成功")

            # 更新配置
            config['stok'] = new_stok
            config['last_login_time'] = datetime.now().isoformat()
            save_config(config)

            # 使用新stok获取WAN状态
            response_data = try_get_wan_status(config['host'], new_stok)
            return response_data
        else:
            logging.error("登录失败")
            return None
    except Exception as e:
        logging.error(f"登录过程中发生错误: {e}")
        return None


def get_wan_status(encrypt_password):
    """保持向后兼容的函数"""
    stok = login(encrypt_password=encrypt_password).get('stok')
    payload = '{"network":{"name":["wan_status"]},"method":"get"}'
    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    url = '%sstok=%s/ds' % ('http://192.168.1.1/', stok)
    response = requests.post(url, data=payload, headers=headers)
    return response.text


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
    """监控WAN状态的主函数"""
    logging.info("开始监控WAN状态，每分钟获取一次数据...")

    while True:
        try:
            logging.info("正在获取WAN状态...")
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
