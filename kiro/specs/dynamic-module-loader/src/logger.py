"""
日志输出器模块

本模块提供统一的日志输出功能，用于动态模块加载器的日志记录。

需求追溯：
- 需求 9.1: 实现日志输出功能
- 需求 9.2: 实现日志级别（INFO, WARNING, ERROR）
- 需求 9.3: 实现模块状态日志
- 需求 9.4: 使用清晰的日志格式

日志格式：
[时间] [级别] [组件] 消息内容

示例：
[2026-03-03 10:30:00] [INFO] [DynamicLoader] 开始加载模块
[2026-03-03 10:30:01] [WARNING] [DynamicLoader] 配置文件不存在
[2026-03-03 10:30:02] [ERROR] [DynamicLoader] 读取文件失败
"""

from datetime import datetime
from typing import Dict, Any, Optional


def _format_timestamp() -> str:
    """
    格式化当前时间戳
    
    Returns:
        格式化的时间字符串（YYYY-MM-DD HH:MM:SS）
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_info(message: str, component: str = "DynamicLoader") -> None:
    """
    输出信息日志
    
    Args:
        message: 日志消息内容
        component: 组件名称，默认为 "DynamicLoader"
    
    需求追溯：需求 9.1, 9.2
    
    示例：
        >>> log_info("开始加载模块")
        [2026-03-03 10:30:00] [INFO] [DynamicLoader] 开始加载模块
    """
    timestamp = _format_timestamp()
    print(f"[{timestamp}] [INFO] [{component}] {message}")


def log_warning(message: str, component: str = "DynamicLoader") -> None:
    """
    输出警告日志
    
    Args:
        message: 日志消息内容
        component: 组件名称，默认为 "DynamicLoader"
    
    需求追溯：需求 9.1, 9.2
    
    示例：
        >>> log_warning("配置文件不存在")
        [2026-03-03 10:30:00] [WARNING] [DynamicLoader] 配置文件不存在
    """
    timestamp = _format_timestamp()
    print(f"[{timestamp}] [WARNING] [{component}] {message}")


def log_error(message: str, component: str = "DynamicLoader") -> None:
    """
    输出错误日志
    
    Args:
        message: 日志消息内容
        component: 组件名称，默认为 "DynamicLoader"
    
    需求追溯：需求 9.1, 9.2
    
    示例：
        >>> log_error("读取文件失败")
        [2026-03-03 10:30:00] [ERROR] [DynamicLoader] 读取文件失败
    """
    timestamp = _format_timestamp()
    print(f"[{timestamp}] [ERROR] [{component}] {message}")


def log_module_status(
    module: Dict[str, Any],
    status: str,
    component: str = "DynamicLoader"
) -> None:
    """
    输出模块状态日志
    
    Args:
        module: 模块信息字典，应包含以下字段：
            - name: 模块名称
            - version: 模块版本
            - priority: 模块优先级
        status: 模块状态描述（如 "已激活", "已跳过", "加载成功" 等）
        component: 组件名称，默认为 "DynamicLoader"
    
    需求追溯：需求 9.3, 9.4
    
    示例：
        >>> module = {"name": "workflow", "version": "v1.0", "priority": 200}
        >>> log_module_status(module, "已激活")
        [2026-03-03 10:30:00] [INFO] [DynamicLoader] 模块: workflow | 版本: v1.0 | 优先级: 200 | 状态: 已激活
    """
    timestamp = _format_timestamp()
    name = module.get("name", "未知")
    version = module.get("version", "未知")
    priority = module.get("priority", 0)
    
    message = f"模块: {name} | 版本: {version} | 优先级: {priority} | 状态: {status}"
    print(f"[{timestamp}] [INFO] [{component}] {message}")


def log_loading_start(total_modules: int, component: str = "DynamicLoader") -> None:
    """
    输出加载开始日志
    
    Args:
        total_modules: 总模块数量
        component: 组件名称，默认为 "DynamicLoader"
    
    需求追溯：需求 9.1, 9.4
    
    示例：
        >>> log_loading_start(4)
        [2026-03-03 10:30:00] [INFO] [DynamicLoader] ========================================
        [2026-03-03 10:30:00] [INFO] [DynamicLoader] 开始加载模块（共 4 个模块）
        [2026-03-03 10:30:00] [INFO] [DynamicLoader] ========================================
    """
    timestamp = _format_timestamp()
    separator = "=" * 40
    print(f"[{timestamp}] [INFO] [{component}] {separator}")
    print(f"[{timestamp}] [INFO] [{component}] 开始加载模块（共 {total_modules} 个模块）")
    print(f"[{timestamp}] [INFO] [{component}] {separator}")


def log_loading_complete(
    activated_count: int,
    skipped_count: int,
    component: str = "DynamicLoader"
) -> None:
    """
    输出加载完成日志
    
    Args:
        activated_count: 激活的模块数量
        skipped_count: 跳过的模块数量
        component: 组件名称，默认为 "DynamicLoader"
    
    需求追溯：需求 9.1, 9.4
    
    示例：
        >>> log_loading_complete(3, 1)
        [2026-03-03 10:30:00] [INFO] [DynamicLoader] ========================================
        [2026-03-03 10:30:00] [INFO] [DynamicLoader] 模块加载完成
        [2026-03-03 10:30:00] [INFO] [DynamicLoader] 激活模块: 3 个 | 跳过模块: 1 个
        [2026-03-03 10:30:00] [INFO] [DynamicLoader] ========================================
    """
    timestamp = _format_timestamp()
    separator = "=" * 40
    print(f"[{timestamp}] [INFO] [{component}] {separator}")
    print(f"[{timestamp}] [INFO] [{component}] 模块加载完成")
    print(f"[{timestamp}] [INFO] [{component}] 激活模块: {activated_count} 个 | 跳过模块: {skipped_count} 个")
    print(f"[{timestamp}] [INFO] [{component}] {separator}")


def log_section_separator(component: str = "DynamicLoader") -> None:
    """
    输出分隔线
    
    Args:
        component: 组件名称，默认为 "DynamicLoader"
    
    需求追溯：需求 9.4
    
    示例：
        >>> log_section_separator()
        [2026-03-03 10:30:00] [INFO] [DynamicLoader] ----------------------------------------
    """
    timestamp = _format_timestamp()
    separator = "-" * 40
    print(f"[{timestamp}] [INFO] [{component}] {separator}")
