"""
Steering 加载器单元测试

测试 steering_loader.py 模块的所有功能，包括：
- 路径构建逻辑
- 路径格式验证
- 文件内容加载
- 模块标识注释生成
- 错误处理

需求追溯：需求 7.1, 7.3, 8.1, 8.2, 8.3, 14.3
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

# 添加 src 目录到路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from steering_loader import (
    SteeringLoader,
    build_steering_path,
    load_steering_file,
    validate_steering_path
)


class TestSteeringLoader:
    """Steering 加载器测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.loader = SteeringLoader(self.temp_dir)
        
    def teardown_method(self):
        """每个测试方法后的清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init_default_path(self):
        """测试默认路径初始化"""
        loader = SteeringLoader()
        expected_path = Path(".kiro/modules")
        assert loader.base_path == expected_path
    
    def test_init_custom_path(self):
        """测试自定义路径初始化"""
        custom_path = "/custom/modules"
        loader = SteeringLoader(custom_path)
        expected_path = Path(custom_path)
        assert loader.base_path == expected_path
    
    def test_build_steering_path_standard_module(self):
        """测试标准模块的路径构建"""
        module_name = "ai-dev"
        module_version = "v1.0"
        
        path = self.loader.build_steering_path(module_name, module_version)
        
        expected = os.path.join(self.temp_dir, "ai-dev", "v1.0", "steering", "ai-dev.md")
        assert path == expected
    
    def test_build_steering_path_workflow_module(self):
        """测试 workflow 模块的特殊路径构建"""
        module_name = "workflow"
        module_version = "v1.0-simple"
        
        path = self.loader.build_steering_path(module_name, module_version)
        
        expected = os.path.join(self.temp_dir, "workflow", "v1.0-simple", "steering", "workflow_selector.md")
        assert path == expected
    
    def test_build_steering_path_various_versions(self):
        """测试各种版本格式的路径构建"""
        test_cases = [
            ("git-commit", "v1.0", "git-commit.md"),
            ("git-rollback", "v2.1.3", "git-rollback.md"),
            ("custom-module", "v1.0-alpha", "custom-module.md"),
            ("workflow", "v1.0-complex", "workflow_selector.md"),
        ]
        
        for module_name, version, expected_filename in test_cases:
            path = self.loader.build_steering_path(module_name, version)
            expected = os.path.join(self.temp_dir, module_name, version, "steering", expected_filename)
            assert path == expected
    
    def test_validate_path_format_valid_paths(self):
        """测试有效路径格式验证"""
        valid_paths = [
            ".kiro/modules/ai-dev/v1.0/steering/ai-dev.md",
            "/path/to/modules/workflow/v1.0/steering/workflow_selector.md",
            "modules/git-commit/v2.0/steering/git-commit.md",
            "custom/modules/test-module/v1.0-alpha/steering/test-module.md"
        ]
        
        for path in valid_paths:
            assert self.loader.validate_path_format(path) is True
    
    def test_validate_path_format_invalid_paths(self):
        """测试无效路径格式验证"""
        invalid_paths = [
            # 缺少 modules
            ".kiro/ai-dev/v1.0/steering/ai-dev.md",
            # 缺少 steering
            ".kiro/modules/ai-dev/v1.0/ai-dev.md",
            # 不是 .md 文件
            ".kiro/modules/ai-dev/v1.0/steering/ai-dev.txt",
            # 路径太短
            "modules/ai-dev.md",
            # 空路径
            "",
            # 只有文件名
            "ai-dev.md"
        ]
        
        for path in invalid_paths:
            assert self.loader.validate_path_format(path) is False
    
    def test_load_steering_content_success(self):
        """测试成功加载文件内容"""
        # 创建测试文件
        test_content = "# Test Steering Content\n\nThis is a test steering file."
        test_file = os.path.join(self.temp_dir, "test.md")
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        success, content, error_type = self.loader.load_steering_content(test_file)
        
        assert success is True
        assert content == test_content
        assert error_type is None
    
    def test_load_steering_content_file_not_found(self):
        """测试文件不存在的情况"""
        non_existent_file = os.path.join(self.temp_dir, "non_existent.md")
        
        success, message, error_type = self.loader.load_steering_content(non_existent_file)
        
        assert success is False
        assert "文件不存在" in message
        assert error_type == "FileNotFound"
    
    def test_load_steering_content_not_a_file(self):
        """测试路径不是文件的情况"""
        # 创建目录而不是文件
        test_dir = os.path.join(self.temp_dir, "test_dir")
        os.makedirs(test_dir)
        
        success, message, error_type = self.loader.load_steering_content(test_dir)
        
        assert success is False
        assert "不是文件" in message
        assert error_type == "NotAFile"
    
    @patch('builtins.open', side_effect=PermissionError("Permission denied"))
    def test_load_steering_content_permission_error(self, mock_file):
        """测试权限错误"""
        # 先创建文件以通过存在性检查
        test_file = os.path.join(self.temp_dir, "test.md")
        Path(test_file).touch()
        
        success, message, error_type = self.loader.load_steering_content(test_file)
        
        assert success is False
        assert "没有权限" in message
        assert error_type == "PermissionError"
    
    @patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid'))
    def test_load_steering_content_encoding_error(self, mock_file):
        """测试编码错误"""
        # 先创建文件以通过存在性检查
        test_file = os.path.join(self.temp_dir, "test.md")
        Path(test_file).touch()
        
        success, message, error_type = self.loader.load_steering_content(test_file)
        
        assert success is False
        assert "编码错误" in message
        assert error_type == "EncodingError"
    
    def test_create_module_comment_simple_conditions(self):
        """测试简单激活条件的注释生成"""
        module_name = "ai-dev"
        module_version = "v1.0"
        module_priority = 100
        activation_conditions = {"always": True}
        
        comment = self.loader.create_module_comment(
            module_name, module_version, module_priority, activation_conditions
        )
        
        expected = "<!-- Module: ai-dev | Version: v1.0 | Priority: 100 | Activated: always -->\n\n"
        assert comment == expected
    
    def test_create_module_comment_directory_conditions(self):
        """测试目录匹配条件的注释生成"""
        activation_conditions = {
            "directory_match": [".kiro/steering/*", "doc/project/*"]
        }
        
        comment = self.loader.create_module_comment(
            "workflow", "v1.0", 200, activation_conditions
        )
        
        assert "dir:.kiro/steering/*,doc/project/*" in comment
    
    def test_create_module_comment_file_type_conditions(self):
        """测试文件类型条件的注释生成"""
        activation_conditions = {
            "file_type_match": [".md", ".yaml"]
        }
        
        comment = self.loader.create_module_comment(
            "git-commit", "v1.0", 80, activation_conditions
        )
        
        assert "type:.md,.yaml" in comment
    
    def test_create_module_comment_complex_conditions(self):
        """测试复杂条件的注释生成"""
        test_cases = [
            ({"and": [{"always": True}]}, "and_logic"),
            ({"or": [{"always": True}]}, "or_logic"),
            ({}, "always"),
            ({"custom_field": "value"}, "custom")
        ]
        
        for conditions, expected_text in test_cases:
            comment = self.loader.create_module_comment(
                "test", "v1.0", 50, conditions
            )
            assert expected_text in comment
    
    def test_format_activation_conditions_truncation(self):
        """测试激活条件格式化的截断功能"""
        # 测试长列表的截断
        long_conditions = {
            "directory_match": [".kiro/*", "doc/*", "src/*", "tests/*"]
        }
        
        formatted = self.loader._format_activation_conditions(long_conditions)
        assert formatted == "dir:.kiro/*,doc/*..."
    
    def test_get_module_info_valid_path(self):
        """测试从有效路径提取模块信息"""
        test_cases = [
            (".kiro/modules/ai-dev/v1.0/steering/ai-dev.md", "ai-dev", "v1.0"),
            ("modules/workflow/v1.0-simple/steering/workflow_selector.md", "workflow", "v1.0-simple"),
            ("/path/to/modules/git-commit/v2.1/steering/git-commit.md", "git-commit", "v2.1")
        ]
        
        for path, expected_name, expected_version in test_cases:
            info = self.loader.get_module_info(path)
            assert info is not None
            assert info['module_name'] == expected_name
            assert info['version'] == expected_version
    
    def test_get_module_info_invalid_path(self):
        """测试从无效路径提取模块信息"""
        invalid_paths = [
            "invalid/path.md",
            ".kiro/ai-dev.md",
            "modules/ai-dev.md",
            ""
        ]
        
        for path in invalid_paths:
            info = self.loader.get_module_info(path)
            assert info is None
    
    def test_load_steering_full_workflow_success(self):
        """测试完整的 Steering 加载流程 - 成功情况"""
        # 创建测试目录结构
        module_name = "test-module"
        module_version = "v1.0"
        module_dir = os.path.join(self.temp_dir, module_name, module_version, "steering")
        os.makedirs(module_dir, exist_ok=True)
        
        # 创建测试文件
        test_content = "# Test Module Steering\n\nTest content here."
        test_file = os.path.join(module_dir, f"{module_name}.md")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 执行加载
        success, content, error_type = self.loader.load_steering(
            module_name, module_version, 100, {"always": True}
        )
        
        assert success is True
        assert error_type is None
        assert "<!-- Module: test-module" in content
        assert test_content in content
    
    def test_load_steering_full_workflow_workflow_module(self):
        """测试 workflow 模块的完整加载流程"""
        # 创建 workflow 模块目录结构
        module_name = "workflow"
        module_version = "v1.0-simple"
        module_dir = os.path.join(self.temp_dir, module_name, module_version, "steering")
        os.makedirs(module_dir, exist_ok=True)
        
        # 创建 workflow_selector.md 文件
        test_content = "# Workflow Selector\n\nWorkflow steering content."
        test_file = os.path.join(module_dir, "workflow_selector.md")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 执行加载
        success, content, error_type = self.loader.load_steering(
            module_name, module_version, 200, {"always": True}
        )
        
        assert success is True
        assert error_type is None
        assert "<!-- Module: workflow" in content
        assert test_content in content
    
    def test_load_steering_full_workflow_file_not_found(self):
        """测试完整流程 - 文件不存在"""
        success, message, error_type = self.loader.load_steering(
            "non-existent", "v1.0", 100, {"always": True}
        )
        
        assert success is False
        assert error_type == "FileNotFound"
        assert "文件不存在" in message
    
    def test_load_steering_invalid_path_format(self):
        """测试无效路径格式的处理"""
        # 使用会导致无效路径的基础路径
        loader = SteeringLoader("")
        
        success, message, error_type = loader.load_steering(
            "test", "v1.0", 100, {"always": True}
        )
        
        assert success is False
        assert error_type == "InvalidPath"
        assert "路径格式无效" in message


class TestConvenienceFunctions:
    """便捷函数测试类"""
    
    def test_build_steering_path_convenience(self):
        """测试路径构建便捷函数"""
        path = build_steering_path("ai-dev", "v1.0")
        expected = ".kiro/modules/ai-dev/v1.0/steering/ai-dev.md"
        assert path == expected
    
    def test_build_steering_path_convenience_custom_base(self):
        """测试自定义基础路径的便捷函数"""
        path = build_steering_path("workflow", "v1.0", "/custom/modules")
        expected = "/custom/modules/workflow/v1.0/steering/workflow_selector.md"
        assert path == expected
    
    def test_validate_steering_path_convenience(self):
        """测试路径验证便捷函数"""
        valid_path = ".kiro/modules/ai-dev/v1.0/steering/ai-dev.md"
        invalid_path = "invalid/path.txt"
        
        assert validate_steering_path(valid_path) is True
        assert validate_steering_path(invalid_path) is False
    
    def test_load_steering_file_convenience(self):
        """测试文件加载便捷函数"""
        # 这个测试需要实际文件，所以只测试函数调用不出错
        success, message, error_type = load_steering_file(
            "non-existent", "v1.0", 100, {"always": True}
        )
        
        # 应该返回文件不存在的错误
        assert success is False
        assert error_type == "FileNotFound"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])