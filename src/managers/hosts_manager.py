# -*- coding:utf8 -*-
import os
import logging
import subprocess
from datetime import datetime


class HostsManager:
    def __init__(self, hosts_file_path='hosts'):
        """
        初始化hosts文件管理器
        
        Args:
            hosts_file_path (str): hosts文件路径，默认为当前目录下的hosts文件
        """
        self.hosts_file_path = hosts_file_path
        self.current_ip = None
        
    def create_hosts_file(self, domain_list=None):
        """
        创建初始hosts文件
        
        Args:
            domain_list (list): 需要绑定的域名列表，默认为一些常用域名
        """
        if domain_list is None:
            domain_list = [
                "example.com",
                "www.example.com",
                "api.example.com",
                "app.example.com"
            ]
        
        try:
            with open(self.hosts_file_path, 'w', encoding='utf-8') as f:
                f.write("# Auto-generated hosts file\n")
                f.write(f"# Created at: {datetime.now().isoformat()}\n")
                f.write("# This file is automatically updated by router monitor\n\n")
                
                # 添加默认的localhost条目
                f.write("127.0.0.1    localhost\n")
                f.write("::1          localhost\n\n")
                
                # 添加注释说明动态IP部分
                f.write("# Dynamic WAN IP entries (auto-updated)\n")
                for domain in domain_list:
                    f.write(f"# {domain}\n")
                
            logging.info(f"hosts文件已创建: {self.hosts_file_path}")
            return True
            
        except Exception as e:
            logging.error(f"创建hosts文件失败: {e}")
            return False
    
    def update_hosts_file(self, new_ip, domain_list=None):
        """
        更新hosts文件中的IP地址
        
        Args:
            new_ip (str): 新的IP地址
            domain_list (list): 需要更新的域名列表
            
        Returns:
            bool: 是否有实际更新
        """
        if domain_list is None:
            domain_list = [
                "example.com",
                "www.example.com", 
                "api.example.com",
                "app.example.com"
            ]
        
        # 如果IP没有变化，不需要更新
        if self.current_ip == new_ip:
            return False
            
        try:
            # 如果文件不存在，先创建
            if not os.path.exists(self.hosts_file_path):
                self.create_hosts_file(domain_list)
            
            # 读取现有内容
            with open(self.hosts_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 更新内容
            updated_content = []
            in_dynamic_section = False
            
            for line in lines:
                stripped_line = line.strip()
                
                # 标记动态IP部分的开始
                if "# Dynamic WAN IP entries" in line:
                    in_dynamic_section = True
                    updated_content.append(line)
                    continue
                
                # 如果在动态部分，跳过旧的IP条目
                if in_dynamic_section and any(domain in line for domain in domain_list):
                    continue
                
                updated_content.append(line)
            
            # 如果没有找到动态部分，添加它
            if not in_dynamic_section:
                updated_content.extend([
                    "\n# Dynamic WAN IP entries (auto-updated)\n"
                ])
            
            # 添加新的IP条目
            updated_content.append(f"# Updated at: {datetime.now().isoformat()}\n")
            for domain in domain_list:
                updated_content.append(f"{new_ip}    {domain}\n")
            
            # 写入更新后的内容
            with open(self.hosts_file_path, 'w', encoding='utf-8') as f:
                f.writelines(updated_content)
            
            self.current_ip = new_ip
            logging.info(f"hosts文件已更新，新IP: {new_ip}")
            return True
            
        except Exception as e:
            logging.error(f"更新hosts文件失败: {e}")
            return False
    
    def get_current_ip_from_hosts(self):
        """
        从hosts文件中获取当前设置的IP地址
        
        Returns:
            str: 当前IP地址，如果未找到返回None
        """
        try:
            if not os.path.exists(self.hosts_file_path):
                return None
                
            with open(self.hosts_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 查找最后一个有效的IP条目
            for line in reversed(lines):
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith('#'):
                    parts = stripped_line.split()
                    if len(parts) >= 2:
                        # 简单验证是否为IP地址格式
                        ip = parts[0]
                        if ip.count('.') == 3 and ip != '127.0.0.1':
                            return ip
            
            return None
            
        except Exception as e:
            logging.error(f"读取hosts文件失败: {e}")
            return None


class GitManager:
    def __init__(self, repo_path='.'):
        """
        初始化Git管理器
        
        Args:
            repo_path (str): Git仓库路径，默认为当前目录
        """
        self.repo_path = repo_path
    
    def is_git_repo(self):
        """检查是否为Git仓库"""
        return os.path.exists(os.path.join(self.repo_path, '.git'))
    
    def init_git_repo(self):
        """初始化Git仓库"""
        try:
            if not self.is_git_repo():
                result = subprocess.run(['git', 'init'], 
                                      cwd=self.repo_path, 
                                      capture_output=True, 
                                      text=True)
                if result.returncode == 0:
                    logging.info("Git仓库初始化成功")
                    return True
                else:
                    logging.error(f"Git仓库初始化失败: {result.stderr}")
                    return False
            return True
        except Exception as e:
            logging.error(f"初始化Git仓库时发生错误: {e}")
            return False
    
    def add_and_commit(self, file_path, commit_message):
        """
        添加文件到Git并提交
        
        Args:
            file_path (str): 要添加的文件路径
            commit_message (str): 提交信息
            
        Returns:
            bool: 是否成功
        """
        try:
            # 添加文件
            result = subprocess.run(['git', 'add', file_path], 
                                  cwd=self.repo_path, 
                                  capture_output=True, 
                                  text=True)
            if result.returncode != 0:
                logging.error(f"Git add失败: {result.stderr}")
                return False
            
            # 检查是否有变化需要提交
            result = subprocess.run(['git', 'diff', '--cached', '--quiet'], 
                                  cwd=self.repo_path, 
                                  capture_output=True, 
                                  text=True)
            
            # 如果返回码为1，说明有变化需要提交
            if result.returncode == 1:
                # 提交变化
                result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                      cwd=self.repo_path, 
                                      capture_output=True, 
                                      text=True)
                if result.returncode == 0:
                    logging.info(f"Git提交成功: {commit_message}")
                    return True
                else:
                    logging.error(f"Git提交失败: {result.stderr}")
                    return False
            else:
                logging.info("没有变化需要提交")
                return True
                
        except Exception as e:
            logging.error(f"Git操作时发生错误: {e}")
            return False
    
    def push_to_remote(self, remote='origin', branch='main'):
        """
        推送到远程仓库
        
        Args:
            remote (str): 远程仓库名，默认为origin
            branch (str): 分支名，默认为main
            
        Returns:
            bool: 是否成功
        """
        try:
            result = subprocess.run(['git', 'push', remote, branch], 
                                  cwd=self.repo_path, 
                                  capture_output=True, 
                                  text=True)
            if result.returncode == 0:
                logging.info(f"推送到远程仓库成功: {remote}/{branch}")
                return True
            else:
                logging.error(f"推送到远程仓库失败: {result.stderr}")
                return False
                
        except Exception as e:
            logging.error(f"推送到远程仓库时发生错误: {e}")
            return False
    
    def set_git_config(self, name, email):
        """
        设置Git用户配置
        
        Args:
            name (str): 用户名
            email (str): 邮箱
        """
        try:
            subprocess.run(['git', 'config', 'user.name', name], 
                          cwd=self.repo_path, 
                          capture_output=True, 
                          text=True)
            subprocess.run(['git', 'config', 'user.email', email], 
                          cwd=self.repo_path, 
                          capture_output=True, 
                          text=True)
            logging.info(f"Git配置已设置: {name} <{email}>")
        except Exception as e:
            logging.error(f"设置Git配置时发生错误: {e}")
