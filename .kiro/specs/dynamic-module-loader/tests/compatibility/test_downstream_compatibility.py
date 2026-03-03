"""
上下游兼容性测试

验证 current_context.yaml 格式与下游模块（Git 提交模块、VibCoding 工作流）的兼容性
"""

import pytest
import yaml
import os
import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from context_manager import ContextManager


class TestGitCommitModuleCompatibility:
    """测试与 Git 提交模块的兼容性"""
    
    def test_context_format_compatibility(self, tmp_path):
        """测试 current_context.yaml 格式与 Git 提交模块兼容"""
        # 创建上下文管理器
        context_file = tmp_path / 'current_context.yaml'
        context_mgr = ContextManager(context_path=str(context_file))
        
        # 更新上下文
        context_mgr.update_context(
            requirement_id='test-requirement',
            requirement_name='测试需求',
            requirement_path='.kiro/specs/test',
            current_directory='.kiro/specs/test',
            current_file='test.py',
            current_file_type='.py'
        )
        
        # 读取上下文（模拟 Git 提交模块读取）
        with open(context_file, 'r', encoding='utf-8') as f:
            context = yaml.safe_load(f)
        
        # 验证必需字段存在
        assert 'active_requirement' in context
        assert 'environment' in context
        assert 'updated_at' in context
        
        # 验证 active_requirement 字段
        assert 'requirement_id' in context['active_requirement']
        assert 'requirement_name' in context['active_requirement']
        assert 'requirement_path' in context['active_requirement']
        
        # 验证 environment 字段
        assert 'current_directory' in context['environment']
        assert 'current_file' in context['environment']
        assert 'current_file_type' in context['environment']
        
        # 验证字段值
        assert context['active_requirement']['requirement_id'] == 'test-requirement'
        assert context['active_requirement']['requirement_name'] == '测试需求'
        assert context['active_requirement']['requirement_path'] == '.kiro/specs/test'
        assert context['environment']['current_directory'] == '.kiro/specs/test'
        assert context['environment']['current_file'] == 'test.py'
        assert context['environment']['current_file_type'] == '.py'
    
    def test_requirement_id_format(self, tmp_path):
        """测试 requirement_id 使用 kebab-case 格式"""
        context_file = tmp_path / 'current_context.yaml'
        context_mgr = ContextManager(context_path=str(context_file))
        
        # 测试各种 kebab-case 格式
        test_cases = [
            'simple-name',
            'multi-word-name',
            'name-with-numbers-123',
            'a-b-c-d-e'
        ]
        
        for requirement_id in test_cases:
            context_mgr.update_context(
                requirement_id=requirement_id,
                requirement_name='测试',
                requirement_path='.kiro/specs/test',
                current_directory='.kiro/specs/test',
                current_file='test.py',
                current_file_type='.py'
            )
            
            with open(context_file, 'r', encoding='utf-8') as f:
                context = yaml.safe_load(f)
            
            # 验证格式
            import re
            assert re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', context['active_requirement']['requirement_id'])
    
    def test_git_commit_message_generation(self, tmp_path):
        """测试 Git 提交消息生成（模拟 Git 提交模块的使用）"""
        context_file = tmp_path / 'current_context.yaml'
        context_mgr = ContextManager(context_path=str(context_file))
        
        context_mgr.update_context(
            requirement_id='dynamic-module-loader',
            requirement_name='动态模块加载器',
            requirement_path='.kiro/specs/dynamic-module-loader',
            current_directory='.kiro/specs/dynamic-module-loader',
            current_file='src/dynamic_loader.py',
            current_file_type='.py'
        )
        
        # 模拟 Git 提交模块读取上下文
        with open(context_file, 'r', encoding='utf-8') as f:
            context = yaml.safe_load(f)
        
        requirement_id = context['active_requirement']['requirement_id']
        requirement_name = context['active_requirement']['requirement_name']
        
        # 生成 Git 提交消息
        commit_message = f"feat({requirement_id}): {requirement_name} - 实现核心功能"
        
        # 验证提交消息格式
        assert commit_message == "feat(dynamic-module-loader): 动态模块加载器 - 实现核心功能"


