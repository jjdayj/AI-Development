"""
优先级排序器的属性测试

使用 Hypothesis 框架进行基于属性的测试，验证：
- 属性 5：优先级排序正确性

需求追溯：
- 需求 6.1：按 Priority 从高到低排序
- 需求 6.2：Priority 相同时按模块名称字母顺序排序

作者: yangzhuo
日期: 2026-03-03
版本: v1.0
"""

import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings, example, assume
from typing import List, Dict, Any

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from priority_sorter import sort_by_priority, validate_module_data


# ============================================================
# 简化的策略生成器：生成测试数据
# ============================================================

# 简单的模块名称生成器
def simple_module_names():
    """生成简单的模块名称"""
    return st.sampled_from([
        'workflow', 'ai-dev', 'git-commit', 'git-rollback', 'doc-save',
        'module-a', 'module-b', 'module-c', 'test-x', 'test-y', 'test-z'
    ])

# 简单的版本号生成器
def simple_versions():
    """生成简单的版本号"""
    return st.sampled_from(['v1.0', 'v1.1', 'v2.0', 'v1.0-simple', 'v1.0-complex'])

# 简单的优先级生成器
def simple_priorities():
    """生成简单的优先级"""
    return st.integers(min_value=0, max_value=300)

# 生成简单的模块字典
@st.composite
def simple_module(draw):
    """生成简单的模块字典"""
    return {
        'name': draw(simple_module_names()),
        'version': draw(simple_versions()),
        'priority': draw(simple_priorities())
    }

# 生成唯一名称的模块列表
@st.composite
def unique_module_list(draw, min_size=0, max_size=10):
    """生成名称唯一的模块列表"""
    # 先生成足够多的模块
    modules = draw(st.lists(
        simple_module(),
        min_size=0,
        max_size=max_size * 2  # 生成更多模块以确保有足够的唯一名称
    ))
    
    # 去重，保留第一个出现的模块
    seen_names = set()
    unique_modules = []
    
    for module in modules:
        if module['name'] not in seen_names and len(unique_modules) < max_size:
            seen_names.add(module['name'])
            unique_modules.append(module)
    
    # 确保满足最小数量要求
    while len(unique_modules) < min_size:
        # 生成新的唯一名称模块
        new_name = f"generated-{len(unique_modules)}"
        unique_modules.append({
            'name': new_name,
            'version': 'v1.0',
            'priority': draw(simple_priorities())
        })
    
    return unique_modules


# ============================================================
# 属性 5：优先级排序正确性
# ============================================================

@given(modules=unique_module_list(min_size=0, max_size=15))
@settings(max_examples=100, deadline=None)
@example(modules=[])  # 空列表
@example(modules=[{'name': 'single', 'version': 'v1.0', 'priority': 100}])  # 单个模块
@example(modules=[  # 不同优先级
    {'name': 'high', 'version': 'v1.0', 'priority': 200},
    {'name': 'low', 'version': 'v1.0', 'priority': 100}
])
@example(modules=[  # 相同优先级
    {'name': 'zebra', 'version': 'v1.0', 'priority': 100},
    {'name': 'alpha', 'version': 'v1.0', 'priority': 100}
])
def test_property_5_priority_sorting_correctness(modules):
    """
    属性 5：优先级排序正确性
    
    Feature: dynamic-module-loader
    Property 5: 优先级排序正确性
    
    对于任意激活模块列表，排序后的列表应该满足：
    1. 对于列表中任意两个相邻模块 A 和 B（A 在 B 前面），A 的优先级 >= B 的优先级
    2. 如果 A 和 B 的优先级相同，则 A 的名称字母顺序 <= B 的名称字母顺序
    
    验证需求：需求 6.1, 6.2
    """
    # 跳过无效的模块数据
    errors = validate_module_data(modules)
    assume(len(errors) == 0)
    
    # 执行排序
    sorted_modules = sort_by_priority(modules)
    
    # 验证排序结果的长度
    assert len(sorted_modules) == len(modules), \
        f"排序后长度不匹配：原始 {len(modules)}，排序后 {len(sorted_modules)}"
    
    # 验证所有模块都被保留
    original_names = {m['name'] for m in modules}
    sorted_names = {m['name'] for m in sorted_modules}
    assert original_names == sorted_names, \
        f"排序后模块集合不匹配：原始 {original_names}，排序后 {sorted_names}"
    
    # 验证排序规则
    for i in range(len(sorted_modules) - 1):
        current = sorted_modules[i]
        next_module = sorted_modules[i + 1]
        
        current_priority = current['priority']
        next_priority = next_module['priority']
        current_name = current['name']
        next_name = next_module['name']
        
        # 规则 1：优先级应该从高到低排序
        assert current_priority >= next_priority, \
            f"优先级排序错误：模块 '{current_name}' (优先级 {current_priority}) " \
            f"应该在模块 '{next_name}' (优先级 {next_priority}) 之前"
        
        # 规则 2：如果优先级相同，名称应该按字母顺序排序
        if current_priority == next_priority:
            assert current_name <= next_name, \
                f"相同优先级时名称排序错误：模块 '{current_name}' " \
                f"应该在模块 '{next_name}' 之前（字母顺序）"


