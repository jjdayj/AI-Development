"""
当前上下文管理器单元测试

测试 context_manager.py 模块的所有功能，包括：
- 上下文读写操作
- 格式校验
- 错误处理
- 便捷函数

需求追溯：需求 17.1, 17.2, 17.3, 17.4
"""

import pytest
import os
import tempfile
import yaml
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, mock_open

# 添加 src 目录到路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from context_manager import (
    ContextManager, 
    create_sample_context,
    read_current_context,
    write_current_context,
    update_current_context
)


class TestContextManager:
    """上下文管理器测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.context_path = os.path.join(self.temp_dir, "current_context.yaml")
        self.manager = ContextManager(self.context_path)
        
    def teardown_method(self):
        """每个测试方法后的清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init_default_path(self):
        """测试默认路径初始化"""
        manager = ContextManager()
        expected_path = Path(".kiro/current_context.yaml")
        assert manager.context_path == expected_path
    
    def test_init_custom_path(self):
        """测试自定义路径初始化"""
        custom_path = "/custom/path/context.yaml"
        manager = ContextManager(custom_path)
        expected_path = Path(custom_path)
        assert manager.context_path == expected_path
    
    def test_read_context_file_not_exists(self):
        """测试读取不存在的上下文文件"""
        result = self.manager.read_context()
        assert result is None
    
    def test_read_context_empty_file(self):
        """测试读取空文件"""
        # 创建空文件
        Path(self.context_path).touch()
        
        result = self.manager.read_context()
        assert result == {}
    
    def test_read_context_valid_file(self):
        """测试读取有效的上下文文件"""
        test_context = {
            'active_requirement': {
                'module_name': 'test-module',
                'version': 'v1.0'
            },
            'updated_at': '2026-03-03T10:00:00'
        }
        
        # 写入测试数据
        os.makedirs(os.path.dirname(self.context_path), exist_ok=True)
        with open(self.context_path, 'w', encoding='utf-8') as f:
            yaml.dump(test_context, f)
        
        result = self.manager.read_context()
        assert result == test_context
    
    def test_read_context_invalid_yaml(self):
        """测试读取无效 YAML 文件"""
        # 写入无效 YAML
        os.makedirs(os.path.dirname(self.context_path), exist_ok=True)
        with open(self.context_path, 'w', encoding='utf-8') as f:
            f.write("invalid: yaml: content: [")
        
        with pytest.raises(yaml.YAMLError):
            self.manager.read_context()
    
    def test_write_context_success(self):
        """测试成功写入上下文"""
        test_context = {
            'active_requirement': {
                'module_name': 'test-module',
                'version': 'v1.0'
            }
        }
        
        result = self.manager.write_context(test_context)
        assert result is True
        
        # 验证文件内容
        with open(self.context_path, 'r', encoding='utf-8') as f:
            written_content = yaml.safe_load(f)
        
        assert written_content['active_requirement'] == test_context['active_requirement']
        assert 'updated_at' in written_content
    
    def test_write_context_creates_directory(self):
        """测试写入时自动创建目录"""
        nested_path = os.path.join(self.temp_dir, "nested", "dir", "context.yaml")
        manager = ContextManager(nested_path)
        
        test_context = {'test': 'data'}
        result = manager.write_context(test_context)
        
        assert result is True
        assert os.path.exists(nested_path)
    
    def test_write_context_adds_timestamp(self):
        """测试写入时自动添加时间戳"""
        test_context = {'test': 'data'}
        
        before_write = datetime.now()
        self.manager.write_context(test_context)
        after_write = datetime.now()
        
        # 读取并验证时间戳
        written_content = self.manager.read_context()
        updated_at = datetime.fromisoformat(written_content['updated_at'])
        
        assert before_write <= updated_at <= after_write
    
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_write_context_io_error(self, mock_file):
        """测试写入时 IO 错误"""
        test_context = {'test': 'data'}
        
        with pytest.raises(IOError):
            self.manager.write_context(test_context)
    
    def test_update_context_new_file(self):
        """测试更新不存在的上下文文件"""
        updates = {
            'active_requirement': {
                'module_name': 'new-module'
            }
        }
        
        result = self.manager.update_context(updates)
        assert result is True
        
        # 验证内容
        content = self.manager.read_context()
        assert content['active_requirement']['module_name'] == 'new-module'
    
    def test_update_context_existing_file(self):
        """测试更新现有上下文文件"""
        # 先写入初始内容
        initial_context = {
            'active_requirement': {
                'module_name': 'old-module',
                'version': 'v1.0'
            },
            'environment': {
                'current_directory': '/old/path'
            }
        }
        self.manager.write_context(initial_context)
        
        # 更新部分内容
        updates = {
            'active_requirement': {
                'module_name': 'new-module'
            },
            'environment': {
                'current_file_path': '/new/file.py'
            }
        }
        
        result = self.manager.update_context(updates)
        assert result is True
        
        # 验证合并结果
        content = self.manager.read_context()
        assert content['active_requirement']['module_name'] == 'new-module'
        assert content['active_requirement']['version'] == 'v1.0'  # 保留原有字段
        assert content['environment']['current_directory'] == '/old/path'  # 保留原有字段
        assert content['environment']['current_file_path'] == '/new/file.py'  # 新增字段
    
    def test_validate_context_format_valid(self):
        """测试有效上下文格式验证"""
        valid_context = {
            'active_requirement': {
                'module_name': 'test-module',
                'version': 'v1.0',
                'requirement_path': 'requirements/test-module/v1.0',
                'requirement_title': '测试模块',
                'created_at': '2026-03-03T10:00:00'
            },
            'environment': {
                'current_directory': '/test/path',
                'current_file_path': '/test/file.py',
                'current_file_type': '.py'
            },
            'updated_at': '2026-03-03T10:00:00'
        }
        
        is_valid, errors = self.manager.validate_context_format(valid_context)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_context_format_missing_top_level(self):
        """测试缺少顶层字段的格式验证"""
        invalid_context = {
            'active_requirement': {
                'module_name': 'test-module'
            }
            # 缺少 environment 和 updated_at
        }
        
        is_valid, errors = self.manager.validate_context_format(invalid_context)
        assert is_valid is False
        assert '缺少必需字段: environment' in errors
        assert '缺少必需字段: updated_at' in errors
    
    def test_validate_context_format_invalid_active_requirement(self):
        """测试无效 active_requirement 格式验证"""
        invalid_context = {
            'active_requirement': {
                'module_name': 'test-module'
                # 缺少其他必需字段
            },
            'environment': {
                'current_directory': '/test/path',
                'current_file_path': '/test/file.py',
                'current_file_type': '.py'
            },
            'updated_at': '2026-03-03T10:00:00'
        }
        
        is_valid, errors = self.manager.validate_context_format(invalid_context)
        assert is_valid is False
        assert any('active_requirement 缺少必需字段' in error for error in errors)
    
    def test_validate_context_format_invalid_environment(self):
        """测试无效 environment 格式验证"""
        invalid_context = {
            'active_requirement': {
                'module_name': 'test-module',
                'version': 'v1.0',
                'requirement_path': 'requirements/test-module/v1.0',
                'requirement_title': '测试模块',
                'created_at': '2026-03-03T10:00:00'
            },
            'environment': {
                'current_directory': '/test/path'
                # 缺少其他必需字段
            },
            'updated_at': '2026-03-03T10:00:00'
        }
        
        is_valid, errors = self.manager.validate_context_format(invalid_context)
        assert is_valid is False
        assert any('environment 缺少必需字段' in error for error in errors)
    
    def test_validate_context_format_invalid_timestamp(self):
        """测试无效时间戳格式验证"""
        invalid_context = {
            'active_requirement': {
                'module_name': 'test-module',
                'version': 'v1.0',
                'requirement_path': 'requirements/test-module/v1.0',
                'requirement_title': '测试模块',
                'created_at': '2026-03-03T10:00:00'
            },
            'environment': {
                'current_directory': '/test/path',
                'current_file_path': '/test/file.py',
                'current_file_type': '.py'
            },
            'updated_at': 'invalid-timestamp'
        }
        
        is_valid, errors = self.manager.validate_context_format(invalid_context)
        assert is_valid is False
        assert 'updated_at 时间戳格式无效' in errors
    
    def test_validate_context_format_not_dict(self):
        """测试非字典类型的格式验证"""
        invalid_context = "not a dict"
        
        is_valid, errors = self.manager.validate_context_format(invalid_context)
        assert is_valid is False
        assert '上下文必须是字典类型' in errors
    
    def test_validate_context_format_field_types(self):
        """测试字段类型验证"""
        invalid_context = {
            'active_requirement': {
                'module_name': 123,  # 应该是字符串
                'version': 'v1.0',
                'requirement_path': 'requirements/test-module/v1.0',
                'requirement_title': '测试模块',
                'created_at': 'invalid-timestamp'
            },
            'environment': {
                'current_directory': 456,  # 应该是字符串
                'current_file_path': '/test/file.py',
                'current_file_type': '.py'
            },
            'updated_at': '2026-03-03T10:00:00'
        }
        
        is_valid, errors = self.manager.validate_context_format(invalid_context)
        assert is_valid is False
        assert 'active_requirement.module_name 必须是字符串' in errors
        assert 'environment.current_directory 必须是字符串' in errors
        assert 'active_requirement.created_at 时间戳格式无效' in errors
    
    def test_validate_and_fix_context_empty(self):
        """测试修复空上下文"""
        empty_context = {}
        
        fixed_context, warnings = self.manager.validate_and_fix_context(empty_context)
        
        assert 'active_requirement' in fixed_context
        assert 'environment' in fixed_context
        assert 'updated_at' in fixed_context
        assert len(warnings) >= 3
        assert any('自动添加缺失的 active_requirement 字段' in w for w in warnings)
        assert any('自动添加缺失的 environment 字段' in w for w in warnings)
        assert any('自动添加缺失的 updated_at 字段' in w for w in warnings)
    
    def test_validate_and_fix_context_partial(self):
        """测试修复部分缺失的上下文"""
        partial_context = {
            'active_requirement': {
                'module_name': 'test-module'
                # 缺少其他字段
            },
            'environment': {
                'current_directory': '/test/path'
                # 缺少其他字段
            }
            # 缺少 updated_at
        }
        
        fixed_context, warnings = self.manager.validate_and_fix_context(partial_context)
        
        # 验证修复结果
        assert fixed_context['active_requirement']['module_name'] == 'test-module'
        assert 'version' in fixed_context['active_requirement']
        assert 'requirement_path' in fixed_context['active_requirement']
        assert 'requirement_title' in fixed_context['active_requirement']
        assert 'created_at' in fixed_context['active_requirement']
        
        assert fixed_context['environment']['current_directory'] == '/test/path'
        assert 'current_file_path' in fixed_context['environment']
        assert 'current_file_type' in fixed_context['environment']
        
        assert 'updated_at' in fixed_context
        
        # 验证警告信息
        assert len(warnings) > 0
    
    def test_validate_and_fix_context_invalid_types(self):
        """测试修复无效类型的上下文"""
        invalid_context = {
            'active_requirement': "not a dict",
            'environment': "not a dict",
            'updated_at': '2026-03-03T10:00:00'
        }
        
        fixed_context, warnings = self.manager.validate_and_fix_context(invalid_context)
        
        assert isinstance(fixed_context['active_requirement'], dict)
        assert isinstance(fixed_context['environment'], dict)
        assert any('修复 active_requirement 字段类型' in w for w in warnings)
        assert any('修复 environment 字段类型' in w for w in warnings)
    
    def test_context_exists_true(self):
        """测试上下文文件存在检查"""
        # 创建文件
        Path(self.context_path).touch()
        
        assert self.manager.context_exists() is True
    
    def test_context_exists_false(self):
        """测试上下文文件不存在检查"""
        assert self.manager.context_exists() is False
    
    def test_delete_context_existing_file(self):
        """测试删除存在的上下文文件"""
        # 创建文件
        Path(self.context_path).touch()
        
        result = self.manager.delete_context()
        assert result is True
        assert not os.path.exists(self.context_path)
    
    def test_delete_context_non_existing_file(self):
        """测试删除不存在的上下文文件"""
        result = self.manager.delete_context()
        assert result is True  # 不存在也算成功
    
    def test_backup_context_success(self):
        """测试成功备份上下文文件"""
        # 创建测试文件
        test_content = "test content"
        with open(self.context_path, 'w') as f:
            f.write(test_content)
        
        backup_path = self.manager.backup_context("test_backup")
        
        assert backup_path is not None
        assert os.path.exists(backup_path)
        
        # 验证备份内容
        with open(backup_path, 'r') as f:
            backup_content = f.read()
        assert backup_content == test_content
    
    def test_backup_context_auto_timestamp(self):
        """测试自动时间戳备份"""
        # 创建测试文件
        Path(self.context_path).touch()
        
        backup_path = self.manager.backup_context()
        
        assert backup_path is not None
        assert "backup." in backup_path
        assert os.path.exists(backup_path)
    
    def test_backup_context_file_not_exists(self):
        """测试备份不存在的文件"""
        backup_path = self.manager.backup_context()
        assert backup_path is None
    
    def test_deep_merge_simple(self):
        """测试简单字典合并"""
        base = {'a': 1, 'b': 2}
        updates = {'b': 3, 'c': 4}
        
        result = self.manager._deep_merge(base, updates)
        
        expected = {'a': 1, 'b': 3, 'c': 4}
        assert result == expected
    
    def test_deep_merge_nested(self):
        """测试嵌套字典合并"""
        base = {
            'level1': {
                'a': 1,
                'b': 2,
                'level2': {
                    'x': 10,
                    'y': 20
                }
            }
        }
        updates = {
            'level1': {
                'b': 3,
                'c': 4,
                'level2': {
                    'y': 30,
                    'z': 40
                }
            }
        }
        
        result = self.manager._deep_merge(base, updates)
        
        expected = {
            'level1': {
                'a': 1,
                'b': 3,
                'c': 4,
                'level2': {
                    'x': 10,
                    'y': 30,
                    'z': 40
                }
            }
        }
        assert result == expected


