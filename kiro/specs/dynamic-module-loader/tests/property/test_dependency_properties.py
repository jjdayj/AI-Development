"""
依赖校验器的属性测试

使用 Hypothesis 框架进行基于属性的测试，验证：
- 属性 14：依赖关系校验正确性
- 属性 15：循环依赖检测正确性

作者: yangzhuo
日期: 2026-03-03
版本: v1.0
"""

import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings, example, assume

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from dependency_validator import (
    validate_dependencies,
    detect_circular_dependencies,
    get_dependency_order
)


# ============================================================
# 策略生成器：生成测试数据
# ============================================================

# 生成模块名称
@st.composite
def module_name(draw):
    """生成模块名称"""
    return draw(st.sampled_from([
        'module-a', 'module-b', 'module-c', 'module-d', 'module-e',
        'workflow', 'ai-dev', 'git-commit', 'git-rollback', 'doc-save'
    ]))


# 生成模块列表（无依赖）
@st.composite
def modules_without_dependencies(draw):
    """生成没有依赖的模块列表"""
    num_modules = draw(st.integers(min_value=0, max_value=10))
    modules = []
    used_names = set()
    
    for i in range(num_modules):
        name = f'module-{i}'
        used_names.add(name)
        modules.append({
            'name': name,
            'version': 'v1.0',
            'priority': draw(st.integers(min_value=0, max_value=1000)),
            'dependencies': []
        })
    
    return modules


# 生成模块列表（有依赖）
@st.composite
def modules_with_dependencies(draw, allow_circular=False):
    """生成有依赖的模块列表"""
    num_modules = draw(st.integers(min_value=1, max_value=8))
    modules = []
    module_names = [f'module-{i}' for i in range(num_modules)]
    
    for i, name in enumerate(module_names):
        # 生成依赖列表（只依赖已经存在的模块）
        if allow_circular:
            # 允许循环依赖：可以依赖任何模块
            possible_deps = module_names
        else:
            # 不允许循环依赖：只能依赖索引小于当前模块的模块
            possible_deps = module_names[:i]
        
        if possible_deps:
            num_deps = draw(st.integers(min_value=0, max_value=min(3, len(possible_deps))))
            dependencies = draw(st.lists(
                st.sampled_from(possible_deps),
                min_size=num_deps,
                max_size=num_deps,
                unique=True
            ))
        else:
            dependencies = []
        
        modules.append({
            'name': name,
            'version': 'v1.0',
            'priority': draw(st.integers(min_value=0, max_value=1000)),
            'dependencies': dependencies
        })
    
    return modules


# 生成有缺失依赖的模块列表
@st.composite
def modules_with_missing_dependencies(draw):
    """生成有缺失依赖的模块列表"""
    num_modules = draw(st.integers(min_value=1, max_value=8))
    modules = []
    module_names = [f'module-{i}' for i in range(num_modules)]
    
    for i, name in enumerate(module_names):
        # 随机决定是否添加缺失的依赖
        if draw(st.booleans()):
            # 添加一个不存在的依赖
            missing_dep = f'missing-module-{i}'
            dependencies = [missing_dep]
        else:
            # 正常依赖
            possible_deps = module_names[:i]
            if possible_deps:
                num_deps = draw(st.integers(min_value=0, max_value=min(2, len(possible_deps))))
                dependencies = draw(st.lists(
                    st.sampled_from(possible_deps),
                    min_size=num_deps,
                    max_size=num_deps,
                    unique=True
                ))
            else:
                dependencies = []
        
        modules.append({
            'name': name,
            'version': 'v1.0',
            'priority': draw(st.integers(min_value=0, max_value=1000)),
            'dependencies': dependencies
        })
    
    return modules


# 生成循环依赖的模块列表
@st.composite
def modules_with_circular_dependencies(draw):
    """生成有循环依赖的模块列表"""
    cycle_size = draw(st.integers(min_value=2, max_value=5))
    modules = []
    
    for i in range(cycle_size):
        name = f'module-{i}'
        # 每个模块依赖下一个模块，最后一个模块依赖第一个模块
        next_module = f'module-{(i + 1) % cycle_size}'
        
        modules.append({
            'name': name,
            'version': 'v1.0',
            'priority': draw(st.integers(min_value=0, max_value=1000)),
            'dependencies': [next_module]
        })
    
    return modules


# ============================================================
# 属性 14：依赖关系校验正确性
# ============================================================

@given(modules=modules_without_dependencies())
@settings(max_examples=100, deadline=None)
@example(modules=[])
@example(modules=[{'name': 'module-0', 'version': 'v1.0', 'priority': 100, 'dependencies': []}])
def test_property_14_no_dependencies_all_valid(modules):
    """
    属性 14：依赖关系校验正确性（无依赖）
    
    Feature: dynamic-module-loader
    Property 14: 依赖关系校验正确性
    
    对于任意没有依赖的模块列表，所有模块都应该通过校验
    """
    valid, invalid = validate_dependencies(modules)
    
    # 所有模块都应该通过校验
    assert len(valid) == len(modules), f"无依赖的模块应该全部通过校验"
    assert len(invalid) == 0, f"不应该有失败的模块"
    
    # 验证返回的模块与输入的模块一致
    valid_names = {m['name'] for m in valid}
    input_names = {m['name'] for m in modules}
    assert valid_names == input_names, f"返回的模块名称应该与输入一致"


