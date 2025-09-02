# -*- coding:utf8 -*-
"""
路径工具模块
提供统一的路径管理功能，解决相对路径问题
"""
import os


def get_project_root() -> str:
    """
    获取项目根目录的绝对路径
    
    Returns:
        str: 项目根目录的绝对路径
    """
    # 从当前文件出发，向上两级到达项目根目录
    # src/utils/path_utils.py -> src -> project_root
    current_file = os.path.realpath(__file__)
    src_dir = os.path.dirname(os.path.dirname(current_file))
    project_root = os.path.dirname(src_dir)
    return project_root


def get_absolute_path(relative_path: str) -> str:
    """
    将相对于项目根目录的路径转换为绝对路径
    
    Args:
        relative_path: 相对于项目根目录的路径
        
    Returns:
        str: 绝对路径
    """
    project_root = get_project_root()
    return os.path.join(project_root, relative_path)


def ensure_dir_exists(file_path: str) -> None:
    """
    确保文件所在的目录存在
    
    Args:
        file_path: 文件路径（可以是相对路径或绝对路径）
    """
    if not os.path.isabs(file_path):
        file_path = get_absolute_path(file_path)
    
    dir_path = os.path.dirname(file_path)
    os.makedirs(dir_path, exist_ok=True)
