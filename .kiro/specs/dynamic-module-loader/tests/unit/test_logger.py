"""
单元测试：日志输出器

测试 logger.py 模块的所有功能。

需求追溯：
- 需求 9.1: 实现日志输出功能
- 需求 9.2: 实现日志级别（INFO, WARNING, ERROR）
- 需求 9.3: 实现模块状态日志
- 需求 9.4: 使用清晰的日志格式
"""

import pytest
import sys
import os
from io import StringIO
from datetime import datetime
from unittest.mock import patch

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from logger import (
    log_info,
    log_warning,
    log_error,
    log_module_status,
    log_loading_start,
    log_loading_complete,
    log_section_separator,
    _format_timestamp
)


class TestTimestampFormatting:
    """测试时间戳格式化功能"""
    
    def test_timestamp_format(self):
        """测试时间戳格式是否正确"""
        timestamp = _format_timestamp()
        
        # 验证格式：YYYY-MM-DD HH:MM:SS
        assert len(timestamp) == 19
        assert timestamp[4] == '-'
        assert timestamp[7] == '-'
        assert timestamp[10] == ' '
        assert timestamp[13] == ':'
        assert timestamp[16] == ':'
    
    def test_timestamp_is_current(self):
        """测试时间戳是否为当前时间"""
        timestamp = _format_timestamp()
        current = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 允许 1 秒的误差
        assert timestamp[:16] == current[:16]


class TestLogInfo:
    """测试 log_info 函数"""
    
    def test_log_info_basic(self, capsys):
        """测试基本信息日志输出"""
        log_info("测试消息")
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证日志格式
        assert "[INFO]" in output
        assert "[DynamicLoader]" in output
        assert "测试消息" in output
    
    def test_log_info_custom_component(self, capsys):
        """测试自定义组件名称"""
        log_info("测试消息", component="TestComponent")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "[TestComponent]" in output
        assert "[DynamicLoader]" not in output
    
    def test_log_info_empty_message(self, capsys):
        """测试空消息"""
        log_info("")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "[INFO]" in output
        assert len(output.strip()) > 0
    
    def test_log_info_special_characters(self, capsys):
        """测试特殊字符"""
        log_info("消息包含特殊字符: !@#$%^&*()")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "!@#$%^&*()" in output
    
    def test_log_info_multiline_message(self, capsys):
        """测试多行消息"""
        log_info("第一行\n第二行\n第三行")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "第一行" in output
        assert "第二行" in output
        assert "第三行" in output


class TestLogWarning:
    """测试 log_warning 函数"""
    
    def test_log_warning_basic(self, capsys):
        """测试基本警告日志输出"""
        log_warning("警告消息")
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证日志格式
        assert "[WARNING]" in output
        assert "[DynamicLoader]" in output
        assert "警告消息" in output
    
    def test_log_warning_custom_component(self, capsys):
        """测试自定义组件名称"""
        log_warning("警告消息", component="TestComponent")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "[TestComponent]" in output
    
    def test_log_warning_long_message(self, capsys):
        """测试长消息"""
        long_message = "这是一个很长的警告消息" * 10
        log_warning(long_message)
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert long_message in output


class TestLogError:
    """测试 log_error 函数"""
    
    def test_log_error_basic(self, capsys):
        """测试基本错误日志输出"""
        log_error("错误消息")
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证日志格式
        assert "[ERROR]" in output
        assert "[DynamicLoader]" in output
        assert "错误消息" in output
    
    def test_log_error_custom_component(self, capsys):
        """测试自定义组件名称"""
        log_error("错误消息", component="TestComponent")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "[TestComponent]" in output
    
    def test_log_error_with_exception_info(self, capsys):
        """测试包含异常信息的错误日志"""
        try:
            raise ValueError("测试异常")
        except ValueError as e:
            log_error(f"发生错误: {str(e)}")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "测试异常" in output


