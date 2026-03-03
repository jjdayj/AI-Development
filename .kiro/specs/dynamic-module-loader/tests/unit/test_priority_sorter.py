"""
优先级排序器单元测试

测试 priority_sorter.py 模块的各种功能。

需求追溯：
- 需求 6.1：按 Priority 从高到低排序
- 需求 6.2：Priority 相同时按模块名称字母顺序排序
"""

import pytest
from src.priority_sorter import (
    sort_by_priority,
    validate_module_data,
    get_sorting_key,
    sort_by_priority_with_validation
)


class TestSortByPriority:
    """测试 sort_by_priority 函数"""
    
    def test_empty_list(self):
        """测试空列表"""
        result = sort_by_priority([])
        assert result == []
    
    def test_single_module(self):
        """测试单个模块"""
        modules = [
            {'name': 'workflow', 'version': 'v1.0', 'priority': 200}
        ]
        result = sort_by_priority(modules)
        assert len(result) == 1
        assert result[0]['name'] == 'workflow'
    
    def test_different_priorities(self):
        """测试不同优先级的排序"""
        modules = [
            {'name': 'git-commit', 'version': 'v1.0', 'priority': 80},
            {'name': 'workflow', 'version': 'v1.0', 'priority': 200},
            {'name': 'ai-dev', 'version': 'v1.0', 'priority': 100}
        ]
        result = sort_by_priority(modules)
        
        # 验证排序顺序：workflow (200) > ai-dev (100) > git-commit (80)
        assert len(result) == 3
        assert result[0]['name'] == 'workflow'
        assert result[0]['priority'] == 200
        assert result[1]['name'] == 'ai-dev'
        assert result[1]['priority'] == 100
        assert result[2]['name'] == 'git-commit'
        assert result[2]['priority'] == 80
    
    def test_same_priority_alphabetical_order(self):
        """测试相同优先级按字母顺序排序"""
        modules = [
            {'name': 'zebra', 'version': 'v1.0', 'priority': 100},
            {'name': 'alpha', 'version': 'v1.0', 'priority': 100},
            {'name': 'beta', 'version': 'v1.0', 'priority': 100}
        ]
        result = sort_by_priority(modules)
        
        # 验证字母顺序：alpha < beta < zebra
        assert len(result) == 3
        assert result[0]['name'] == 'alpha'
        assert result[1]['name'] == 'beta'
        assert result[2]['name'] == 'zebra'
        
        # 验证优先级都相同
        for module in result:
            assert module['priority'] == 100
    
    def test_mixed_priority_and_alphabetical(self):
        """测试混合优先级和字母顺序"""
        modules = [
            {'name': 'git-rollback', 'version': 'v1.0', 'priority': 70},
            {'name': 'git-commit', 'version': 'v1.0', 'priority': 80},
            {'name': 'workflow', 'version': 'v1.0', 'priority': 200},
            {'name': 'ai-dev', 'version': 'v1.0', 'priority': 100},
            {'name': 'doc-save', 'version': 'v1.0', 'priority': 80}  # 与 git-commit 同优先级
        ]
        result = sort_by_priority(modules)
        
        # 验证排序结果
        expected_order = ['workflow', 'ai-dev', 'doc-save', 'git-commit', 'git-rollback']
        actual_order = [m['name'] for m in result]
        assert actual_order == expected_order
        
        # 验证优先级顺序
        priorities = [m['priority'] for m in result]
        assert priorities == [200, 100, 80, 80, 70]
    
    def test_float_priorities(self):
        """测试浮点数优先级"""
        modules = [
            {'name': 'module-a', 'version': 'v1.0', 'priority': 100.5},
            {'name': 'module-b', 'version': 'v1.0', 'priority': 100.1},
            {'name': 'module-c', 'version': 'v1.0', 'priority': 100.9}
        ]
        result = sort_by_priority(modules)
        
        # 验证浮点数排序
        expected_order = ['module-c', 'module-a', 'module-b']
        actual_order = [m['name'] for m in result]
        assert actual_order == expected_order
    
    def test_negative_priorities(self):
        """测试负数优先级"""
        modules = [
            {'name': 'module-a', 'version': 'v1.0', 'priority': -10},
            {'name': 'module-b', 'version': 'v1.0', 'priority': 0},
            {'name': 'module-c', 'version': 'v1.0', 'priority': 10}
        ]
        result = sort_by_priority(modules)
        
        # 验证负数排序
        expected_order = ['module-c', 'module-b', 'module-a']
        actual_order = [m['name'] for m in result]
        assert actual_order == expected_order
    
    def test_preserve_other_fields(self):
        """测试保留其他字段"""
        modules = [
            {
                'name': 'module-a',
                'version': 'v1.0',
                'priority': 100,
                'enabled': True,
                'description': 'Module A'
            },
            {
                'name': 'module-b',
                'version': 'v2.0',
                'priority': 200,
                'enabled': False,
                'description': 'Module B'
            }
        ]
        result = sort_by_priority(modules)
        
        # 验证其他字段被保留
        assert result[0]['name'] == 'module-b'
        assert result[0]['version'] == 'v2.0'
        assert result[0]['enabled'] is False
        assert result[0]['description'] == 'Module B'
        
        assert result[1]['name'] == 'module-a'
        assert result[1]['version'] == 'v1.0'
        assert result[1]['enabled'] is True
        assert result[1]['description'] == 'Module A'
    
    def test_missing_name_field(self):
        """测试缺少 name 字段"""
        modules = [
            {'version': 'v1.0', 'priority': 100}
        ]
        with pytest.raises(KeyError, match="模块缺少必需字段 'name'"):
            sort_by_priority(modules)
    
    def test_missing_priority_field(self):
        """测试缺少 priority 字段"""
        modules = [
            {'name': 'module-a', 'version': 'v1.0'}
        ]
        with pytest.raises(KeyError, match="模块缺少必需字段 'priority'"):
            sort_by_priority(modules)
    
    def test_invalid_module_type(self):
        """测试无效的模块类型"""
        modules = [
            "not a dict"
        ]
        with pytest.raises(TypeError, match="模块必须是字典类型"):
            sort_by_priority(modules)
    
    def test_invalid_priority_type(self):
        """测试无效的优先级类型"""
        modules = [
            {'name': 'module-a', 'priority': 'high'}
        ]
        with pytest.raises(TypeError, match="priority 必须是数字类型"):
            sort_by_priority(modules)


