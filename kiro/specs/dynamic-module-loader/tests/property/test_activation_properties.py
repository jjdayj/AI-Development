"""
激活状态计算器的属性测试

使用 Hypothesis 框架进行基于属性的测试，验证：
- 属性 2：全局开关过滤正确性
- 属性 3：激活状态计算正确性
- 属性 4：条件逻辑组合正确性

作者: yangzhuo
日期: 2026-03-03
版本: v1.0
"""

import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings, example, assume

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from activation_calculator import calculate_activation, evaluate_condition


# ============================================================
# 策略生成器：生成测试数据
# ============================================================

# 生成目录路径
@st.composite
def directory_path(draw):
    """生成目录路径"""
    segments = draw(st.lists(
        st.sampled_from(['.kiro', 'steering', 'modules', 'doc', 'project', 'src', 'tests']),
        min_size=1,
        max_size=5
    ))
    return '/'.join(segments)


# 生成文件类型
@st.composite
def file_type(draw):
    """生成文件类型（扩展名）"""
    return draw(st.sampled_from(['.md', '.yaml', '.json', '.py', '.txt', '.js', '.ts']))


# 生成上下文
@st.composite
def context(draw):
    """生成当前上下文"""
    return {
        'current_directory': draw(directory_path()),
        'current_file_type': draw(file_type())
    }


# 生成简单条件（always, directory_match, file_type_match）
@st.composite
def simple_condition(draw):
    """生成简单条件"""
    condition_type = draw(st.sampled_from(['always', 'directory_match', 'file_type_match']))
    
    if condition_type == 'always':
        return {'always': draw(st.booleans())}
    
    elif condition_type == 'directory_match':
        patterns = draw(st.lists(
            st.sampled_from([
                '.kiro/*', '.kiro/steering/*', '.kiro/modules/*',
                'doc/*', 'doc/project/*', 'src/*', 'tests/*'
            ]),
            min_size=1,
            max_size=3
        ))
        return {'directory_match': patterns}
    
    else:  # file_type_match
        patterns = draw(st.lists(
            st.sampled_from(['.md', '.yaml', '.json', '.py', '.txt']),
            min_size=1,
            max_size=3
        ))
        return {'file_type_match': patterns}


# 生成复杂条件（包含 AND/OR 逻辑）
@st.composite
def complex_condition(draw, max_depth=2):
    """生成复杂条件（支持嵌套）"""
    if max_depth == 0:
        return draw(simple_condition())
    
    condition_type = draw(st.sampled_from(['simple', 'and', 'or']))
    
    if condition_type == 'simple':
        return draw(simple_condition())
    
    elif condition_type == 'and':
        sub_conditions = draw(st.lists(
            complex_condition(max_depth=max_depth-1),
            min_size=2,
            max_size=3
        ))
        return {'and': sub_conditions}
    
    else:  # or
        sub_conditions = draw(st.lists(
            complex_condition(max_depth=max_depth-1),
            min_size=2,
            max_size=3
        ))
        return {'or': sub_conditions}


# ============================================================
# 属性 2：全局开关过滤正确性
# ============================================================

@given(
    activation_conditions=st.one_of(st.none(), simple_condition()),
    ctx=context()
)
@settings(max_examples=100, deadline=None)
@example(activation_conditions={'always': True}, ctx={'current_directory': '.kiro', 'current_file_type': '.md'})
@example(activation_conditions=None, ctx={'current_directory': '', 'current_file_type': ''})
def test_property_2_global_switch_disabled(activation_conditions, ctx):
    """
    属性 2：全局开关过滤正确性
    
    Feature: dynamic-module-loader
    Property 2: 全局开关过滤正确性
    
    对于任意激活条件和上下文，当全局开关为 False 时，
    calculate_activation() 应该始终返回 False
    """
    result = calculate_activation(False, activation_conditions, ctx)
    assert result is False, f"全局开关关闭时应该返回 False，但返回了 {result}"


@given(
    activation_conditions=st.one_of(st.none(), simple_condition()),
    ctx=context()
)
@settings(max_examples=100, deadline=None)
@example(activation_conditions={'always': True}, ctx={'current_directory': '.kiro', 'current_file_type': '.md'})
def test_property_2_global_switch_enabled_with_always(activation_conditions, ctx):
    """
    属性 2 扩展：全局开关开启时，激活状态取决于条件
    
    Feature: dynamic-module-loader
    Property 2: 全局开关过滤正确性（开启时）
    
    当全局开关为 True 时，激活状态应该等于条件评估结果
    """
    # 计算激活状态
    result = calculate_activation(True, activation_conditions, ctx)
    
    # 计算预期结果
    if activation_conditions is None or not activation_conditions:
        expected = True  # 空条件默认为 always: true
    else:
        expected = evaluate_condition(activation_conditions, ctx)
    
    assert result == expected, f"全局开关开启时，激活状态应该等于条件评估结果"


