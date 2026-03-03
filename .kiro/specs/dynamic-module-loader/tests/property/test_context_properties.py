"""
当前上下文管理器属性测试

使用 Hypothesis 进行基于属性的测试，验证上下文管理器的正确性属性。

需求追溯：需求 17.1, 17.2, 17.3, 17.4
属性 11：当前上下文一致性（Round-trip）
"""

import pytest
import os
import tempfile
import yaml
from datetime import datetime
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from hypothesis.strategies import composite

# 添加 src 目录到路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from context_manager import ContextManager, create_sample_context


# 策略定义
@composite
def valid_module_name(draw):
    """生成有效的模块名称"""
    # 模块名称应该是 kebab-case 格式
    parts = draw(st.lists(
        st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Nd')), min_size=1, max_size=10),
        min_size=1, max_size=3
    ))
    return '-'.join(parts)


@composite
def valid_version(draw):
    """生成有效的版本号"""
    major = draw(st.integers(min_value=1, max_value=10))
    minor = draw(st.integers(min_value=0, max_value=10))
    patch = draw(st.integers(min_value=0, max_value=10))
    
    # 可选的预发布版本
    prerelease = draw(st.one_of(
        st.none(),
        st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Nd')), min_size=1, max_size=10)
    ))
    
    version = f"v{major}.{minor}.{patch}"
    if prerelease:
        version += f"-{prerelease}"
    
    return version


@composite
def valid_file_path(draw):
    """生成有效的文件路径"""
    # 生成路径组件
    components = draw(st.lists(
        st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd')), min_size=1, max_size=15),
        min_size=1, max_size=5
    ))
    
    # 生成文件扩展名
    extension = draw(st.sampled_from(['.py', '.md', '.yaml', '.json', '.txt', '.js', '.ts', '']))
    
    path = '/'.join(components)
    if extension:
        path += extension
    
    return path


@composite
def valid_file_type(draw):
    """生成有效的文件类型"""
    return draw(st.sampled_from(['.py', '.md', '.yaml', '.json', '.txt', '.js', '.ts', '.html', '.css', '']))


@composite
def valid_iso_timestamp(draw):
    """生成有效的 ISO 时间戳"""
    year = draw(st.integers(min_value=2020, max_value=2030))
    month = draw(st.integers(min_value=1, max_value=12))
    day = draw(st.integers(min_value=1, max_value=28))  # 避免月份边界问题
    hour = draw(st.integers(min_value=0, max_value=23))
    minute = draw(st.integers(min_value=0, max_value=59))
    second = draw(st.integers(min_value=0, max_value=59))
    
    return f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:02d}"


@composite
def valid_context_data(draw):
    """生成有效的上下文数据"""
    module_name = draw(valid_module_name())
    version = draw(valid_version())
    requirement_path = f"requirements/{module_name}/{version}"
    requirement_title = draw(st.text(min_size=1, max_size=50))
    created_at = draw(valid_iso_timestamp())
    current_directory = draw(valid_file_path())
    current_file_path = draw(valid_file_path())
    current_file_type = draw(valid_file_type())
    updated_at = draw(valid_iso_timestamp())
    
    # 可选字段
    status = draw(st.sampled_from(['in_progress', 'completed', 'paused', 'cancelled']))
    
    context = {
        'active_requirement': {
            'module_name': module_name,
            'version': version,
            'requirement_path': requirement_path,
            'requirement_title': requirement_title,
            'created_at': created_at,
            'status': status
        },
        'environment': {
            'current_directory': current_directory,
            'current_file_path': current_file_path,
            'current_file_type': current_file_type
        },
        'updated_at': updated_at
    }
    
    return context


@composite
def partial_context_data(draw):
    """生成部分缺失的上下文数据"""
    base_context = draw(valid_context_data())
    
    # 随机删除一些字段
    if draw(st.booleans()):
        # 删除 active_requirement 中的一些字段
        active_req = base_context['active_requirement']
        fields_to_remove = draw(st.lists(
            st.sampled_from(['status', 'created_at']),
            max_size=2
        ))
        for field in fields_to_remove:
            active_req.pop(field, None)
    
    if draw(st.booleans()):
        # 删除 environment 中的一些字段
        env = base_context['environment']
        fields_to_remove = draw(st.lists(
            st.sampled_from(['current_file_path', 'current_file_type']),
            max_size=2
        ))
        for field in fields_to_remove:
            env.pop(field, None)
    
    if draw(st.booleans()):
        # 删除顶层字段
        base_context.pop('updated_at', None)
    
    return base_context


