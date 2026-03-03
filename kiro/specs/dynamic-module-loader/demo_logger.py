"""
日志输出器演示脚本

演示 logger.py 模块的各种功能。
"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from logger import (
    log_info,
    log_warning,
    log_error,
    log_module_status,
    log_loading_start,
    log_loading_complete,
    log_section_separator
)


def demo_basic_logging():
    """演示基本日志功能"""
    print("\n=== 演示 1: 基本日志功能 ===\n")
    
    log_info("系统启动成功")
    log_warning("配置文件不存在，使用默认配置")
    log_error("无法连接到数据库")


def demo_module_status():
    """演示模块状态日志"""
    print("\n=== 演示 2: 模块状态日志 ===\n")
    
    modules = [
        {"name": "workflow", "version": "v1.0", "priority": 200},
        {"name": "ai-dev", "version": "v1.0", "priority": 100},
        {"name": "git-commit", "version": "v1.0", "priority": 80},
    ]
    
    for module in modules:
        log_module_status(module, "已激活")


def demo_loading_sequence():
    """演示完整的加载流程"""
    print("\n=== 演示 3: 完整加载流程 ===\n")
    
    # 开始加载
    log_loading_start(4)
    
    # 模块 1: workflow
    module1 = {"name": "workflow", "version": "v1.0", "priority": 200}
    log_module_status(module1, "已激活")
    
    # 模块 2: ai-dev
    module2 = {"name": "ai-dev", "version": "v1.0", "priority": 100}
    log_module_status(module2, "已激活")
    
    # 模块 3: git-commit
    module3 = {"name": "git-commit", "version": "v1.0", "priority": 80}
    log_module_status(module3, "已跳过")
    
    # 模块 4: git-rollback
    module4 = {"name": "git-rollback", "version": "v1.0", "priority": 70}
    log_module_status(module4, "已激活")
    
    # 完成加载
    log_loading_complete(3, 1)


def demo_error_handling():
    """演示错误处理流程"""
    print("\n=== 演示 4: 错误处理流程 ===\n")
    
    log_info("开始读取配置文件: .kiro/config.yaml")
    log_warning("配置文件不存在，使用默认配置")
    
    log_section_separator()
    
    log_info("开始加载模块: test-module")
    log_error("模块配置文件格式错误: .kiro/modules/test-module/v1.0/config.yaml")
    log_warning("跳过模块: test-module")
    
    log_section_separator()
    
    log_info("继续处理其他模块")


def demo_custom_component():
    """演示自定义组件名称"""
    print("\n=== 演示 5: 自定义组件名称 ===\n")
    
    log_info("配置读取器启动", component="ConfigReader")
    log_info("激活状态计算器启动", component="ActivationCalculator")
    log_info("依赖校验器启动", component="DependencyValidator")
    log_info("优先级排序器启动", component="PrioritySorter")
    log_info("Steering 加载器启动", component="SteeringLoader")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("日志输出器功能演示")
    print("=" * 80)
    
    demo_basic_logging()
    demo_module_status()
    demo_loading_sequence()
    demo_error_handling()
    demo_custom_component()
    
    print("\n" + "=" * 80)
    print("演示完成")
    print("=" * 80 + "\n")
