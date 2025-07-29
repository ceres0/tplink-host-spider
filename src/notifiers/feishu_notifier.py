# -*- coding:utf8 -*-
import requests
import json
import time
import logging
import hmac
import hashlib
import base64


class FeishuNotifier:
    def __init__(self, webhook_url, secret):
        self.webhook_url = webhook_url
        self.secret = secret

    def gen_sign(self, timestamp, secret):
        # 拼接timestamp和secret
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        hmac_code = hmac.new(string_to_sign.encode(
            "utf-8"), digestmod=hashlib.sha256).digest()
        # 对结果进行base64处理
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign

    def send_message(self, text):
        """发送消息到飞书"""
        try:
            timestamp = str(int(time.time()))
            sign = self.gen_sign(timestamp, self.secret)

            payload = {
                "timestamp": timestamp,
                "sign": sign,
                "msg_type": "text",
                "content": {
                    "text": text
                }
            }

            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                logging.info("飞书消息发送成功")
                return True
            else:
                logging.error(
                    f"飞书消息发送失败，状态码: {response.status_code}, 响应: {response.text}")
                return False

        except Exception as e:
            logging.error(f"发送飞书消息时发生错误: {e}")
            return False

    def send_ip_change_notification(self, old_ip, new_ip):
        """发送IP变化通知"""
        message = f"路由器WAN口IP地址发生变化\n旧IP: {old_ip}\n新IP: {new_ip}\n时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        return self.send_message(message)

    def send_startup_notification(self, current_ip):
        """发送启动通知"""
        message = f"路由器监控程序已启动\n当前WAN口IP: {current_ip}\n时间: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        return self.send_message(message)
