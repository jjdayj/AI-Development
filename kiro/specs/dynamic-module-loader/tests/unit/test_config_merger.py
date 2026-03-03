"""
单元测试：配置合并器

测试 config_merger.py 模块的所有功能。

需求追溯：
- 隐含需求：配置冲突处理
"""

import pytest
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from config_merger import (
    merge_configs,
    deep_merge,
    validate_merged_config,
    merge_multiple_configs,
    get_merge_summary
)


class TestMergeConfigs:
    """测试 merge_configs 函数"""
    
    def test_merge_configs_basic(self):
        """测试基本配置合并"""
        top_config = {
            "enabled": True,
            "version": "v1.0",
            "priority": 200
        }
        module_config = {
            "activation_conditions": {"always": True}
        }
        
        result = merge_configs(top_config, module_config, "test-module")
        
        # 验证顶层配置优先
        assert result["enabled"] == True
        assert result["version"] == "v1.0"
        assert result["priority"] == 200
        
        # 验证模块配置保留
        assert result["activation_conditions"] == {"always": True}
    
    def test_merge_configs_top_level_priority(self):
        """测试顶层配置优先规则"""
        top_config = {
            "enabled": False,
            "version": "v2.0",
            "priority": 100
        }
        module_config = {
            "enabled": True,  # 应该被顶层配置覆盖
            "version": "v1.0",  # 应该被顶层配置覆盖
            "priority": 200,  # 应该被顶层配置覆盖
            "activation_conditions": {"always": True}
        }
        
        result = merge_configs(top_config, module_config, "test-module")
        
        # 验证顶层配置优先
        assert result["enabled"] == False
        assert result["version"] == "v2.0"
        assert result["priority"] == 100
    
    def test_merge_configs_module_activation_priority(self):
        """测试模块配置的激活条件优先"""
        top_config = {
            "enabled": True,
            "version": "v1.0",
            "priority": 200,
            "activation_conditions": {"always": False}  # 应该被模块配置覆盖
        }
        module_config = {
            "activation_conditions": {
                "directory_match": [".kiro/*"]
            }
        }
        
        result = merge_configs(top_config, module_config, "test-module")
        
        # 验证模块配置的激活条件优先
        assert result["activation_conditions"] == {
            "directory_match": [".kiro/*"]
        }
    
    def test_merge_configs_custom_fields(self):
        """测试自定义字段合并"""
        top_config = {
            "enabled": True,
            "version": "v1.0",
            "priority": 200,
            "custom_field": "top_value"
        }
        module_config = {
            "activation_conditions": {"always": True},
            "custom_field": "module_value",
            "module_specific": "value"
        }
        
        result = merge_configs(top_config, module_config, "test-module")
        
        # 验证自定义字段：模块配置覆盖顶层配置
        assert result["custom_field"] == "module_value"
        # 验证模块特定字段保留
        assert result["module_specific"] == "value"
    
    def test_merge_configs_nested_dict(self):
        """测试嵌套字典合并"""
        top_config = {
            "enabled": True,
            "version": "v1.0",
            "priority": 200,
            "nested": {
                "a": 1,
                "b": 2
            }
        }
        module_config = {
            "activation_conditions": {"always": True},
            "nested": {
                "b": 20,
                "c": 3
            }
        }
        
        result = merge_configs(top_config, module_config, "test-module")
        
        # 验证嵌套字典深度合并
        assert result["nested"]["a"] == 1  # 来自顶层配置
        assert result["nested"]["b"] == 20  # 模块配置覆盖
        assert result["nested"]["c"] == 3  # 来自模块配置
    
    def test_merge_configs_empty_module_config(self):
        """测试空模块配置"""
        top_config = {
            "enabled": True,
            "version": "v1.0",
            "priority": 200
        }
        module_config = {}
        
        result = merge_configs(top_config, module_config, "test-module")
        
        # 验证顶层配置被应用
        assert result["enabled"] == True
        assert result["version"] == "v1.0"
        assert result["priority"] == 200
    
    def test_merge_configs_empty_top_config(self):
        """测试空顶层配置"""
        top_config = {}
        module_config = {
            "activation_conditions": {"always": True},
            "custom_field": "value"
        }
        
        result = merge_configs(top_config, module_config, "test-module")
        
        # 验证模块配置被保留
        assert result["activation_conditions"] == {"always": True}
        assert result["custom_field"] == "value"
    
    def test_merge_configs_no_mutation(self):
        """测试不修改原始配置"""
        top_config = {
            "enabled": True,
            "version": "v1.0",
            "priority": 200
        }
        module_config = {
            "activation_conditions": {"always": True}
        }
        
        # 保存原始值
        original_top = top_config.copy()
        original_module = module_config.copy()
        
        result = merge_configs(top_config, module_config, "test-module")
        
        # 验证原始配置未被修改
        assert top_config == original_top
        assert module_config == original_module


