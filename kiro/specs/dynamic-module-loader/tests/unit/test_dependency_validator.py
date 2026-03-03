"""
依赖校验器单元测试

测试 dependency_validator.py 模块的所有功能：
- 依赖关系校验
- 循环依赖检测
- 拓扑排序
- 边界情况和错误处理

作者: yangzhuo
日期: 2026-03-03
版本: v1.0
"""

import sys
import os
import pytest

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from dependency_validator import (
    validate_dependencies,
    detect_circular_dependencies,
    get_dependency_order
)


class TestValidateDependencies:
    """测试依赖关系校验功能"""
    
    def test_no_dependencies(self):
        """测试：没有依赖的模块"""
        modules = [
            {'name': 'module-a', 'version': 'v1.0', 'priority': 100},
            {'name': 'module-b', 'version': 'v1.0', 'priority': 90}
        ]
        valid, invalid = validate_dependencies(modules)
        
        assert len(valid) == 2
        assert len(invalid) == 0
        assert valid[0]['name'] == 'module-a'
        assert valid[1]['name'] == 'module-b'
    
    def test_simple_dependency_satisfied(self):
        """测试：简单依赖关系满足"""
        modules = [
            {'name': 'module-a', 'version': 'v1.0', 'priority': 100, 'dependencies': []},
            {'name': 'module-b', 'version': 'v1.0', 'priority': 90, 'dependencies': ['module-a']}
        ]
        valid, invalid = validate_dependencies(modules)
        
        assert len(valid) == 2
        assert len(invalid) == 0
    
    def test_simple_dependency_missing(self):
        """测试：简单依赖关系缺失"""
        modules = [
            {'name': 'module-a', 'version': 'v1.0', 'priority': 100, 'dependencies': ['module-c']},
            {'name': 'module-b', 'version': 'v1.0', 'priority': 90, 'dependencies': ['module-a']}
        ]
        valid, invalid = validate_dependencies(modules)
        
        # module-a 缺少 module-c，所以被拒绝
        # module-b 依赖 module-a，module-a 存在但被拒绝，module-b 仍然通过（因为 module-a 在列表中）
        assert len(valid) == 1
        assert len(invalid) == 1
        
        # 检查失败原因
        assert invalid[0]['module']['name'] == 'module-a'
        assert 'module-c' in invalid[0]['reason']
    
    def test_chain_dependency_satisfied(self):
        """测试：链式依赖关系满足"""
        modules = [
            {'name': 'module-a', 'version': 'v1.0', 'priority': 100, 'dependencies': []},
            {'name': 'module-b', 'version': 'v1.0', 'priority': 90, 'dependencies': ['module-a']},
            {'name': 'module-c', 'version': 'v1.0', 'priority': 80, 'dependencies': ['module-b']}
        ]
        valid, invalid = validate_dependencies(modules)
        
        assert len(valid) == 3
        assert len(invalid) == 0
    
    def test_multiple_dependencies_satisfied(self):
        """测试：多个依赖关系满足"""
        modules = [
            {'name': 'module-a', 'version': 'v1.0', 'priority': 100, 'dependencies': []},
            {'name': 'module-b', 'version': 'v1.0', 'priority': 90, 'dependencies': []},
            {'name': 'module-c', 'version': 'v1.0', 'priority': 80, 'dependencies': ['module-a', 'module-b']}
        ]
        valid, invalid = validate_dependencies(modules)
        
        assert len(valid) == 3
        assert len(invalid) == 0
    
    def test_multiple_dependencies_partial_missing(self):
        """测试：多个依赖部分缺失"""
        modules = [
            {'name': 'module-a', 'version': 'v1.0', 'priority': 100, 'dependencies': []},
            {'name': 'module-c', 'version': 'v1.0', 'priority': 80, 'dependencies': ['module-a', 'module-b']}
        ]
        valid, invalid = validate_dependencies(modules)
        
        assert len(valid) == 1
        assert len(invalid) == 1
        assert invalid[0]['module']['name'] == 'module-c'
        assert 'module-b' in invalid[0]['reason']
    
    def test_empty_dependencies_list(self):
        """测试：空依赖列表"""
        modules = [
            {'name': 'module-a', 'version': 'v1.0', 'priority': 100, 'dependencies': []}
        ]
        valid, invalid = validate_dependencies(modules)
        
        assert len(valid) == 1
        assert len(invalid) == 0
    
    def test_empty_modules_list(self):
        """测试：空模块列表"""
        modules = []
        valid, invalid = validate_dependencies(modules)
        
        assert len(valid) == 0
        assert len(invalid) == 0