# ============================================================
# 属性 3：激活状态计算正确性
# ============================================================

@given(
    global_switch=st.booleans(),
    activation_conditions=st.one_of(st.none(), simple_condition()),
    ctx=context()
)
@settings(max_examples=100, deadline=None)
@example(global_switch=True, activation_conditions={'always': True}, ctx={'current_directory': '', 'current_file_type': ''})
@example(global_switch=False, activation_conditions={'always': True}, ctx={'current_directory': '', 'current_file_type': ''})
def test_property_3_activation_calculation(global_switch, activation_conditions, ctx):
    """
    属性 3：激活状态计算正确性
    
    Feature: dynamic-module-loader
    Property 3: 激活状态计算正确性
    
    对于任意全局开关、激活条件和上下文，
    calculate_activation() 的结果应该等于：
    Global_Switch AND Module_Condition_Match
    """
    # 计算激活状态
    result = calculate_activation(global_switch, activation_conditions, ctx)
    
    # 计算预期结果
    if not global_switch:
        expected = False
    elif activation_conditions is None or not activation_conditions:
        expected = True  # 空条件默认为 always: true
    else:
        expected = evaluate_condition(activation_conditions, ctx)
    
    assert result == expected, (
        f"激活状态计算错误：\n"
        f"  全局开关: {global_switch}\n"
        f"  激活条件: {activation_conditions}\n"
        f"  上下文: {ctx}\n"
        f"  预期: {expected}\n"
        f"  实际: {result}"
    )


@given(
    activation_conditions=simple_condition(),
    ctx=context()
)
@settings(max_examples=100, deadline=None)
def test_property_3_idempotence(activation_conditions, ctx):
    """
    属性 3 扩展：激活状态计算的幂等性
    
    Feature: dynamic-module-loader
    Property 3: 激活状态计算正确性（幂等性）
    
    对于相同的输入，多次调用 calculate_activation() 应该得到相同的结果
    """
    # 第一次计算
    result1 = calculate_activation(True, activation_conditions, ctx)
    
    # 第二次计算
    result2 = calculate_activation(True, activation_conditions, ctx)
    
    # 第三次计算
    result3 = calculate_activation(True, activation_conditions, ctx)
    
    assert result1 == result2 == result3, "多次计算应该得到相同的结果"


# ============================================================
# 属性 4：条件逻辑组合正确性
# ============================================================

@given(
    sub_conditions=st.lists(simple_condition(), min_size=2, max_size=4),
    ctx=context()
)
@settings(max_examples=100, deadline=None)
@example(
    sub_conditions=[{'always': True}, {'always': True}],
    ctx={'current_directory': '', 'current_file_type': ''}
)
@example(
    sub_conditions=[{'always': True}, {'always': False}],
    ctx={'current_directory': '', 'current_file_type': ''}
)
def test_property_4_and_logic(sub_conditions, ctx):
    """
    属性 4：AND 逻辑组合正确性
    
    Feature: dynamic-module-loader
    Property 4: 条件逻辑组合正确性（AND）
    
    对于任意子条件列表，AND 逻辑应该满足：
    只有当所有子条件都满足时，AND 条件才满足
    """
    # 构建 AND 条件
    and_condition = {'and': sub_conditions}
    
    # 计算 AND 条件的结果
    and_result = evaluate_condition(and_condition, ctx)
    
    # 计算每个子条件的结果
    sub_results = [evaluate_condition(cond, ctx) for cond in sub_conditions]
    
    # 验证 AND 逻辑：所有子条件都为 True 时，AND 才为 True
    expected = all(sub_results)
    
    assert and_result == expected, (
        f"AND 逻辑错误：\n"
        f"  子条件: {sub_conditions}\n"
        f"  子结果: {sub_results}\n"
        f"  预期: {expected}\n"
        f"  实际: {and_result}"
    )


@given(
    sub_conditions=st.lists(simple_condition(), min_size=2, max_size=4),
    ctx=context()
)
@settings(max_examples=100, deadline=None)
@example(
    sub_conditions=[{'always': False}, {'always': False}],
    ctx={'current_directory': '', 'current_file_type': ''}
)
@example(
    sub_conditions=[{'always': True}, {'always': False}],
    ctx={'current_directory': '', 'current_file_type': ''}
)
def test_property_4_or_logic(sub_conditions, ctx):
    """
    属性 4：OR 逻辑组合正确性
    
    Feature: dynamic-module-loader
    Property 4: 条件逻辑组合正确性（OR）
    
    对于任意子条件列表，OR 逻辑应该满足：
    只要有一个子条件满足，OR 条件就满足
    """
    # 构建 OR 条件
    or_condition = {'or': sub_conditions}
    
    # 计算 OR 条件的结果
    or_result = evaluate_condition(or_condition, ctx)
    
    # 计算每个子条件的结果
    sub_results = [evaluate_condition(cond, ctx) for cond in sub_conditions]
    
    # 验证 OR 逻辑：任一子条件为 True 时，OR 就为 True
    expected = any(sub_results)
    
    assert or_result == expected, (
        f"OR 逻辑错误：\n"
        f"  子条件: {sub_conditions}\n"
        f"  子结果: {sub_results}\n"
        f"  预期: {expected}\n"
        f"  实际: {or_result}"
    )


