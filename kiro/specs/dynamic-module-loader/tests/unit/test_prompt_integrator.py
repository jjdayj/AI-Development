"""
Prompt 整合器单元测试

测试 Prompt 整合器的各种功能，包括内容整合、格式化、验证等。

需求追溯：需求 15.3
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from src.prompt_integrator import (
    PromptIntegrator, 
    integrate_steering_contents,
    get_integration_summary,
    validate_integration_input
)


class TestPromptIntegrator:
    """Prompt 整合器测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.integrator = PromptIntegrator()
        
        # 测试数据
        self.sample_contents = [
            ("workflow", "v1.0", 200, {"always": True}, "# Workflow Rules\n\nWorkflow content here."),
            ("ai-dev", "v1.0", 100, {"directory_match": ["src/*"]}, "# AI Dev Rules\n\nAI development content."),
            ("git-commit", "v1.0", 80, {"file_type_match": [".py", ".js"]}, "# Git Commit Rules\n\nGit commit content.")
        ]
    
    def test_init(self):
        """测试初始化"""
        integrator = PromptIntegrator()
        assert integrator is not None
    
    def test_integrate_prompts_with_content(self):
        """测试有内容的 Prompt 整合"""
        result = self.integrator.integrate_prompts(self.sample_contents)
        
        # 验证基本结构
        assert "# Kiro Prompt 层级结构" in result
        assert "# 激活的模块" in result
        assert "# 模块 Steering 规则" in result
        assert "# Prompt 整合完成" in result
        
        # 验证模块内容
        assert "workflow" in result
        assert "ai-dev" in result
        assert "git-commit" in result
        
        # 验证优先级信息
        assert "优先级: 200" in result
        assert "优先级: 100" in result
        assert "优先级: 80" in result
        
        # 验证激活条件
        assert "始终激活" in result
        assert "目录匹配: src/*" in result
        assert "文件类型: .py, .js" in result
    
    def test_integrate_prompts_empty_content(self):
        """测试空内容的 Prompt 整合"""
        result = self.integrator.integrate_prompts([])
        
        # 验证空 Prompt 结构
        assert "# Kiro Prompt 层级结构" in result
        assert "当前没有激活的模块" in result
        assert "激活模块数**: 0" in result
        assert "当前没有激活的模块需要整合" in result
    
    def test_integrate_prompts_without_hierarchy(self):
        """测试不包含层级结构的整合"""
        result = self.integrator.integrate_prompts(
            self.sample_contents, 
            include_hierarchy=False
        )
        
        # 不应包含层级结构
        assert "# Kiro Prompt 层级结构" not in result
        
        # 应包含其他部分
        assert "# 激活的模块" in result
        assert "# 模块 Steering 规则" in result
    
    def test_integrate_prompts_without_module_list(self):
        """测试不包含模块列表的整合"""
        result = self.integrator.integrate_prompts(
            self.sample_contents, 
            include_module_list=False
        )
        
        # 不应包含模块列表
        assert "# 激活的模块" not in result
        
        # 应包含其他部分
        assert "# Kiro Prompt 层级结构" in result
        assert "# 模块 Steering 规则" in result
    
    def test_integrate_prompts_minimal(self):
        """测试最小化整合（不包含层级和模块列表）"""
        result = self.integrator.integrate_prompts(
            self.sample_contents,
            include_hierarchy=False,
            include_module_list=False
        )
        
        # 只应包含内容和完成标记
        assert "# Kiro Prompt 层级结构" not in result
        assert "# 激活的模块" not in result
        assert "# 模块 Steering 规则" in result
        assert "# Prompt 整合完成" in result
    
    def test_create_hierarchy_section(self):
        """测试层级结构部分创建"""
        result = self.integrator._create_hierarchy_section()
        
        assert "# Kiro Prompt 层级结构" in result
        assert "L0 (顶层入口)" in result
        assert "L1 (加载器逻辑)" in result
        assert "L2 (模块规则)" in result
        assert "优先级规则" in result
    
    def test_create_module_list_section_with_content(self):
        """测试有内容的模块列表部分创建"""
        result = self.integrator._create_module_list_section(self.sample_contents)
        
        assert "# 激活的模块" in result
        assert "共激活 3 个模块" in result
        assert "1. **workflow**" in result
        assert "2. **ai-dev**" in result
        assert "3. **git-commit**" in result
    
    def test_create_module_list_section_empty(self):
        """测试空模块列表部分创建"""
        result = self.integrator._create_module_list_section([])
        
        assert "# 激活的模块" in result
        assert "当前没有激活的模块" in result
    
    def test_create_content_section_with_content(self):
        """测试有内容的 Steering 内容部分创建"""
        result = self.integrator._create_content_section(self.sample_contents)
        
        assert "# 模块 Steering 规则" in result
        assert "## workflow (v1.0) - 优先级 200" in result
        assert "## ai-dev (v1.0) - 优先级 100" in result
        assert "## git-commit (v1.0) - 优先级 80" in result
        
        # 验证内容
        assert "Workflow content here." in result
        assert "AI development content." in result
        assert "Git commit content." in result
    
    def test_create_content_section_empty(self):
        """测试空内容部分创建"""
        result = self.integrator._create_content_section([])
        
        assert result == ""
    
    def test_create_content_section_with_empty_module_content(self):
        """测试包含空模块内容的内容部分创建"""
        empty_contents = [
            ("empty-module", "v1.0", 100, {"always": True}, ""),
            ("whitespace-module", "v1.0", 90, {"always": True}, "   \n  \t  ")
        ]
        
        result = self.integrator._create_content_section(empty_contents)
        
        assert "*此模块没有 Steering 内容*" in result
        # 应该出现两次（两个空模块）
        assert result.count("*此模块没有 Steering 内容*") == 2
    
    def test_create_completion_section(self):
        """测试完成标记部分创建"""
        with patch('src.prompt_integrator.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "2026-03-03 12:00:00"
            
            result = self.integrator._create_completion_section(3)
            
            assert "# Prompt 整合完成" in result
            assert "整合时间**: 2026-03-03 12:00:00" in result
            assert "激活模块数**: 3" in result
            assert "整合状态**: ✅ 完成" in result
    
    def test_format_activation_conditions_always(self):
        """测试 always 条件格式化"""
        conditions = {"always": True}
        result = self.integrator._format_activation_conditions(conditions)
        assert result == "始终激活"
    
    def test_format_activation_conditions_directory_match(self):
        """测试目录匹配条件格式化"""
        # 单个模式
        conditions = {"directory_match": "src/*"}
        result = self.integrator._format_activation_conditions(conditions)
        assert result == "目录匹配: src/*"
        
        # 多个模式
        conditions = {"directory_match": ["src/*", "tests/*"]}
        result = self.integrator._format_activation_conditions(conditions)
        assert result == "目录匹配: src/*, tests/*"
    
    def test_format_activation_conditions_file_type_match(self):
        """测试文件类型匹配条件格式化"""
        # 单个类型
        conditions = {"file_type_match": ".py"}
        result = self.integrator._format_activation_conditions(conditions)
        assert result == "文件类型: .py"
        
        # 多个类型
        conditions = {"file_type_match": [".py", ".js", ".ts"]}
        result = self.integrator._format_activation_conditions(conditions)
        assert result == "文件类型: .py, .js, .ts"
    
    def test_format_activation_conditions_and_logic(self):
        """测试 AND 逻辑条件格式化"""
        conditions = {
            "and": [
                {"always": True},
                {"directory_match": "src/*"}
            ]
        }
        result = self.integrator._format_activation_conditions(conditions)
        assert result == "AND(始终激活, 目录匹配: src/*)"
    
    def test_format_activation_conditions_or_logic(self):
        """测试 OR 逻辑条件格式化"""
        conditions = {
            "or": [
                {"file_type_match": ".py"},
                {"directory_match": "tests/*"}
            ]
        }
        result = self.integrator._format_activation_conditions(conditions)
        assert result == "OR(文件类型: .py, 目录匹配: tests/*)"
    
    def test_format_activation_conditions_empty(self):
        """测试空条件格式化"""
        result = self.integrator._format_activation_conditions({})
        assert result == "无条件"
        
        result = self.integrator._format_activation_conditions(None)
        assert result == "无条件"
    
    def test_format_activation_conditions_custom(self):
        """测试自定义条件格式化"""
        conditions = {"custom_field": "custom_value"}
        result = self.integrator._format_activation_conditions(conditions)
        assert result == "自定义条件"
    
    def test_get_integration_summary_with_content(self):
        """测试有内容的整合摘要"""
        result = self.integrator.get_integration_summary(self.sample_contents)
        
        assert result['total_modules'] == 3
        assert result['total_content_length'] > 0
        assert len(result['modules']) == 3
        assert result['priority_range']['min'] == 80
        assert result['priority_range']['max'] == 200
        assert 'integration_time' in result
        
        # 验证模块信息
        modules = result['modules']
        assert modules[0]['name'] == 'workflow'
        assert modules[0]['priority'] == 200
        assert modules[1]['name'] == 'ai-dev'
        assert modules[2]['name'] == 'git-commit'
    
    def test_get_integration_summary_empty(self):
        """测试空内容的整合摘要"""
        result = self.integrator.get_integration_summary([])
        
        assert result['total_modules'] == 0
        assert result['total_content_length'] == 0
        assert result['modules'] == []
        assert result['priority_range'] is None
        assert 'integration_time' in result
    
    def test_validate_integration_input_valid(self):
        """测试有效输入验证"""
        valid, error = self.integrator.validate_integration_input(self.sample_contents)
        
        assert valid is True
        assert error is None
    
    def test_validate_integration_input_invalid_type(self):
        """测试无效类型输入验证"""
        valid, error = self.integrator.validate_integration_input("not a list")
        
        assert valid is False
        assert "必须是列表类型" in error
    
    def test_validate_integration_input_invalid_tuple_length(self):
        """测试无效元组长度输入验证"""
        invalid_input = [("module", "v1.0", 100)]  # 缺少元素
        
        valid, error = self.integrator.validate_integration_input(invalid_input)
        
        assert valid is False
        assert "必须是包含 5 个元素的元组" in error
    
    def test_validate_integration_input_invalid_module_name(self):
        """测试无效模块名称输入验证"""
        invalid_input = [("", "v1.0", 100, {}, "content")]  # 空模块名
        
        valid, error = self.integrator.validate_integration_input(invalid_input)
        
        assert valid is False
        assert "模块名称必须是非空字符串" in error
    
    def test_validate_integration_input_invalid_version(self):
        """测试无效版本输入验证"""
        invalid_input = [("module", "", 100, {}, "content")]  # 空版本
        
        valid, error = self.integrator.validate_integration_input(invalid_input)
        
        assert valid is False
        assert "版本必须是非空字符串" in error
    
    def test_validate_integration_input_invalid_priority(self):
        """测试无效优先级输入验证"""
        invalid_input = [("module", "v1.0", "100", {}, "content")]  # 字符串优先级
        
        valid, error = self.integrator.validate_integration_input(invalid_input)
        
        assert valid is False
        assert "优先级必须是整数" in error
    
    def test_validate_integration_input_invalid_conditions(self):
        """测试无效条件输入验证"""
        invalid_input = [("module", "v1.0", 100, "not dict", "content")]  # 非字典条件
        
        valid, error = self.integrator.validate_integration_input(invalid_input)
        
        assert valid is False
        assert "激活条件必须是字典" in error
    
    def test_validate_integration_input_invalid_content(self):
        """测试无效内容输入验证"""
        invalid_input = [("module", "v1.0", 100, {}, 123)]  # 非字符串内容
        
        valid, error = self.integrator.validate_integration_input(invalid_input)
        
        assert valid is False
        assert "内容必须是字符串" in error
    
    def test_integration_order_preservation(self):
        """测试整合顺序保持"""
        # 按优先级排序的内容
        ordered_contents = [
            ("high-priority", "v1.0", 300, {"always": True}, "High priority content"),
            ("medium-priority", "v1.0", 200, {"always": True}, "Medium priority content"),
            ("low-priority", "v1.0", 100, {"always": True}, "Low priority content")
        ]
        
        result = self.integrator.integrate_prompts(ordered_contents)
        
        # 验证顺序：high -> medium -> low
        high_pos = result.find("high-priority")
        medium_pos = result.find("medium-priority")
        low_pos = result.find("low-priority")
        
        assert high_pos < medium_pos < low_pos
    
    def test_content_escaping_and_formatting(self):
        """测试内容转义和格式化"""
        special_contents = [
            ("special", "v1.0", 100, {"always": True}, 
             "# Special Content\n\n**Bold** and *italic* text.\n\n```code block```")
        ]
        
        result = self.integrator.integrate_prompts(special_contents)
        
        # 验证特殊字符和格式保持
        assert "# Special Content" in result
        assert "**Bold**" in result
        assert "*italic*" in result
        assert "```code block```" in result


class TestConvenienceFunctions:
    """便捷函数测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.sample_contents = [
            ("workflow", "v1.0", 200, {"always": True}, "Workflow content"),
            ("ai-dev", "v1.0", 100, {"directory_match": ["src/*"]}, "AI dev content")
        ]
    
    def test_integrate_steering_contents_convenience(self):
        """测试 Steering 内容整合便捷函数"""
        result = integrate_steering_contents(self.sample_contents)
        
        assert "# Kiro Prompt 层级结构" in result
        assert "# 激活的模块" in result
        assert "workflow" in result
        assert "ai-dev" in result
    
    def test_integrate_steering_contents_convenience_options(self):
        """测试带选项的 Steering 内容整合便捷函数"""
        result = integrate_steering_contents(
            self.sample_contents,
            include_hierarchy=False,
            include_module_list=False
        )
        
        assert "# Kiro Prompt 层级结构" not in result
        assert "# 激活的模块" not in result
        assert "# 模块 Steering 规则" in result
    
    def test_get_integration_summary_convenience(self):
        """测试整合摘要便捷函数"""
        result = get_integration_summary(self.sample_contents)
        
        assert result['total_modules'] == 2
        assert len(result['modules']) == 2
        assert 'integration_time' in result
    
    def test_validate_integration_input_convenience(self):
        """测试输入验证便捷函数"""
        valid, error = validate_integration_input(self.sample_contents)
        
        assert valid is True
        assert error is None
        
        # 测试无效输入
        valid, error = validate_integration_input("invalid")
        
        assert valid is False
        assert error is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])