class TestValidateModuleData:
    """测试 validate_module_data 函数"""
    
    def test_valid_modules(self):
        """测试有效的模块数据"""
        modules = [
            {'name': 'module-a', 'priority': 100},
            {'name': 'module-b', 'priority': 200}
        ]
        errors = validate_module_data(modules)
        assert errors == []
    
    def test_empty_list(self):
        """测试空列表"""
        errors = validate_module_data([])
        assert errors == []
    
    def test_invalid_modules_type(self):
        """测试无效的 modules 类型"""
        errors = validate_module_data("not a list")
        assert len(errors) == 1
        assert "modules 必须是列表类型" in errors[0]
    
    def test_invalid_module_type(self):
        """测试无效的模块类型"""
        modules = ["not a dict", {'name': 'valid', 'priority': 100}]
        errors = validate_module_data(modules)
        assert len(errors) == 1
        assert "模块 0 必须是字典类型" in errors[0]
    
    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        modules = [
            {'name': 'module-a'},  # 缺少 priority
            {'priority': 100},     # 缺少 name
            {}                     # 缺少所有字段
        ]
        errors = validate_module_data(modules)
        assert len(errors) == 4  # 3个模块，4个错误
        assert any("缺少必需字段 'priority'" in error for error in errors)
        assert any("缺少必需字段 'name'" in error for error in errors)
    
    def test_invalid_field_types(self):
        """测试无效的字段类型"""
        modules = [
            {'name': 123, 'priority': 100},      # name 不是字符串
            {'name': 'module-b', 'priority': 'high'}  # priority 不是数字
        ]
        errors = validate_module_data(modules)
        assert len(errors) == 2
        assert any("'name' 必须是字符串类型" in error for error in errors)
        assert any("'priority' 必须是数字类型" in error for error in errors)