@given(modules=modules_with_dependencies(allow_circular=False))
@settings(max_examples=100, deadline=None)
@example(modules=[
    {'name': 'module-0', 'version': 'v1.0', 'priority': 100, 'dependencies': []},
    {'name': 'module-1', 'version': 'v1.0', 'priority': 90, 'dependencies': ['module-0']}
])
def test_property_14_valid_dependencies_all_pass(modules):
    """
    属性 14：依赖关系校验正确性（有效依赖）
    
    Feature: dynamic-module-loader
    Property 14: 依赖关系校验正确性
    
    对于任意有效的依赖关系（无循环、无缺失），所有模块都应该通过校验
    """
    valid, invalid = validate_dependencies(modules)
    
    # 所有模块都应该通过校验
    assert len(valid) == len(modules), f"有效依赖的模块应该全部通过校验"
    assert len(invalid) == 0, f"不应该有失败的模块"


@given(modules=modules_with_missing_dependencies())
@settings(max_examples=100, deadline=None)
def test_property_14_missing_dependencies_rejected(modules):
    """
    属性 14：依赖关系校验正确性（缺失依赖）
    
    Feature: dynamic-module-loader
    Property 14: 依赖关系校验正确性
    
    对于任意有缺失依赖的模块，该模块应该被拒绝
    """
    valid, invalid = validate_dependencies(modules)
    
    # 计算有缺失依赖的模块数量
    module_names = {m['name'] for m in modules}
    modules_with_missing = []
    
    for module in modules:
        dependencies = module.get('dependencies', [])
        has_missing = any(dep not in module_names for dep in dependencies)
        if has_missing:
            modules_with_missing.append(module['name'])
    
    # 验证所有有缺失依赖的模块都被拒绝
    invalid_names = {item['module']['name'] for item in invalid}
    for module_name in modules_with_missing:
        assert module_name in invalid_names, f"模块 {module_name} 有缺失依赖，应该被拒绝"


@given(modules=modules_with_dependencies(allow_circular=False))
@settings(max_examples=100, deadline=None)
def test_property_14_dependency_consistency(modules):
    """
    属性 14 扩展：依赖关系一致性
    
    Feature: dynamic-module-loader
    Property 14: 依赖关系校验正确性（一致性）
    
    对于任意模块列表，valid + invalid 的数量应该等于输入模块的数量
    """
    valid, invalid = validate_dependencies(modules)
    
    total = len(valid) + len(invalid)
    assert total == len(modules), f"有效模块 + 无效模块应该等于输入模块数量"
    
    # 验证没有重复
    valid_names = {m['name'] for m in valid}
    invalid_names = {item['module']['name'] for item in invalid}
    assert len(valid_names & invalid_names) == 0, f"有效和无效模块不应该有重复"


# ============================================================
# 属性 15：循环依赖检测正确性
# ============================================================

@given(modules=modules_without_dependencies())
@settings(max_examples=100, deadline=None)
@example(modules=[])
def test_property_15_no_dependencies_no_circular(modules):
    """
    属性 15：循环依赖检测正确性（无依赖）
    
    Feature: dynamic-module-loader
    Property 15: 循环依赖检测正确性
    
    对于任意没有依赖的模块列表，不应该检测到循环依赖
    """
    circular = detect_circular_dependencies(modules)
    
    assert len(circular) == 0, f"无依赖的模块不应该有循环依赖"


@given(modules=modules_with_dependencies(allow_circular=False))
@settings(max_examples=100, deadline=None)
def test_property_15_acyclic_graph_no_circular(modules):
    """
    属性 15：循环依赖检测正确性（无环图）
    
    Feature: dynamic-module-loader
    Property 15: 循环依赖检测正确性
    
    对于任意无环的依赖图，不应该检测到循环依赖
    """
    circular = detect_circular_dependencies(modules)
    
    assert len(circular) == 0, f"无环依赖图不应该检测到循环依赖"


@given(modules=modules_with_circular_dependencies())
@settings(max_examples=100, deadline=None)
@example(modules=[
    {'name': 'module-0', 'version': 'v1.0', 'priority': 100, 'dependencies': ['module-1']},
    {'name': 'module-1', 'version': 'v1.0', 'priority': 90, 'dependencies': ['module-0']}
])
def test_property_15_circular_graph_detected(modules):
    """
    属性 15：循环依赖检测正确性（有环图）
    
    Feature: dynamic-module-loader
    Property 15: 循环依赖检测正确性
    
    对于任意有环的依赖图，应该检测到循环依赖
    """
    circular = detect_circular_dependencies(modules)
    
    # 应该检测到循环依赖
    assert len(circular) > 0, f"有环依赖图应该检测到循环依赖"
    
    # 循环中的模块数量应该 >= 2（至少两个模块形成环）
    assert len(circular) >= 2, f"循环依赖至少涉及 2 个模块"
    
    # 所有检测到的模块都应该在输入模块中
    module_names = {m['name'] for m in modules}
    for module_name in circular:
        assert module_name in module_names, f"检测到的循环模块 {module_name} 应该在输入模块中"