class TestCircularDependencies:
    """测试循环依赖检测功能"""
    
    def test_simple_circular_dependency(self):
        """测试：简单循环依赖（A -> B -> A）"""
        modules = [
            {'name': 'module-a', 'dependencies': ['module-b']},
            {'name': 'module-b', 'dependencies': ['module-a']}
        ]
        circular = detect_circular_dependencies(modules)
        
        assert len(circular) == 2
        assert 'module-a' in circular
        assert 'module-b' in circular
    
    def test_three_node_circular_dependency(self):
        """测试：三节点循环依赖（A -> B -> C -> A）"""
        modules = [
            {'name': 'module-a', 'dependencies': ['module-b']},
            {'name': 'module-b', 'dependencies': ['module-c']},
            {'name': 'module-c', 'dependencies': ['module-a']}
        ]
        circular = detect_circular_dependencies(modules)
        
        assert len(circular) == 3
        assert 'module-a' in circular
        assert 'module-b' in circular
        assert 'module-c' in circular
    
    def test_self_dependency(self):
        """测试：自依赖（A -> A）"""
        modules = [
            {'name': 'module-a', 'dependencies': ['module-a']}
        ]
        circular = detect_circular_dependencies(modules)
        
        assert len(circular) == 1
        assert 'module-a' in circular
    
    def test_no_circular_dependency(self):
        """测试：无循环依赖"""
        modules = [
            {'name': 'module-a', 'dependencies': []},
            {'name': 'module-b', 'dependencies': ['module-a']},
            {'name': 'module-c', 'dependencies': ['module-b']}
        ]
        circular = detect_circular_dependencies(modules)
        
        assert len(circular) == 0
    
    def test_complex_graph_with_circular(self):
        """测试：复杂依赖图中的循环依赖"""
        modules = [
            {'name': 'module-a', 'dependencies': ['module-b']},
            {'name': 'module-b', 'dependencies': ['module-c']},
            {'name': 'module-c', 'dependencies': ['module-a']},
            {'name': 'module-d', 'dependencies': ['module-a']},
            {'name': 'module-e', 'dependencies': []}
        ]
        circular = detect_circular_dependencies(modules)
        
        # 只有 A, B, C 在循环中
        assert 'module-a' in circular
        assert 'module-b' in circular
        assert 'module-c' in circular
        assert 'module-d' not in circular
        assert 'module-e' not in circular
    
    def test_multiple_separate_cycles(self):
        """测试：多个独立的循环"""
        modules = [
            {'name': 'module-a', 'dependencies': ['module-b']},
            {'name': 'module-b', 'dependencies': ['module-a']},
            {'name': 'module-c', 'dependencies': ['module-d']},
            {'name': 'module-d', 'dependencies': ['module-c']}
        ]
        circular = detect_circular_dependencies(modules)
        
        assert len(circular) == 4
        assert 'module-a' in circular
        assert 'module-b' in circular
        assert 'module-c' in circular
        assert 'module-d' in circular
    
    def test_missing_dependency_node(self):
        """测试：依赖的节点不存在（不应该导致循环检测失败）"""
        modules = [
            {'name': 'module-a', 'dependencies': ['module-b']},
            {'name': 'module-b', 'dependencies': ['module-c']}
            # module-c 不存在
        ]
        circular = detect_circular_dependencies(modules)
        
        assert len(circular) == 0


class TestValidateDependenciesWithCircular:
    """测试依赖校验与循环依赖的集成"""
    
    def test_circular_dependency_rejected(self):
        """测试：循环依赖的模块被拒绝"""
        modules = [
            {'name': 'module-a', 'version': 'v1.0', 'priority': 100, 'dependencies': ['module-b']},
            {'name': 'module-b', 'version': 'v1.0', 'priority': 90, 'dependencies': ['module-a']}
        ]
        valid, invalid = validate_dependencies(modules)
        
        assert len(valid) == 0
        assert len(invalid) == 2
        
        # 检查失败原因包含 "循环依赖"
        for item in invalid:
            assert '循环依赖' in item['reason']
    
    def test_circular_and_missing_dependencies(self):
        """测试：同时存在循环依赖和缺失依赖"""
        modules = [
            {'name': 'module-a', 'version': 'v1.0', 'priority': 100, 'dependencies': ['module-b']},
            {'name': 'module-b', 'version': 'v1.0', 'priority': 90, 'dependencies': ['module-a']},
            {'name': 'module-c', 'version': 'v1.0', 'priority': 80, 'dependencies': ['module-d']}
        ]
        valid, invalid = validate_dependencies(modules)
        
        assert len(valid) == 0
        assert len(invalid) == 3
        
        # module-a 和 module-b 因循环依赖被拒绝
        circular_modules = [item for item in invalid if '循环依赖' in item['reason']]
        assert len(circular_modules) == 2
        
        # module-c 因缺失依赖被拒绝
        missing_modules = [item for item in invalid if '缺少依赖' in item['reason']]
        assert len(missing_modules) == 1
        assert missing_modules[0]['module']['name'] == 'module-c'