class TestGetSortingKey:
    """测试 get_sorting_key 函数"""
    
    def test_sorting_key(self):
        """测试排序键生成"""
        module = {'name': 'test-module', 'priority': 100}
        key = get_sorting_key(module)
        assert key == (-100, 'test-module')
    
    def test_negative_priority_key(self):
        """测试负数优先级的排序键"""
        module = {'name': 'test-module', 'priority': -50}
        key = get_sorting_key(module)
        assert key == (50, 'test-module')  # -(-50) = 50
    
    def test_float_priority_key(self):
        """测试浮点数优先级的排序键"""
        module = {'name': 'test-module', 'priority': 100.5}
        key = get_sorting_key(module)
        assert key == (-100.5, 'test-module')


class TestSortByPriorityWithValidation:
    """测试 sort_by_priority_with_validation 函数"""
    
    def test_valid_modules(self):
        """测试有效的模块数据"""
        modules = [
            {'name': 'module-b', 'priority': 100},
            {'name': 'module-a', 'priority': 200}
        ]
        result, errors = sort_by_priority_with_validation(modules)
        
        assert errors == []
        assert len(result) == 2
        assert result[0]['name'] == 'module-a'  # 优先级更高
        assert result[1]['name'] == 'module-b'
    
    def test_invalid_modules(self):
        """测试无效的模块数据"""
        modules = [
            {'name': 'module-a'},  # 缺少 priority
            "not a dict"           # 不是字典
        ]
        result, errors = sort_by_priority_with_validation(modules)
        
        assert result == []
        assert len(errors) > 0
        assert any("缺少必需字段" in error for error in errors)
        assert any("必须是字典类型" in error for error in errors)
    
    def test_empty_list(self):
        """测试空列表"""
        result, errors = sort_by_priority_with_validation([])
        assert result == []
        assert errors == []


class TestRealWorldScenarios:
    """测试真实世界场景"""
    
    def test_kiro_modules_sorting(self):
        """测试 Kiro 模块的实际排序场景"""
        modules = [
            {'name': 'git-rollback', 'version': 'v1.0', 'priority': 70, 'enabled': True},
            {'name': 'git-commit', 'version': 'v1.0', 'priority': 80, 'enabled': True},
            {'name': 'doc-save', 'version': 'v1.0', 'priority': 90, 'enabled': True},
            {'name': 'ai-dev', 'version': 'v1.0', 'priority': 100, 'enabled': True},
            {'name': 'workflow', 'version': 'v1.0-simple', 'priority': 200, 'enabled': True}
        ]
        
        result = sort_by_priority(modules)
        
        # 验证 Kiro 模块的预期排序
        expected_order = ['workflow', 'ai-dev', 'doc-save', 'git-commit', 'git-rollback']
        actual_order = [m['name'] for m in result]
        assert actual_order == expected_order
        
        # 验证优先级递减
        priorities = [m['priority'] for m in result]
        assert priorities == [200, 100, 90, 80, 70]
    
    def test_workflow_versions_sorting(self):
        """测试 workflow 模块不同版本的排序"""
        modules = [
            {'name': 'workflow', 'version': 'v1.0-simple', 'priority': 200},
            {'name': 'workflow', 'version': 'v1.0-complex', 'priority': 200}
        ]
        
        result = sort_by_priority(modules)
        
        # 两个模块优先级相同，应该按名称排序（都是 'workflow'，所以顺序保持不变）
        assert len(result) == 2
        assert all(m['priority'] == 200 for m in result)
        assert all(m['name'] == 'workflow' for m in result)
    
    def test_large_module_list(self):
        """测试大量模块的排序"""
        # 生成 100 个模块
        modules = []
        for i in range(100):
            modules.append({
                'name': f'module-{i:03d}',
                'version': 'v1.0',
                'priority': i % 10  # 优先级 0-9 循环
            })
        
        result = sort_by_priority(modules)
        
        # 验证排序正确性
        assert len(result) == 100
        
        # 验证优先级递减
        for i in range(len(result) - 1):
            current_priority = result[i]['priority']
            next_priority = result[i + 1]['priority']
            
            if current_priority == next_priority:
                # 优先级相同时，名称应该按字母顺序
                assert result[i]['name'] <= result[i + 1]['name']
            else:
                # 优先级应该递减
                assert current_priority >= next_priority