# -*- coding:utf8 -*-
import requests
import json
import logging
from datetime import datetime


class RouterMonitor:
    def __init__(self, host="192.168.1.1"):
        self.host = host

    def encrypt_pwd(self, password):
        """加密提交后的密码"""
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
            cl = 187
            cr = 187
            if index >= len1:
                cr = ord(password[index])
            elif index >= len2:
                cl = ord(input1[index])
            else:
                cl = ord(input1[index])
                cr = ord(password[index])
            index += 1
            output = output + chr(ord(dictionary[cl ^ cr]) % lenDict)
        return output

    def login(self, password='', encrypt_password=None):
        """提交登录请求的方法"""
        if not encrypt_password:
            encrypt_password = self.encrypt_pwd(password)

        url = f'http://{self.host}/'
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        payload = '{"method":"do","login":{"password":"%s"}}' % encrypt_password
        response = requests.post(url, data=payload, headers=headers)
        response_body = json.loads(response.text)
        return response_body

    def get_all_host(self, encrypt_password=None):
        """获取所有主机信息"""
        stok = self.login(encrypt_password=encrypt_password).get('stok')
        payload = '{"hosts_info":{"table":"host_info"},"method":"get"}'
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        url = f'http://{self.host}/stok={stok}/ds'
        response = requests.post(url, data=payload, headers=headers)
        return response.text

    def try_get_wan_status(self, stok):
        """尝试使用给定的stok获取WAN状态"""
        payload = '{"network":{"name":["wan_status"]},"method":"get"}'
        headers = {'Content-Type': 'application/json; charset=UTF-8'}
        url = f'http://{self.host}/stok={stok}/ds'

        try:
            response = requests.post(
                url, data=payload, headers=headers, timeout=10)
            response_data = json.loads(response.text)
            return response_data
        except Exception as e:
            logging.error(f"请求WAN状态失败: {e}")
            return None

    def get_wan_status_with_auth(self, config):
        """获取WAN状态，带智能身份验证"""

        # 如果有保存的stok，先尝试使用
        if config.get('stok'):
            logging.info("尝试使用保存的stok获取WAN状态")
            response_data = self.try_get_wan_status(config['stok'])

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
                config['encrypt_password'] = self.encrypt_pwd(
                    config['password'])

            login_response = self.login(
                encrypt_password=config['encrypt_password'])
            if login_response and 'stok' in login_response:
                new_stok = login_response['stok']
                logging.info("重新登录成功")

                # 更新配置
                config['stok'] = new_stok
                config['last_login_time'] = datetime.now().isoformat()

                # 使用新stok获取WAN状态
                response_data = self.try_get_wan_status(new_stok)
                return response_data
            else:
                logging.error("登录失败")
                return None
        except Exception as e:
            logging.error(f"登录过程中发生错误: {e}")
            return None

    def extract_wan_ip(self, wan_data):
        """从WAN状态数据中提取IP地址"""
        if wan_data and wan_data.get('network') and wan_data['network'].get('wan_status'):
            wan_status = wan_data['network']['wan_status']
            return wan_status.get('ipaddr', None)
        return None