class TestContextManagerProperties:
    """上下文管理器属性测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.context_path = os.path.join(self.temp_dir, "test_context.yaml")
        self.manager = ContextManager(self.context_path)
        
    def teardown_method(self):
        """每个测试方法后的清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @given(context_data=valid_context_data())
    @settings(max_examples=100, deadline=None)
    def test_property_11_context_roundtrip_consistency(self, context_data):
        """
        属性 11：当前上下文一致性（Round-trip）
        
        验证需求：需求 17.1, 17.2, 17.3, 17.4
        
        属性：对于任何有效的上下文数据，写入后读取的内容应该与原始数据一致
        （除了自动添加的 updated_at 时间戳）
        """
        # 写入上下文
        write_success = self.manager.write_context(context_data)
        assert write_success, "写入上下文应该成功"
        
        # 读取上下文
        read_context = self.manager.read_context()
        assert read_context is not None, "读取上下文应该成功"
        
        # 验证核心数据一致性（忽略时间戳差异）
        assert read_context['active_requirement'] == context_data['active_requirement']
        assert read_context['environment'] == context_data['environment']
        
        # 验证时间戳被更新
        assert 'updated_at' in read_context
        
        # 验证时间戳格式有效
        try:
            datetime.fromisoformat(read_context['updated_at'])
        except ValueError:
            pytest.fail("updated_at 时间戳格式应该有效")
    
    @given(context_data=valid_context_data())
    @settings(max_examples=50, deadline=None)
    def test_property_11_validation_consistency(self, context_data):
        """
        属性 11 扩展：验证一致性
        
        属性：有效的上下文数据应该通过格式验证
        """
        is_valid, errors = self.manager.validate_context_format(context_data)
        assert is_valid, f"有效的上下文数据应该通过验证，错误: {errors}"
        assert len(errors) == 0, f"有效的上下文数据不应该有验证错误: {errors}"
    
    @given(
        initial_context=valid_context_data(),
        updates=st.dictionaries(
            st.sampled_from(['active_requirement', 'environment']),
            st.dictionaries(
                st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd', 'Pc')), min_size=1, max_size=20),
                st.text(alphabet=st.characters(whitelist_categories=('Ll', 'Lu', 'Nd', 'Pc', 'Pd', 'Zs')), min_size=1, max_size=50),
                min_size=1, max_size=3
            ),
            min_size=1, max_size=2
        )
    )
    @settings(max_examples=50, deadline=None)
    def test_property_11_update_consistency(self, initial_context, updates):
        """
        属性 11 扩展：更新一致性
        
        属性：更新上下文后，未更新的字段应该保持不变，更新的字段应该反映新值
        """
        # 过滤掉可能导致 YAML 序列化问题的更新
        filtered_updates = {}
        for section, section_updates in updates.items():
            filtered_section_updates = {}
            for field, value in section_updates.items():
                # 确保字段名和值都是可序列化的
                try:
                    yaml.dump({field: value})
                    filtered_section_updates[field] = value
                except:
                    continue
            if filtered_section_updates:
                filtered_updates[section] = filtered_section_updates
        
        if not filtered_updates:
            # 如果没有有效的更新，跳过这个测试
            assume(False)
        
        # 写入初始上下文
        self.manager.write_context(initial_context)
        
        # 更新上下文
        update_success = self.manager.update_context(filtered_updates)
        assert update_success, "更新上下文应该成功"
        
        # 读取更新后的上下文
        updated_context = self.manager.read_context()
        assert updated_context is not None, "读取更新后的上下文应该成功"
        
        # 验证更新的字段
        for section, section_updates in filtered_updates.items():
            if section in updated_context:
                for field, value in section_updates.items():
                    assert updated_context[section][field] == value, \
                        f"更新的字段 {section}.{field} 应该有新值"
        
        # 验证未更新的字段保持不变
        for section in ['active_requirement', 'environment']:
            if section not in filtered_updates:
                # 整个 section 未更新，应该保持不变
                assert updated_context[section] == initial_context[section], \
                    f"未更新的 section {section} 应该保持不变"
            else:
                # section 部分更新，检查未更新的字段
                for field, value in initial_context[section].items():
                    if field not in filtered_updates[section]:
                        assert updated_context[section][field] == value, \
                            f"未更新的字段 {section}.{field} 应该保持不变"
    
    @given(context_data=partial_context_data())
    @settings(max_examples=50, deadline=None)
    def test_property_11_fix_context_completeness(self, context_data):
        """
        属性 11 扩展：修复上下文完整性
        
        属性：修复后的上下文应该包含所有必需字段并通过验证
        """
        fixed_context, warnings = self.manager.validate_and_fix_context(context_data)
        
        # 验证修复后的上下文通过格式验证
        is_valid, errors = self.manager.validate_context_format(fixed_context)
        assert is_valid, f"修复后的上下文应该通过验证，错误: {errors}"
        assert len(errors) == 0, f"修复后的上下文不应该有验证错误: {errors}"
        
        # 验证所有必需字段存在
        assert 'active_requirement' in fixed_context
        assert 'environment' in fixed_context
        assert 'updated_at' in fixed_context
        
        # 验证 active_requirement 必需字段
        active_req = fixed_context['active_requirement']
        required_active_fields = ['module_name', 'version', 'requirement_path', 'requirement_title', 'created_at']
        for field in required_active_fields:
            assert field in active_req, f"修复后的 active_requirement 应该包含 {field}"
        
        # 验证 environment 必需字段
        env = fixed_context['environment']
        required_env_fields = ['current_directory', 'current_file_path', 'current_file_type']
        for field in required_env_fields:
            assert field in env, f"修复后的 environment 应该包含 {field}"
    
    @given(context_data=valid_context_data())
    @settings(max_examples=30, deadline=None)
    def test_property_11_backup_restore_consistency(self, context_data):
        """
        属性 11 扩展：备份恢复一致性
        
        属性：备份后恢复的上下文应该与原始上下文一致
        """
        # 写入原始上下文
        self.manager.write_context(context_data)
        
        # 备份上下文
        backup_path = self.manager.backup_context("test_backup")
        assert backup_path is not None, "备份应该成功"
        assert os.path.exists(backup_path), "备份文件应该存在"
        
        # 修改原始上下文
        modified_context = context_data.copy()
        modified_context['active_requirement'] = modified_context['active_requirement'].copy()
        modified_context['active_requirement']['module_name'] = 'modified-module'
        self.manager.write_context(modified_context)
        
        # 从备份恢复
        backup_manager = ContextManager(backup_path)
        restored_context = backup_manager.read_context()
        
        # 验证恢复的上下文与原始上下文一致（除了时间戳）
        assert restored_context['active_requirement'] == context_data['active_requirement']
        assert restored_context['environment'] == context_data['environment']
    
    @given(context_data=valid_context_data())
    @settings(max_examples=30, deadline=None)
    def test_property_11_delete_and_recreate_consistency(self, context_data):
        """
        属性 11 扩展：删除重建一致性
        
        属性：删除上下文后重新创建，应该能正常工作
        """
        # 写入上下文
        self.manager.write_context(context_data)
        assert self.manager.context_exists(), "上下文文件应该存在"
        
        # 删除上下文
        delete_success = self.manager.delete_context()
        assert delete_success, "删除上下文应该成功"
        assert not self.manager.context_exists(), "上下文文件应该不存在"
        
        # 重新创建上下文
        write_success = self.manager.write_context(context_data)
        assert write_success, "重新写入上下文应该成功"
        
        # 验证重新创建的上下文
        recreated_context = self.manager.read_context()
        assert recreated_context is not None, "重新读取上下文应该成功"
        assert recreated_context['active_requirement'] == context_data['active_requirement']
        assert recreated_context['environment'] == context_data['environment']