@given(st.just([
    {'name': 'workflow', 'version': 'v1.0', 'priority': 200},
    {'name': 'ai-dev', 'version': 'v1.0', 'priority': 100},
    {'name': 'doc-save', 'version': 'v1.0', 'priority': 90},
    {'name': 'git-commit', 'version': 'v1.0', 'priority': 80},
    {'name': 'git-rollback', 'version': 'v1.0', 'priority': 70}
]))
@settings(max_examples=10, deadline=None)
def test_property_5_kiro_modules_priority_sorting(modules):
    """
    属性 5 扩展：Kiro 真实模块的优先级排序
    
    Feature: dynamic-module-loader
    Property 5: Kiro 模块优先级排序正确性
    
    验证 Kiro 真实模块的排序符合预期顺序
    """
    sorted_modules = sort_by_priority(modules)
    
    # 验证 Kiro 模块的预期优先级顺序
    expected_order = ['workflow', 'ai-dev', 'doc-save', 'git-commit', 'git-rollback']
    actual_order = [m['name'] for m in sorted_modules]
    
    assert actual_order == expected_order, \
        f"Kiro 模块排序错误：实际 {actual_order}，期望 {expected_order}"


@given(
    priority=st.integers(min_value=50, max_value=150),
    names=st.lists(
        st.sampled_from(['alpha', 'beta', 'gamma', 'delta', 'epsilon']),
        min_size=2,
        max_size=5,
        unique=True
    )
)
@settings(max_examples=50, deadline=None)
def test_property_5_same_priority_alphabetical_sorting(priority, names):
    """
    属性 5 扩展：相同优先级时的字母排序
    
    Feature: dynamic-module-loader
    Property 5: 相同优先级字母排序正确性
    
    当所有模块优先级相同时，应该严格按照名称字母顺序排序
    """
    # 创建所有模块都有相同优先级的列表
    modules = []
    for name in names:
        modules.append({
            'name': name,
            'version': 'v1.0',
            'priority': priority
        })
    
    sorted_modules = sort_by_priority(modules)
    
    # 验证字母顺序
    actual_names = [m['name'] for m in sorted_modules]
    expected_names = sorted(names)
    
    assert actual_names == expected_names, \
        f"相同优先级时字母排序错误：实际 {actual_names}，期望 {expected_names}"


@given(
    base_priority=st.integers(min_value=50, max_value=150),
    module_count=st.integers(min_value=3, max_value=10)
)
@settings(max_examples=50, deadline=None)
def test_property_5_priority_range_sorting(base_priority, module_count):
    """
    属性 5 扩展：优先级范围排序
    
    Feature: dynamic-module-loader
    Property 5: 优先级范围排序正确性
    
    生成具有不同优先级的模块，验证排序的正确性
    """
    modules = []
    
    for i in range(module_count):
        # 生成递减的优先级
        priority = base_priority - (i * 10)
        modules.append({
            'name': f'module-{i:02d}',
            'version': 'v1.0',
            'priority': priority
        })
    
    # 随机打乱顺序
    import random
    random.shuffle(modules)
    
    sorted_modules = sort_by_priority(modules)
    
    # 验证优先级递减
    priorities = [m['priority'] for m in sorted_modules]
    expected_priorities = sorted(priorities, reverse=True)
    
    assert priorities == expected_priorities, \
        f"优先级排序错误：实际 {priorities}，期望 {expected_priorities}"


# ============================================================
# 边界情况和错误处理测试
# ============================================================

@given(st.just([]))
@settings(max_examples=10, deadline=None)
def test_property_5_empty_list_handling(modules):
    """
    属性 5 边界：空列表处理
    
    Feature: dynamic-module-loader
    Property 5: 空列表排序正确性
    """
    sorted_modules = sort_by_priority(modules)
    assert sorted_modules == []


@given(modules=st.lists(
    st.builds(
        dict,
        name=simple_module_names(),
        version=simple_versions(),
        priority=simple_priorities()
    ),
    min_size=1,
    max_size=1
))
@settings(max_examples=20, deadline=None)
def test_property_5_single_module_handling(modules):
    """
    属性 5 边界：单个模块处理
    
    Feature: dynamic-module-loader
    Property 5: 单个模块排序正确性
    """
    sorted_modules = sort_by_priority(modules)
    assert len(sorted_modules) == 1
    assert sorted_modules[0] == modules[0]


if __name__ == "__main__":
    # 运行所有属性测试
    import pytest
    pytest.main([__file__, "-v", "--tb=short"])