class TestCreateSampleContext:
    """测试示例上下文创建函数"""
    
    def test_create_sample_context_structure(self):
        """测试示例上下文结构"""
        context = create_sample_context()
        
        assert 'active_requirement' in context
        assert 'environment' in context
        assert 'updated_at' in context
        
        # 验证 active_requirement 结构
        active_req = context['active_requirement']
        assert 'module_name' in active_req
        assert 'version' in active_req
        assert 'requirement_path' in active_req
        assert 'requirement_title' in active_req
        assert 'created_at' in active_req
        assert 'status' in active_req
        
        # 验证 environment 结构
        env = context['environment']
        assert 'current_directory' in env
        assert 'current_file_path' in env
        assert 'current_file_type' in env
    
    def test_create_sample_context_values(self):
        """测试示例上下文值"""
        context = create_sample_context()
        
        assert context['active_requirement']['module_name'] == 'dynamic-module-loader'
        assert context['active_requirement']['version'] == 'v1.0'
        assert context['active_requirement']['status'] == 'in_progress'
        assert context['environment']['current_directory'] == os.getcwd()


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.context_path = os.path.join(self.temp_dir, "current_context.yaml")
        
    def teardown_method(self):
        """每个测试方法后的清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_read_current_context_convenience(self):
        """测试读取上下文便捷函数"""
        # 创建测试文件
        test_context = {'test': 'data'}
        os.makedirs(os.path.dirname(self.context_path), exist_ok=True)
        with open(self.context_path, 'w', encoding='utf-8') as f:
            yaml.dump(test_context, f)
        
        result = read_current_context(self.context_path)
        assert result == test_context
    
    def test_write_current_context_convenience(self):
        """测试写入上下文便捷函数"""
        test_context = {'test': 'data'}
        
        result = write_current_context(test_context, self.context_path)
        assert result is True
        
        # 验证文件内容
        with open(self.context_path, 'r', encoding='utf-8') as f:
            written_content = yaml.safe_load(f)
        assert written_content['test'] == 'data'
        assert 'updated_at' in written_content
    
    def test_update_current_context_convenience(self):
        """测试更新上下文便捷函数"""
        # 先写入初始内容
        initial_context = {'existing': 'data'}
        write_current_context(initial_context, self.context_path)
        
        # 更新内容
        updates = {'new': 'value'}
        result = update_current_context(updates, self.context_path)
        assert result is True
        
        # 验证合并结果
        content = read_current_context(self.context_path)
        assert content['existing'] == 'data'
        assert content['new'] == 'value'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])