class TestDependencyOrder:
    """测试拓扑排序功能"""
    
    def test_simple_order(self):
        """测试：简单依赖顺序"""
        modules = [
            {'name': 'module-b', 'dependencies': ['module-a']},
            {'name': 'module-a', 'dependencies': []}
        ]
        order = get_dependency_order(modules)
        
        assert len(order) == 2
        assert order.index('module-a') < order.index('module-b')
    
    def test_chain_order(self):
        """测试：链式依赖顺序"""
        modules = [
            {'name': 'module-c', 'dependencies': ['module-b']},
            {'name': 'module-b', 'dependencies': ['module-a']},
            {'name': 'module-a', 'dependencies': []}
        ]
        order = get_dependency_order(modules)
        
        assert len(order) == 3
        assert order.index('module-a') < order.index('module-b')
        assert order.index('module-b') < order.index('module-c')
    
    def test_diamond_dependency(self):
        """测试：菱形依赖"""
        modules = [
            {'name': 'module-a', 'dependencies': []},
            {'name': 'module-b', 'dependencies': ['module-a']},
            {'name': 'module-c', 'dependencies': ['module-a']},
            {'name': 'module-d', 'dependencies': ['module-b', 'module-c']}
        ]
        order = get_dependency_order(modules)
        
        assert len(order) == 4
        assert order.index('module-a') < order.index('module-b')
        assert order.index('module-a') < order.index('module-c')
        assert order.index('module-b') < order.index('module-d')
        assert order.index('module-c') < order.index('module-d')
    
    def test_circular_dependency_returns_empty(self):
        """测试：循环依赖返回空列表"""
        modules = [
            {'name': 'module-a', 'dependencies': ['module-b']},
            {'name': 'module-b', 'dependencies': ['module-a']}
        ]
        order = get_dependency_order(modules)
        
        assert len(order) == 0
    
    def test_no_dependencies(self):
        """测试：无依赖关系"""
        modules = [
            {'name': 'module-a', 'dependencies': []},
            {'name': 'module-b', 'dependencies': []},
            {'name': 'module-c', 'dependencies': []}
        ]
        order = get_dependency_order(modules)
        
        assert len(order) == 3
        # 无依赖关系时，顺序可以是任意的
        assert set(order) == {'module-a', 'module-b', 'module-c'}


class TestEdgeCases:
    """测试边界情况"""
    
    def test_module_without_dependencies_field(self):
        """测试：模块没有 dependencies 字段"""
        modules = [
            {'name': 'module-a', 'version': 'v1.0', 'priority': 100}
        ]
        valid, invalid = validate_dependencies(modules)
        
        assert len(valid) == 1
        assert len(invalid) == 0
    
    def test_empty_string_dependency(self):
        """测试：空字符串依赖"""
        modules = [
            {'name': 'module-a', 'version': 'v1.0', 'priority': 100, 'dependencies': ['']}
        ]
        valid, invalid = validate_dependencies(modules)
        
        # 空字符串依赖应该被视为缺失依赖
        assert len(valid) == 0
        assert len(invalid) == 1
    
    def test_duplicate_dependencies(self):
        """测试：重复的依赖"""
        modules = [
            {'name': 'module-a', 'version': 'v1.0', 'priority': 100, 'dependencies': []},
            {'name': 'module-b', 'version': 'v1.0', 'priority': 90, 'dependencies': ['module-a', 'module-a']}
        ]
        valid, invalid = validate_dependencies(modules)
        
        # 重复依赖不应该影响校验结果
        assert len(valid) == 2
        assert len(invalid) == 0
    
    def test_large_dependency_graph(self):
        """测试：大型依赖图"""
        modules = []
        for i in range(100):
            if i == 0:
                modules.append({'name': f'module-{i}', 'dependencies': []})
            else:
                modules.append({'name': f'module-{i}', 'dependencies': [f'module-{i-1}']})
        
        valid, invalid = validate_dependencies(modules)
        
        assert len(valid) == 100
        assert len(invalid) == 0


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v', '--tb=short'])