class TestDeepMerge:
    """测试 deep_merge 函数"""
    
    def test_deep_merge_simple(self):
        """测试简单字典合并"""
        base = {"a": 1, "b": 2}
        override = {"b": 20, "c": 3}
        
        result = deep_merge(base, override)
        
        assert result == {"a": 1, "b": 20, "c": 3}
    
    def test_deep_merge_nested(self):
        """测试嵌套字典合并"""
        base = {
            "a": 1,
            "b": {
                "c": 2,
                "d": 3
            }
        }
        override = {
            "b": {
                "c": 20,
                "e": 4
            },
            "f": 5
        }
        
        result = deep_merge(base, override)
        
        assert result == {
            "a": 1,
            "b": {
                "c": 20,
                "d": 3,
                "e": 4
            },
            "f": 5
        }
    
    def test_deep_merge_deeply_nested(self):
        """测试深层嵌套合并"""
        base = {
            "level1": {
                "level2": {
                    "level3": {
                        "a": 1,
                        "b": 2
                    }
                }
            }
        }
        override = {
            "level1": {
                "level2": {
                    "level3": {
                        "b": 20,
                        "c": 3
                    }
                }
            }
        }
        
        result = deep_merge(base, override)
        
        assert result["level1"]["level2"]["level3"]["a"] == 1
        assert result["level1"]["level2"]["level3"]["b"] == 20
        assert result["level1"]["level2"]["level3"]["c"] == 3
    
    def test_deep_merge_list_override(self):
        """测试列表覆盖（不合并）"""
        base = {"a": [1, 2, 3]}
        override = {"a": [4, 5]}
        
        result = deep_merge(base, override)
        
        # 列表应该被完全覆盖，不合并
        assert result["a"] == [4, 5]
    
    def test_deep_merge_empty_base(self):
        """测试空基础字典"""
        base = {}
        override = {"a": 1, "b": 2}
        
        result = deep_merge(base, override)
        
        assert result == {"a": 1, "b": 2}
    
    def test_deep_merge_empty_override(self):
        """测试空覆盖字典"""
        base = {"a": 1, "b": 2}
        override = {}
        
        result = deep_merge(base, override)
        
        assert result == {"a": 1, "b": 2}
    
    def test_deep_merge_no_mutation(self):
        """测试不修改原始字典"""
        base = {"a": 1, "b": {"c": 2}}
        override = {"b": {"c": 20}}
        
        original_base = {"a": 1, "b": {"c": 2}}
        original_override = {"b": {"c": 20}}
        
        result = deep_merge(base, override)
        
        # 验证原始字典未被修改
        assert base == original_base
        assert override == original_override


