# -*- coding:utf8 -*-
"""
数据管理模块
负责WAN口数据的存储和管理
"""
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from utils.path_utils import get_absolute_path, ensure_dir_exists


class DataManager:
    """数据管理器"""
    
    def __init__(self, data_file: str = 'data/wan_status_data.json'):
        self.data_file = get_absolute_path(data_file)
        
    def save_wan_data(self, data: Dict[str, Any]) -> bool:
        """保存WAN口数据到文件"""
        try:
            # 确保数据目录存在
            ensure_dir_exists(self.data_file)
            
            # 读取现有数据
            wan_history = []
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
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
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(wan_history, f, indent=4, ensure_ascii=False)

            logging.info(f"WAN口数据已保存，总记录数: {len(wan_history)}")
            return True
        except Exception as e:
            logging.error(f"保存WAN口数据失败: {e}")
            return False
    
    def load_wan_history(self) -> List[Dict[str, Any]]:
        """加载WAN口历史数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logging.error(f"加载WAN口历史数据失败: {e}")
            return []
    
    def get_latest_wan_data(self) -> Dict[str, Any]:
        """获取最新的WAN口数据"""
        history = self.load_wan_history()
        if history:
            return history[-1]
        return {}
