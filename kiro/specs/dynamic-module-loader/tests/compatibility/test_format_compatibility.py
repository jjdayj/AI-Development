"""
数据格式兼容性测试

验证 current_context.yaml 格式与下游模块的兼容性
"""

import pytest
import yaml
import os
import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from context_manager import ContextManager


class TestContextFormatCompatibility:
    """测试上下文格式兼容性"""
    
    def test_context_yaml_structure(self, tmp_path):
        """测试 current_context.yaml 基本结构"""
        context_file = tmp_path / 'current_context.yaml'
        context_mgr = ContextManager(context_path=str(context_file))
        
        # 创建测试数据
        context_data = {
            'active_requirement': {
                'requirement_id': 'test-requirement',
                'requirement_name': '测试需求',
                'requirement_path': '.kiro/specs/test'
            },
            'environment': {
                'current_directory': '.kiro/specs/test',
                'current_file': 'test.py',
                'current_file_type': '.py'
            },
            'updated_at': '2026-03-03T10:30:00Z'
        }
        
        # 写入并读取
        context_mgr.write_context(context_data)
        
        with open(context_file, 'r', encoding='utf-8') as f:
            loaded_context = yaml.safe_load(f)
        
        # 验证结构
        assert 'active_requirement' in loaded_context
        assert 'environment' in loaded_context
        assert 'updated_at' in loaded_context
        
        # 验证字段
        assert loaded_context['active_requirement']['requirement_id'] == 'test-requirement'
        assert loaded_context['active_requirement']['requirement_name'] == '测试需求'
        assert loaded_context['environment']['current_file_type'] == '.py'
    
    def test_requirement_id_kebab_case(self, tmp_path):
        """测试 requirement_id 使用 kebab-case 格式"""
        context_file = tmp_path / 'current_context.yaml'
        context_mgr = ContextManager(context_path=str(context_file))
        
        test_ids = ['simple-name', 'multi-word-name', 'name-with-123']
        
        for req_id in test_ids:
            context_data = {
                'active_requirement': {
                    'requirement_id': req_id,
                    'requirement_name': '测试',
                    'requirement_path': '.kiro/specs/test'
                },
                'environment': {
                    'current_directory': '.kiro/specs/test',
                    'current_file': 'test.py',
                    'current_file_type': '.py'
                },
                'updated_at': '2026-03-03T10:30:00Z'
            }
            
            context_mgr.write_context(context_data)
            
            with open(context_file, 'r', encoding='utf-8') as f:
                loaded = yaml.safe_load(f)
            
            import re
            assert re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', loaded['active_requirement']['requirement_id'])
    
    def test_utf8_encoding(self, tmp_path):
        """测试 UTF-8 编码支持"""
        context_file = tmp_path / 'current_context.yaml'
        context_mgr = ContextManager(context_path=str(context_file))
        
        context_data = {
            'active_requirement': {
                'requirement_id': 'test-requirement',
                'requirement_name': '测试需求（中文）',
                'requirement_path': '.kiro/specs/test'
            },
            'environment': {
                'current_directory': '.kiro/specs/test',
                'current_file': '测试文件.py',
                'current_file_type': '.py'
            },
            'updated_at': '2026-03-03T10:30:00Z'
        }
        
        context_mgr.write_context(context_data)
        
        with open(context_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '测试需求（中文）' in content
            assert '测试文件.py' in content
    
    def test_iso8601_timestamp(self, tmp_path):
        """测试 ISO 8601 时间戳格式"""
        context_file = tmp_path / 'current_context.yaml'
        context_mgr = ContextManager(context_path=str(context_file))
        
        context_data = {
            'active_requirement': {
                'requirement_id': 'test',
                'requirement_name': '测试',
                'requirement_path': '.kiro/specs/test'
            },
            'environment': {
                'current_directory': '.kiro/specs/test',
                'current_file': 'test.py',
                'current_file_type': '.py'
            },
            'updated_at': '2026-03-03T10:30:00Z'
        }
        
        context_mgr.write_context(context_data)
        
        with open(context_file, 'r', encoding='utf-8') as f:
            loaded = yaml.safe_load(f)
        
        import re
        # 接受带或不带微秒的 ISO 8601 格式
        assert re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z?$', loaded['updated_at'])
    
    def test_relative_paths(self, tmp_path):
        """测试相对路径格式"""
        context_file = tmp_path / 'current_context.yaml'
        context_mgr = ContextManager(context_path=str(context_file))
        
        context_data = {
            'active_requirement': {
                'requirement_id': 'test',
                'requirement_name': '测试',
                'requirement_path': '.kiro/specs/test'
            },
            'environment': {
                'current_directory': '.kiro/specs/test',
                'current_file': 'src/test.py',
                'current_file_type': '.py'
            },
            'updated_at': '2026-03-03T10:30:00Z'
        }
        
        context_mgr.write_context(context_data)
        
        with open(context_file, 'r', encoding='utf-8') as f:
            loaded = yaml.safe_load(f)
        
        # 验证都是相对路径
        assert not os.path.isabs(loaded['active_requirement']['requirement_path'])
        assert not os.path.isabs(loaded['environment']['current_directory'])
        assert not os.path.isabs(loaded['environment']['current_file'])


class TestGitCommitCompatibility:
    """测试与 Git 提交模块的兼容性"""
    
    def test_git_commit_message_format(self, tmp_path):
        """测试 Git 提交消息生成"""
        context_file = tmp_path / 'current_context.yaml'
        context_mgr = ContextManager(context_path=str(context_file))
        
        context_data = {
            'active_requirement': {
                'requirement_id': 'dynamic-module-loader',
                'requirement_name': '动态模块加载器',
                'requirement_path': '.kiro/specs/dynamic-module-loader'
            },
            'environment': {
                'current_directory': '.kiro/specs/dynamic-module-loader',
                'current_file': 'src/dynamic_loader.py',
                'current_file_type': '.py'
            },
            'updated_at': '2026-03-03T10:30:00Z'
        }
        
        context_mgr.write_context(context_data)
        
        # 模拟 Git 提交模块读取
        with open(context_file, 'r', encoding='utf-8') as f:
            context = yaml.safe_load(f)
        
        req_id = context['active_requirement']['requirement_id']
        req_name = context['active_requirement']['requirement_name']
        
        commit_msg = f"feat({req_id}): {req_name} - 实现核心功能"
        
        assert commit_msg == "feat(dynamic-module-loader): 动态模块加载器 - 实现核心功能"


class TestVibCodingCompatibility:
    """测试与 VibCoding 工作流的兼容性"""
    
    def test_requirement_path_access(self, tmp_path):
        """测试需求路径访问"""
        context_file = tmp_path / 'current_context.yaml'
        context_mgr = ContextManager(context_path=str(context_file))
        
        context_data = {
            'active_requirement': {
                'requirement_id': 'test',
                'requirement_name': '测试',
                'requirement_path': '.kiro/specs/dynamic-module-loader'
            },
            'environment': {
                'current_directory': '.kiro/specs/dynamic-module-loader',
                'current_file': 'requirements.md',
                'current_file_type': '.md'
            },
            'updated_at': '2026-03-03T10:30:00Z'
        }
        
        context_mgr.write_context(context_data)
        
        # 模拟 VibCoding 工作流读取
        with open(context_file, 'r', encoding='utf-8') as f:
            context = yaml.safe_load(f)
        
        req_path = context['active_requirement']['requirement_path']
        
        # 验证路径格式
        assert req_path.startswith('.kiro/specs/')
        assert not os.path.isabs(req_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