class TestLogModuleStatus:
    """测试 log_module_status 函数"""
    
    def test_log_module_status_basic(self, capsys):
        """测试基本模块状态日志"""
        module = {
            "name": "workflow",
            "version": "v1.0",
            "priority": 200
        }
        log_module_status(module, "已激活")
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证日志格式
        assert "[INFO]" in output
        assert "模块: workflow" in output
        assert "版本: v1.0" in output
        assert "优先级: 200" in output
        assert "状态: 已激活" in output
    
    def test_log_module_status_missing_fields(self, capsys):
        """测试缺少字段的模块信息"""
        module = {}
        log_module_status(module, "已跳过")
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 应该使用默认值
        assert "模块: 未知" in output
        assert "版本: 未知" in output
        assert "优先级: 0" in output
        assert "状态: 已跳过" in output
    
    def test_log_module_status_partial_fields(self, capsys):
        """测试部分字段的模块信息"""
        module = {
            "name": "ai-dev",
            "version": "v1.0"
            # 缺少 priority
        }
        log_module_status(module, "加载成功")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "模块: ai-dev" in output
        assert "版本: v1.0" in output
        assert "优先级: 0" in output
    
    def test_log_module_status_custom_component(self, capsys):
        """测试自定义组件名称"""
        module = {
            "name": "test-module",
            "version": "v2.0",
            "priority": 150
        }
        log_module_status(module, "测试中", component="TestComponent")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "[TestComponent]" in output
    
    def test_log_module_status_various_statuses(self, capsys):
        """测试各种状态描述"""
        module = {
            "name": "test-module",
            "version": "v1.0",
            "priority": 100
        }
        
        statuses = ["已激活", "已跳过", "加载成功", "加载失败", "依赖缺失", "循环依赖"]
        
        for status in statuses:
            log_module_status(module, status)
            captured = capsys.readouterr()
            output = captured.out
            assert f"状态: {status}" in output


class TestLogLoadingStart:
    """测试 log_loading_start 函数"""
    
    def test_log_loading_start_basic(self, capsys):
        """测试加载开始日志"""
        log_loading_start(4)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证包含分隔线
        assert "=" * 40 in output
        # 验证包含模块数量
        assert "共 4 个模块" in output
        # 验证包含开始消息
        assert "开始加载模块" in output
    
    def test_log_loading_start_zero_modules(self, capsys):
        """测试零个模块的情况"""
        log_loading_start(0)
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "共 0 个模块" in output
    
    def test_log_loading_start_many_modules(self, capsys):
        """测试大量模块的情况"""
        log_loading_start(100)
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "共 100 个模块" in output
    
    def test_log_loading_start_custom_component(self, capsys):
        """测试自定义组件名称"""
        log_loading_start(5, component="TestComponent")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "[TestComponent]" in output


class TestLogLoadingComplete:
    """测试 log_loading_complete 函数"""
    
    def test_log_loading_complete_basic(self, capsys):
        """测试加载完成日志"""
        log_loading_complete(3, 1)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证包含分隔线
        assert "=" * 40 in output
        # 验证包含完成消息
        assert "模块加载完成" in output
        # 验证包含统计信息
        assert "激活模块: 3 个" in output
        assert "跳过模块: 1 个" in output
    
    def test_log_loading_complete_all_activated(self, capsys):
        """测试所有模块都激活的情况"""
        log_loading_complete(5, 0)
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "激活模块: 5 个" in output
        assert "跳过模块: 0 个" in output
    
    def test_log_loading_complete_all_skipped(self, capsys):
        """测试所有模块都跳过的情况"""
        log_loading_complete(0, 5)
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "激活模块: 0 个" in output
        assert "跳过模块: 5 个" in output
    
    def test_log_loading_complete_custom_component(self, capsys):
        """测试自定义组件名称"""
        log_loading_complete(2, 2, component="TestComponent")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "[TestComponent]" in output


