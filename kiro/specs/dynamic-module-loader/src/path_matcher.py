"""
路径匹配逻辑模块

该模块提供路径和文件类型的匹配功能，支持通配符模式。

支持的匹配类型：
    - directory_match: 目录路径匹配（支持 * 通配符）
    - file_type_match: 文件类型匹配（按扩展名）

作者: yangzhuo
日期: 2026-03-03
版本: v1.0
"""

import fnmatch
from typing import List, Union


def match_directory(path: str, patterns: Union[str, List[str]]) -> bool:
    """
    匹配目录路径（支持通配符 *）
    
    Args:
        path: 实际路径
        patterns: 模式字符串或模式列表（支持 * 通配符）
        
    Returns:
        是否匹配任一模式
        
    Examples:
        >>> match_directory('.kiro/steering/main.md', '.kiro/steering/*')
        True
        
        >>> match_directory('.kiro/modules/workflow/v1.0', '.kiro/modules/*')
        True
        
        >>> match_directory('.kiro/steering', '.kiro/*')
        True
        
        >>> match_directory('src/main.py', '.kiro/*')
        False
        
        >>> match_directory('.kiro/steering/main.md', ['.kiro/steering/*', '.kiro/modules/*'])
        True
        
    Notes:
        - 支持单个模式字符串或模式列表
        - 使用 fnmatch 进行通配符匹配
        - * 匹配任意字符（包括路径分隔符）
        - 任一模式匹配即返回 True
    """
    # 确保 patterns 是列表
    if isinstance(patterns, str):
        patterns = [patterns]
    
    # 检查是否匹配任一模式
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    
    return False


def match_file_type(file_path: str, extensions: Union[str, List[str]]) -> bool:
    """
    匹配文件类型（按扩展名）
    
    Args:
        file_path: 文件路径或扩展名（如 '.md' 或 'file.md'）
        extensions: 扩展名字符串或扩展名列表（如 '.md' 或 ['.md', '.yaml']）
        
    Returns:
        是否匹配任一扩展名
        
    Examples:
        >>> match_file_type('.md', '.md')
        True
        
        >>> match_file_type('file.md', '.md')
        True
        
        >>> match_file_type('.md', '.yaml')
        False
        
        >>> match_file_type('.md', ['.md', '.yaml', '.json'])
        True
        
        >>> match_file_type('config.yaml', ['.md', '.yaml', '.json'])
        True
        
        >>> match_file_type('script.py', ['.md', '.yaml'])
        False
        
    Notes:
        - 支持单个扩展名字符串或扩展名列表
        - 扩展名应包含点号（如 '.md'）
        - 任一扩展名匹配即返回 True
        - 如果 file_path 本身就是扩展名（以 . 开头），直接匹配
    """
    # 确保 extensions 是列表
    if isinstance(extensions, str):
        extensions = [extensions]
    
    # 检查是否匹配任一扩展名
    for ext in extensions:
        if file_path.endswith(ext):
            return True
    
    return False


def match_pattern(path: str, pattern: str) -> bool:
    """
    通用路径模式匹配（支持通配符 *）
    
    这是一个通用的模式匹配函数，被 match_directory 内部使用。
    也可以直接调用进行简单的模式匹配。
    
    Args:
        path: 实际路径
        pattern: 模式字符串（支持 * 通配符）
        
    Returns:
        是否匹配
        
    Examples:
        >>> match_pattern('.kiro/steering', '.kiro/*')
        True
        
        >>> match_pattern('.kiro/modules/workflow/v1.0', '.kiro/modules/*')
        True
        
        >>> match_pattern('doc/project/test.md', 'doc/**/*')
        True
        
        >>> match_pattern('src/main.py', '.kiro/*')
        False
        
    Notes:
        - 使用 fnmatch 进行通配符匹配
        - * 匹配任意字符（包括路径分隔符）
        - ** 在 fnmatch 中等同于 *
    """
    return fnmatch.fnmatch(path, pattern)


def normalize_path(path: str) -> str:
    """
    规范化路径（可选功能，用于未来扩展）
    
    将路径转换为统一格式，处理不同操作系统的路径分隔符。
    
    Args:
        path: 原始路径
        
    Returns:
        规范化后的路径
        
    Examples:
        >>> normalize_path('.kiro\\steering\\main.md')
        '.kiro/steering/main.md'
        
        >>> normalize_path('.kiro/steering/main.md')
        '.kiro/steering/main.md'
        
    Notes:
        - 将反斜杠 \\ 转换为正斜杠 /
        - 用于处理 Windows 和 Unix 路径差异
        - 当前版本为简单实现，未来可扩展
    """
    return path.replace('\\', '/')


# 导出的公共 API
__all__ = [
    'match_directory',
    'match_file_type',
    'match_pattern',
    'normalize_path'
]