@given(modules=modules_with_circular_dependencies())
@settings(max_examples=50, deadline=None)
def test_property_15_circular_modules_rejected(modules):
    """
    属性 15 扩展：循环依赖模块被拒绝
    
    Feature: dynamic-module-loader
    Property 15: 循环依赖检测正确性（拒绝）
    
    对于任意有循环依赖的模块，validate_dependencies 应该拒绝它们
    """
    circular = detect_circular_dependencies(modules)
    valid, invalid = validate_dependencies(modules)
    
    # 所有循环依赖的模块都应该被拒绝
    invalid_names = {item['module']['name'] for item in invalid}
    for module_name in circular:
        assert module_name in invalid_names, f"循环依赖模块 {module_name} 应该被拒绝"


# ============================================================
# 属性 15 扩展：拓扑排序正确性
# ============================================================

@given(modules=modules_with_dependencies(allow_circular=False))
@settings(max_examples=100, deadline=None)
def test_property_15_topological_order_correctness(modules):
    """
    属性 15 扩展：拓扑排序正确性
    
    Feature: dynamic-module-loader
    Property 15: 循环依赖检测正确性（拓扑排序）
    
    对于任意无环的依赖图，拓扑排序应该满足：
    对于每个模块，它的所有依赖都应该在它之前
    """
    order = get_dependency_order(modules)
    
    # 如果没有循环依赖，应该返回非空列表
    if len(modules) > 0:
        assert len(order) == len(modules), f"拓扑排序应该包含所有模块"
    
    # 构建模块名称到索引的映射
    order_index = {name: i for i, name in enumerate(order)}
    
    # 验证每个模块的依赖都在它之前
    for module in modules:
        module_name = module['name']
        dependencies = module.get('dependencies', [])
        
        if module_name in order_index:
            module_index = order_index[module_name]
            
            for dep in dependencies:
                if dep in order_index:
                    dep_index = order_index[dep]
                    assert dep_index < module_index, (
                        f"依赖 {dep} 应该在模块 {module_name} 之前，"
                        f"但 {dep} 的索引是 {dep_index}，{module_name} 的索引是 {module_index}"
                    )


@given(modules=modules_with_circular_dependencies())
@settings(max_examples=50, deadline=None)
def test_property_15_circular_graph_empty_order(modules):
    """
    属性 15 扩展：循环依赖返回空顺序
    
    Feature: dynamic-module-loader
    Property 15: 循环依赖检测正确性（空顺序）
    
    对于任意有环的依赖图，拓扑排序应该返回空列表
    """
    order = get_dependency_order(modules)
    
    # 有循环依赖时，应该返回空列表
    assert len(order) == 0, f"有循环依赖时，拓扑排序应该返回空列表"


# ============================================================
# 属性 14 & 15 综合测试
# ============================================================

@given(modules=modules_with_dependencies(allow_circular=False))
@settings(max_examples=50, deadline=None)
def test_property_14_15_integration(modules):
    """
    属性 14 & 15 综合：依赖校验与循环检测的一致性
    
    Feature: dynamic-module-loader
    Property 14 & 15: 依赖校验与循环检测的一致性
    
    对于任意模块列表：
    1. 如果没有循环依赖，且所有依赖都满足，所有模块都应该通过校验
    2. 如果有循环依赖，循环中的模块应该被拒绝
    """
    circular = detect_circular_dependencies(modules)
    valid, invalid = validate_dependencies(modules)
    
    # 如果没有循环依赖
    if len(circular) == 0:
        # 检查是否所有依赖都满足
        module_names = {m['name'] for m in modules}
        all_deps_satisfied = True
        
        for module in modules:
            dependencies = module.get('dependencies', [])
            if any(dep not in module_names for dep in dependencies):
                all_deps_satisfied = False
                break
        
        # 如果所有依赖都满足，所有模块都应该通过校验
        if all_deps_satisfied:
            assert len(valid) == len(modules), f"无循环且依赖满足时，所有模块应该通过校验"
            assert len(invalid) == 0, f"不应该有失败的模块"
    
    # 如果有循环依赖
    else:
        # 循环中的模块应该被拒绝
        invalid_names = {item['module']['name'] for item in invalid}
        for module_name in circular:
            assert module_name in invalid_names, f"循环依赖模块 {module_name} 应该被拒绝"


# ============================================================
# 运行测试
# ============================================================

if __name__ == "__main__":
    import pytest
    
    print("=" * 60)
    print("运行依赖校验器属性测试")
    print("=" * 60)
    print()
    
    # 运行 pytest
    pytest.main([__file__, "-v", "--tb=short"])