class TestValidateMergedConfig:
    """测试 validate_merged_config 函数"""
    
    def test_validate_valid_config(self):
        """测试有效配置"""
        config = {
            "enabled": True,
            "version": "v1.0",
            "priority": 200
        }
        
        is_valid, errors = validate_merged_config(config)
        
        assert is_valid == True
        assert errors == []
    
    def test_validate_missing_enabled(self):
        """测试缺少 enabled 字段"""
        config = {
            "version": "v1.0",
            "priority": 200
        }
        
        is_valid, errors = validate_merged_config(config)
        
        assert is_valid == False
        assert "缺少必需字段: enabled" in errors
    
    def test_validate_missing_version(self):
        """测试缺少 version 字段"""
        config = {
            "enabled": True,
            "priority": 200
        }
        
        is_valid, errors = validate_merged_config(config)
        
        assert is_valid == False
        assert "缺少必需字段: version" in errors
    
    def test_validate_missing_priority(self):
        """测试缺少 priority 字段"""
        config = {
            "enabled": True,
            "version": "v1.0"
        }
        
        is_valid, errors = validate_merged_config(config)
        
        assert is_valid == False
        assert "缺少必需字段: priority" in errors
    
    def test_validate_invalid_enabled_type(self):
        """测试 enabled 字段类型错误"""
        config = {
            "enabled": "true",  # 应该是布尔值
            "version": "v1.0",
            "priority": 200
        }
        
        is_valid, errors = validate_merged_config(config)
        
        assert is_valid == False
        assert any("enabled" in error and "布尔值" in error for error in errors)
    
    def test_validate_invalid_priority_type(self):
        """测试 priority 字段类型错误"""
        config = {
            "enabled": True,
            "version": "v1.0",
            "priority": "200"  # 应该是数字
        }
        
        is_valid, errors = validate_merged_config(config)
        
        assert is_valid == False
        assert any("priority" in error and "数字" in error for error in errors)
    
    def test_validate_invalid_version_type(self):
        """测试 version 字段类型错误"""
        config = {
            "enabled": True,
            "version": 1.0,  # 应该是字符串
            "priority": 200
        }
        
        is_valid, errors = validate_merged_config(config)
        
        assert is_valid == False
        assert any("version" in error and "字符串" in error for error in errors)
    
    def test_validate_multiple_errors(self):
        """测试多个错误"""
        config = {
            "enabled": "true",
            "priority": "200"
        }
        
        is_valid, errors = validate_merged_config(config)
        
        assert is_valid == False
        assert len(errors) >= 3  # 缺少 version + enabled 类型错误 + priority 类型错误
    
    def test_validate_float_priority(self):
        """测试浮点数优先级（应该有效）"""
        config = {
            "enabled": True,
            "version": "v1.0",
            "priority": 200.5
        }
        
        is_valid, errors = validate_merged_config(config)
        
        assert is_valid == True
        assert errors == []


class TestMergeMultipleConfigs:
    """测试 merge_multiple_configs 函数"""
    
    def test_merge_multiple_configs_basic(self):
        """测试基本多配置合并"""
        configs = [
            ("default", {"a": 1, "b": 2}),
            ("user", {"b": 20, "c": 3}),
            ("local", {"c": 30, "d": 4})
        ]
        
        result = merge_multiple_configs(configs)
        
        assert result == {"a": 1, "b": 20, "c": 30, "d": 4}
    
    def test_merge_multiple_configs_with_priority_order(self):
        """测试带优先级顺序的合并"""
        configs = [
            ("default", {"a": 1, "b": 2}),
            ("user", {"b": 20, "c": 3}),
            ("local", {"c": 30, "d": 4})
        ]
        
        # 指定优先级顺序：local > user > default
        result = merge_multiple_configs(configs, priority_order=["local", "user", "default"])
        
        # local 的值应该优先
        assert result["c"] == 30
        assert result["d"] == 4
    
    def test_merge_multiple_configs_empty_list(self):
        """测试空配置列表"""
        configs = []
        
        result = merge_multiple_configs(configs)
        
        assert result == {}
    
    def test_merge_multiple_configs_single_config(self):
        """测试单个配置"""
        configs = [
            ("default", {"a": 1, "b": 2})
        ]
        
        result = merge_multiple_configs(configs)
        
        assert result == {"a": 1, "b": 2}
    
    def test_merge_multiple_configs_nested(self):
        """测试嵌套配置合并"""
        configs = [
            ("default", {"nested": {"a": 1, "b": 2}}),
            ("user", {"nested": {"b": 20, "c": 3}})
        ]
        
        result = merge_multiple_configs(configs)
        
        assert result["nested"]["a"] == 1
        assert result["nested"]["b"] == 20
        assert result["nested"]["c"] == 3


