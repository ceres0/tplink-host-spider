# -*- coding:utf8 -*-
"""
路由器监控服务
整合所有功能模块的主服务类
"""
import logging
import time
from typing import Optional

from core.router_monitor import RouterMonitor
from notifiers.feishu_notifier import FeishuNotifier
from managers.hosts_manager import HostsManager, GitManager
from utils.config_manager import ConfigManager
from utils.data_manager import DataManager


class RouterMonitorService:
    """路由器监控服务"""
    
    def __init__(self):
        # 初始化各个管理器
        self.config_manager = ConfigManager()
        self.data_manager = DataManager()
        
        # 加载配置
        self.config = self.config_manager.load_config()
        if not self.config:
            raise Exception("无法加载配置文件，服务启动失败")
        
        # 初始化各个模块
        self.router = RouterMonitor(self.config.get('host', '192.168.1.1'))
        self.feishu_notifier = self._init_feishu_notifier()
        self.hosts_manager = self._init_hosts_manager()
        self.git_manager = self._init_git_manager()
        
        # 状态变量
        self.last_ip = None
        self.startup_notification_sent = False
        
    def _init_feishu_notifier(self) -> Optional[FeishuNotifier]:
        """初始化飞书通知器"""
        feishu_webhook = self.config.get('feishu_webhook_url')
        feishu_secret = self.config.get('feishu_secret')
        
        if feishu_webhook and feishu_secret:
            logging.info("飞书通知器已初始化")
            return FeishuNotifier(feishu_webhook, feishu_secret)
        else:
            logging.warning("飞书配置不完整，将不会发送通知")
            return None
    
    def _init_hosts_manager(self) -> Optional[HostsManager]:
        """初始化hosts管理器"""
        if self.config.get('hosts_enabled', True):
            hosts_file = self.config.get('hosts_file', 'hosts')
            return HostsManager(hosts_file)
        return None
    
    def _init_git_manager(self) -> Optional[GitManager]:
        """初始化Git管理器"""
        if self.config.get('git_enabled', False):
            git_manager = GitManager()
            
            # 初始化Git仓库（如果需要）
            if not git_manager.is_git_repo():
                logging.info("初始化Git仓库...")
                git_manager.init_git_repo()
            
            # 设置Git用户信息
            git_name = self.config.get('git_name', 'Router Monitor')
            git_email = self.config.get('git_email', 'router@monitor.local')
            git_manager.set_git_config(git_name, git_email)
            
            logging.info("Git管理器已初始化")
            return git_manager
        else:
            logging.info("Git功能已禁用")
            return None
    
    def monitor_wan_status(self):
        """监控WAN状态的主函数"""
        logging.info("开始监控WAN状态，每分钟获取一次数据...")
        
        while True:
            try:
                self._check_wan_status()
            except Exception as e:
                logging.error(f"监控过程中发生错误: {e}")
            
            # 等待60秒
            logging.info("等待60秒后进行下次获取...")
            time.sleep(60)
    
    def _check_wan_status(self):
        """检查WAN状态"""
        logging.info("正在获取WAN状态...")
        wan_data = self.router.get_wan_status_with_auth(self.config)
        
        if wan_data:
            # 保存数据到文件
            self.data_manager.save_wan_data(wan_data)
            
            # 提取当前IP地址
            current_ip = self.router.extract_wan_ip(wan_data)
            
            if current_ip:
                self._handle_ip_status(current_ip)
                
                # 更新配置文件（保存最新的stok等信息）
                self.config_manager.save_config(self.config)
            else:
                logging.warning("无法提取WAN口IP地址")
            
            # 记录关键信息
            self._log_wan_status(wan_data)
        else:
            logging.error("获取WAN状态失败")
    
    def _handle_ip_status(self, current_ip: str):
        """处理IP状态变化"""
        logging.info(f"当前WAN口IP: {current_ip}")
        
        # 发送启动通知（仅第一次）
        if not self.startup_notification_sent and self.feishu_notifier:
            self.feishu_notifier.send_startup_notification(current_ip)
            self.startup_notification_sent = True
        
        # 检查IP是否发生变化
        if self.last_ip is not None and self.last_ip != current_ip:
            logging.info(f"检测到IP变化: {self.last_ip} -> {current_ip}")
            self._handle_ip_change(self.last_ip, current_ip)
        
        # 更新hosts文件
        if self.hosts_manager:
            domain_list = self.config.get('domains', [])
            if self.hosts_manager.update_hosts_file(current_ip, domain_list):
                logging.info("hosts文件已更新")
                self._handle_git_commit(current_ip)
        
        # 更新上次IP
        self.last_ip = current_ip
    
    def _handle_ip_change(self, old_ip: str, new_ip: str):
        """处理IP变化"""
        # 发送飞书通知
        if self.feishu_notifier:
            self.feishu_notifier.send_ip_change_notification(old_ip, new_ip)
    
    def _handle_git_commit(self, current_ip: str):
        """处理Git提交"""
        if self.git_manager:
            hosts_file = self.config.get('hosts_file', 'hosts')
            commit_message = f"Update hosts file with new WAN IP: {current_ip}"
            
            if self.git_manager.add_and_commit(hosts_file, commit_message):
                # 推送到远程仓库
                remote = self.config.get('git_remote', 'origin')
                branch = self.config.get('git_branch', 'main')
                self.git_manager.push_to_remote(remote, branch)
    
    def _log_wan_status(self, wan_data: dict):
        """记录WAN状态信息"""
        if wan_data.get('network') and wan_data['network'].get('wan_status'):
            wan_status = wan_data['network']['wan_status']
            proto = wan_status.get('proto', 'unknown')
            logging.info(f"WAN状态: {proto}")
        else:
            logging.warning("WAN状态数据格式异常")