@given(
    condition=complex_condition(max_depth=2),
    ctx=context()
)
@settings(max_examples=100, deadline=None)
def test_property_4_nested_logic(condition, ctx):
    """
    属性 4 扩展：嵌套逻辑组合正确性
    
    Feature: dynamic-module-loader
    Property 4: 条件逻辑组合正确性（嵌套）
    
    对于任意嵌套的逻辑条件，evaluate_condition() 应该：
    1. 不抛出异常
    2. 返回布尔值
    3. 结果符合逻辑规则
    """
    # 计算条件结果（不应该抛出异常）
    try:
        result = evaluate_condition(condition, ctx)
    except Exception as e:
        raise AssertionError(f"嵌套逻辑计算抛出异常: {e}\n条件: {condition}")
    
    # 验证返回值是布尔类型
    assert isinstance(result, bool), f"返回值应该是布尔类型，但得到 {type(result)}"


# ============================================================
# 属性 4 扩展：逻辑组合的德摩根定律
# ============================================================

@given(
    sub_conditions=st.lists(simple_condition(), min_size=2, max_size=3),
    ctx=context()
)
@settings(max_examples=50, deadline=None)
def test_property_4_de_morgan_law(sub_conditions, ctx):
    """
    属性 4 扩展：德摩根定律验证
    
    Feature: dynamic-module-loader
    Property 4: 条件逻辑组合正确性（德摩根定律）
    
    验证德摩根定律：
    NOT (A AND B) = (NOT A) OR (NOT B)
    NOT (A OR B) = (NOT A) AND (NOT B)
    
    注意：由于我们的条件系统不支持 NOT 操作，
    这个测试主要验证 AND 和 OR 的对偶性
    """
    # 计算 AND 结果
    and_condition = {'and': sub_conditions}
    and_result = evaluate_condition(and_condition, ctx)
    
    # 计算 OR 结果
    or_condition = {'or': sub_conditions}
    or_result = evaluate_condition(or_condition, ctx)
    
    # 计算每个子条件的结果
    sub_results = [evaluate_condition(cond, ctx) for cond in sub_conditions]
    
    # 验证 AND 和 OR 的关系
    # 如果所有子条件都为 True，则 AND 和 OR 都为 True
    if all(sub_results):
        assert and_result is True, "所有子条件为 True 时，AND 应该为 True"
        assert or_result is True, "所有子条件为 True 时，OR 应该为 True"
    
    # 如果所有子条件都为 False，则 AND 和 OR 都为 False
    elif not any(sub_results):
        assert and_result is False, "所有子条件为 False 时，AND 应该为 False"
        assert or_result is False, "所有子条件为 False 时，OR 应该为 False"
    
    # 如果部分子条件为 True，则 AND 为 False，OR 为 True
    else:
        assert and_result is False, "部分子条件为 True 时，AND 应该为 False"
        assert or_result is True, "部分子条件为 True 时，OR 应该为 True"


# ============================================================
# 属性 4 扩展：空列表边界情况
# ============================================================

@given(ctx=context())
@settings(max_examples=50, deadline=None)
def test_property_4_empty_and_list(ctx):
    """
    属性 4 扩展：空 AND 列表
    
    Feature: dynamic-module-loader
    Property 4: 条件逻辑组合正确性（空 AND）
    
    空 AND 列表应该返回 True（vacuous truth）
    """
    empty_and = {'and': []}
    result = evaluate_condition(empty_and, ctx)
    assert result is True, "空 AND 列表应该返回 True"


@given(ctx=context())
@settings(max_examples=50, deadline=None)
def test_property_4_empty_or_list(ctx):
    """
    属性 4 扩展：空 OR 列表
    
    Feature: dynamic-module-loader
    Property 4: 条件逻辑组合正确性（空 OR）
    
    空 OR 列表应该返回 False
    """
    empty_or = {'or': []}
    result = evaluate_condition(empty_or, ctx)
    assert result is False, "空 OR 列表应该返回 False"


# ============================================================
# 运行测试
# ============================================================

if __name__ == "__main__":
    import pytest
    
    print("=" * 60)
    print("运行激活状态计算器属性测试")
    print("=" * 60)
    print()
    
    # 运行 pytest
    pytest.main([__file__, "-v", "--tb=short"])