class TestGetMergeSummary:
    """测试 get_merge_summary 函数"""
    
    def test_get_merge_summary_basic(self):
        """测试基本合并摘要"""
        top_config = {
            "enabled": True,
            "priority": 200
        }
        module_config = {
            "activation_conditions": {"always": True}
        }
        merged = merge_configs(top_config, module_config, "test")
        
        summary = get_merge_summary(top_config, module_config, merged)
        
        assert "配置合并摘要" in summary
        assert "enabled" in summary
        assert "priority" in summary
        assert "activation_conditions" in summary
    
    def test_get_merge_summary_priority_fields(self):
        """测试优先字段标注"""
        top_config = {
            "enabled": True,
            "version": "v1.0",
            "priority": 200
        }
        module_config = {
            "enabled": False,
            "version": "v2.0",
            "priority": 100,
            "activation_conditions": {"always": True}
        }
        merged = merge_configs(top_config, module_config, "test")
        
        summary = get_merge_summary(top_config, module_config, merged)
        
        assert "enabled: 顶层配置优先" in summary
        assert "version: 顶层配置优先" in summary
        assert "priority: 顶层配置优先" in summary
        assert "activation_conditions: 模块配置优先" in summary
    
    def test_get_merge_summary_custom_fields(self):
        """测试自定义字段标注"""
        top_config = {
            "enabled": True,
            "version": "v1.0",
            "priority": 200,
            "custom_field": "value"
        }
        module_config = {
            "activation_conditions": {"always": True},
            "custom_field": "other_value"
        }
        merged = merge_configs(top_config, module_config, "test")
        
        summary = get_merge_summary(top_config, module_config, merged)
        
        assert "custom_field: 深度合并" in summary


class TestIntegrationScenarios:
    """测试集成场景"""
    
    def test_realistic_workflow_module(self):
        """测试真实的 workflow 模块配置合并"""
        top_config = {
            "enabled": True,
            "version": "v1.0",
            "priority": 200
        }
        module_config = {
            "activation_conditions": {
                "or": [
                    {"directory_match": [".kiro/steering/*"]},
                    {"file_type_match": [".md"]}
                ]
            },
            "module_specific_config": {
                "workflow_type": "dual-track"
            }
        }
        
        result = merge_configs(top_config, module_config, "workflow")
        
        # 验证合并结果
        assert result["enabled"] == True
        assert result["version"] == "v1.0"
        assert result["priority"] == 200
        assert "or" in result["activation_conditions"]
        assert result["module_specific_config"]["workflow_type"] == "dual-track"
        
        # 验证配置有效性
        is_valid, errors = validate_merged_config(result)
        assert is_valid == True
    
    def test_realistic_git_commit_module(self):
        """测试真实的 git-commit 模块配置合并"""
        top_config = {
            "enabled": True,
            "version": "v1.0",
            "priority": 80,
            "dependencies": ["workflow"]
        }
        module_config = {
            "activation_conditions": {"always": True},
            "module_specific_config": {
                "commit_template": "[{topic}] {version} - {description}",
                "auto_stage": False
            }
        }
        
        result = merge_configs(top_config, module_config, "git-commit")
        
        # 验证合并结果
        assert result["enabled"] == True
        assert result["dependencies"] == ["workflow"]
        assert result["module_specific_config"]["commit_template"] == "[{topic}] {version} - {description}"
        
        # 验证配置有效性
        is_valid, errors = validate_merged_config(result)
        assert is_valid == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