class TestVibCodingWorkflowCompatibility:
    """测试与 VibCoding 工作流的兼容性"""
    
    def test_context_format_compatibility(self, tmp_path):
        """测试 current_context.yaml 格式与 VibCoding 工作流兼容"""
        context_file = tmp_path / 'current_context.yaml'
        context_mgr = ContextManager(context_path=str(context_file))
        
        context_mgr.update_context(
            requirement_id='dynamic-module-loader',
            requirement_name='动态模块加载器',
            requirement_path='.kiro/specs/dynamic-module-loader',
            current_directory='.kiro/specs/dynamic-module-loader',
            current_file='requirements.md',
            current_file_type='.md'
        )
        
        # 模拟 VibCoding 工作流读取上下文
        with open(context_file, 'r', encoding='utf-8') as f:
            context = yaml.safe_load(f)
        
        # 验证必需字段
        assert 'active_requirement' in context
        assert 'requirement_path' in context['active_requirement']
        
        # 提取需求路径
        requirement_path = context['active_requirement']['requirement_path']
        assert requirement_path == '.kiro/specs/dynamic-module-loader'
    
    def test_requirement_path_validity(self, tmp_path):
        """测试 requirement_path 指向有效目录"""
        context_file = tmp_path / 'current_context.yaml'
        context_mgr = ContextManager(context_path=str(context_file))
        
        # 使用实际存在的路径
        actual_path = '.kiro/specs/dynamic-module-loader'
        
        context_mgr.update_context(
            requirement_id='dynamic-module-loader',
            requirement_name='动态模块加载器',
            requirement_path=actual_path,
            current_directory=actual_path,
            current_file='requirements.md',
            current_file_type='.md'
        )
        
        with open(context_file, 'r', encoding='utf-8') as f:
            context = yaml.safe_load(f)
        
        requirement_path = context['active_requirement']['requirement_path']
        
        # 验证路径格式（相对路径）
        assert not os.path.isabs(requirement_path)
        assert requirement_path.startswith('.kiro/specs/')


class TestDataFormatCompatibility:
    """测试数据格式兼容性"""
    
    def test_utf8_encoding(self, tmp_path):
        """测试文件编码为 UTF-8"""
        context_file = tmp_path / 'current_context.yaml'
        context_mgr = ContextManager(context_path=str(context_file))
        
        # 使用中文字符
        context_mgr.update_context(
            requirement_id='test-requirement',
            requirement_name='测试需求（中文）',
            requirement_path='.kiro/specs/test',
            current_directory='.kiro/specs/test',
            current_file='测试文件.py',
            current_file_type='.py'
        )
        
        # 验证可以用 UTF-8 读取
        with open(context_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '测试需求（中文）' in content
            assert '测试文件.py' in content
    
    def test_iso8601_timestamp_format(self, tmp_path):
        """测试 updated_at 使用 ISO 8601 格式"""
        context_file = tmp_path / 'current_context.yaml'
        context_mgr = ContextManager(context_path=str(context_file))
        
        context_mgr.update_context(
            requirement_id='test-requirement',
            requirement_name='测试需求',
            requirement_path='.kiro/specs/test',
            current_directory='.kiro/specs/test',
            current_file='test.py',
            current_file_type='.py'
        )
        
        with open(context_file, 'r', encoding='utf-8') as f:
            context = yaml.safe_load(f)
        
        updated_at = context['updated_at']
        
        # 验证 ISO 8601 格式
        import re
        assert re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', updated_at)
    
    def test_relative_path_format(self, tmp_path):
        """测试所有路径使用相对路径"""
        context_file = tmp_path / 'current_context.yaml'
        context_mgr = ContextManager(context_path=str(context_file))
        
        context_mgr.update_context(
            requirement_id='test-requirement',
            requirement_name='测试需求',
            requirement_path='.kiro/specs/test',
            current_directory='.kiro/specs/test',
            current_file='src/test.py',
            current_file_type='.py'
        )
        
        with open(context_file, 'r', encoding='utf-8') as f:
            context = yaml.safe_load(f)
        
        # 验证所有路径都是相对路径
        requirement_path = context['active_requirement']['requirement_path']
        current_directory = context['environment']['current_directory']
        current_file = context['environment']['current_file']
        
        assert not os.path.isabs(requirement_path)
        assert not os.path.isabs(current_directory)
        assert not os.path.isabs(current_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