class TestLogSectionSeparator:
    """测试 log_section_separator 函数"""
    
    def test_log_section_separator_basic(self, capsys):
        """测试分隔线输出"""
        log_section_separator()
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证包含分隔线
        assert "-" * 40 in output
        # 验证包含日志级别
        assert "[INFO]" in output
    
    def test_log_section_separator_custom_component(self, capsys):
        """测试自定义组件名称"""
        log_section_separator(component="TestComponent")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "[TestComponent]" in output


class TestLogFormatConsistency:
    """测试日志格式一致性"""
    
    def test_all_logs_have_timestamp(self, capsys):
        """测试所有日志都包含时间戳"""
        log_info("测试")
        log_warning("测试")
        log_error("测试")
        
        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        
        # 每行都应该以时间戳开始
        for line in lines:
            assert line.startswith('[')
            # 验证时间戳格式
            assert '] [' in line
    
    def test_all_logs_have_level(self, capsys):
        """测试所有日志都包含级别"""
        log_info("测试")
        log_warning("测试")
        log_error("测试")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "[INFO]" in output
        assert "[WARNING]" in output
        assert "[ERROR]" in output
    
    def test_all_logs_have_component(self, capsys):
        """测试所有日志都包含组件名称"""
        log_info("测试")
        log_warning("测试")
        log_error("测试")
        
        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        
        # 每行都应该包含组件名称
        for line in lines:
            assert "[DynamicLoader]" in line


class TestLogIntegration:
    """测试日志功能的集成场景"""
    
    def test_typical_loading_sequence(self, capsys):
        """测试典型的加载流程日志序列"""
        # 模拟完整的加载流程
        log_loading_start(3)
        
        module1 = {"name": "workflow", "version": "v1.0", "priority": 200}
        log_module_status(module1, "已激活")
        
        module2 = {"name": "ai-dev", "version": "v1.0", "priority": 100}
        log_module_status(module2, "已激活")
        
        module3 = {"name": "git-commit", "version": "v1.0", "priority": 80}
        log_module_status(module3, "已跳过")
        
        log_loading_complete(2, 1)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证完整流程
        assert "开始加载模块" in output
        assert "workflow" in output
        assert "ai-dev" in output
        assert "git-commit" in output
        assert "模块加载完成" in output
        assert "激活模块: 2 个" in output
        assert "跳过模块: 1 个" in output
    
    def test_error_handling_sequence(self, capsys):
        """测试错误处理流程的日志序列"""
        log_info("开始读取配置文件")
        log_warning("配置文件不存在，使用默认配置")
        log_error("无法加载模块: test-module")
        log_info("继续处理其他模块")
        
        captured = capsys.readouterr()
        output = captured.out
        
        # 验证错误处理流程
        assert "[INFO]" in output
        assert "[WARNING]" in output
        assert "[ERROR]" in output
        assert "开始读取配置文件" in output
        assert "配置文件不存在" in output
        assert "无法加载模块" in output
        assert "继续处理其他模块" in output


class TestEdgeCases:
    """测试边缘情况"""
    
    def test_very_long_module_name(self, capsys):
        """测试非常长的模块名称"""
        module = {
            "name": "a" * 100,
            "version": "v1.0",
            "priority": 100
        }
        log_module_status(module, "已激活")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "a" * 100 in output
    
    def test_unicode_characters(self, capsys):
        """测试 Unicode 字符"""
        log_info("测试中文、日本語、한국어、Emoji 😀")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "测试中文" in output
        assert "日本語" in output
        assert "한국어" in output
        assert "😀" in output
    
    def test_negative_priority(self, capsys):
        """测试负数优先级"""
        module = {
            "name": "test-module",
            "version": "v1.0",
            "priority": -100
        }
        log_module_status(module, "已激活")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "优先级: -100" in output
    
    def test_zero_priority(self, capsys):
        """测试零优先级"""
        module = {
            "name": "test-module",
            "version": "v1.0",
            "priority": 0
        }
        log_module_status(module, "已激活")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "优先级: 0" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