class TestContextManagerEdgeCases:
    """上下文管理器边缘情况测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.context_path = os.path.join(self.temp_dir, "edge_case_context.yaml")
        self.manager = ContextManager(self.context_path)
        
    def teardown_method(self):
        """每个测试方法后的清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @given(st.text(min_size=0, max_size=1000))
    @settings(max_examples=50, deadline=None)
    def test_property_11_invalid_yaml_handling(self, invalid_yaml_content):
        """
        属性 11 扩展：无效 YAML 处理
        
        属性：读取无效 YAML 文件应该抛出适当的异常
        """
        assume(invalid_yaml_content.strip() != "")  # 避免空内容
        assume(not invalid_yaml_content.startswith('#'))  # 避免纯注释
        
        # 写入无效 YAML 内容
        try:
            with open(self.context_path, 'w', encoding='utf-8') as f:
                f.write(invalid_yaml_content + ": [")  # 确保是无效 YAML
        except:
            assume(False)  # 跳过无法写入的内容
        
        # 尝试读取应该抛出异常
        with pytest.raises(yaml.YAMLError):
            self.manager.read_context()
    
    @given(st.dictionaries(st.text(), st.text(), min_size=0, max_size=10))
    @settings(max_examples=30, deadline=None)
    def test_property_11_arbitrary_dict_validation(self, arbitrary_dict):
        """
        属性 11 扩展：任意字典验证
        
        属性：任意字典应该能被验证（可能失败，但不应该崩溃）
        """
        try:
            is_valid, errors = self.manager.validate_context_format(arbitrary_dict)
            # 验证应该返回布尔值和错误列表
            assert isinstance(is_valid, bool)
            assert isinstance(errors, list)
            assert all(isinstance(error, str) for error in errors)
        except Exception as e:
            pytest.fail(f"验证任意字典不应该抛出异常: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])