# -*- coding:utf8 -*-
"""
配置管理模块
负责配置文件的加载、保存和验证
"""
import json
import os
import logging
from typing import Dict, Any, Optional


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = 'router_config.json'):
        self.config_file = config_file
        self.config = {}
        
    def load_config(self) -> Optional[Dict[str, Any]]:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    return self.config
            else:
                logging.warning(f"配置文件不存在: {self.config_file}")
                return None
        except Exception as e:
            logging.error(f"加载配置文件失败: {e}")
            return None

    def save_config(self, config: Dict[str, Any]) -> bool:
        """保存配置到文件"""
        try:
            # 确保配置目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            self.config = config
            logging.info("配置已保存到文件")
            return True
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")
            return False
    
    def get_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return self.config
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置项"""
        self.config[key] = value
    
    def validate_config(self) -> bool:
        """验证配置完整性"""
        required_keys = ['host', 'password']
        for key in required_keys:
            if key not in self.config:
                logging.error(f"缺少必需的配置项: {key}")
                return False
        return True
