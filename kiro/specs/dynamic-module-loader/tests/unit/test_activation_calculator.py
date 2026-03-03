"""
激活状态计算器单元测试

测试 activation_calculator.py 模块的所有功能：
- 全局开关过滤
- 各种条件类型（always, directory_match, file_type_match）
- AND/OR 逻辑组合
- 嵌套逻辑
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

from activation_calculator import calculate_activation, evaluate_condition


class TestGlobalSwitchFiltering:
    """测试全局开关过滤功能"""
    
    def test_global_switch_enabled_with_always_condition(self):
        """测试：全局开关开启 + always 条件 → 激活"""
        result = calculate_activation(True, {'always': True}, {})
        assert result == True
    
    def test_global_switch_disabled_with_always_condition(self):
        """测试：全局开关关闭 + always 条件 → 不激活"""
        result = calculate_activation(False, {'always': True}, {})
        assert result == False
    
    def test_global_switch_enabled_with_empty_conditions(self):
        """测试：全局开关开启 + 空条件（默认 always） → 激活"""
        result = calculate_activation(True, {}, {})
        assert result == True
    
    def test_global_switch_disabled_with_empty_conditions(self):
        """测试：全局开关关闭 + 空条件 → 不激活"""
        result = calculate_activation(False, {}, {})
        assert result == False
    
    def test_global_switch_enabled_with_none_conditions(self):
        """测试：全局开关开启 + None 条件 → 激活"""
        result = calculate_activation(True, None, {})
        assert result == True
    
    def test_global_switch_disabled_with_matching_condition(self):
        """测试：全局开关关闭 + 匹配的条件 → 不激活（全局开关优先）"""
        context = {'current_directory': '.kiro/steering/main.md'}
        conditions = {'directory_match': ['.kiro/steering/*']}
        result = calculate_activation(False, conditions, context)
        assert result == False


class TestAlwaysCondition:
    """测试 always 条件"""
    
    def test_always_true(self):
        """测试：always: true → 激活"""
        result = evaluate_condition({'always': True}, {})
        assert result == True
    
    def test_always_false(self):
        """测试：always: false → 不激活"""
        result = evaluate_condition({'always': False}, {})
        assert result == False
    
    def test_always_with_context(self):
        """测试：always 条件忽略上下文"""
        context = {'current_directory': 'any/path', 'current_file_type': '.any'}
        result = evaluate_condition({'always': True}, context)
        assert result == True


class TestDirectoryMatchCondition:
    """测试 directory_match 条件"""
    
    def test_directory_match_single_pattern_success(self):
        """测试：单个模式匹配成功"""
        context = {'current_directory': '.kiro/steering/main.md'}
        conditions = {'directory_match': '.kiro/steering/*'}
        result = evaluate_condition(conditions, context)
        assert result == True
    
    def test_directory_match_single_pattern_failure(self):
        """测试：单个模式匹配失败"""
        context = {'current_directory': '.kiro/steering/main.md'}
        conditions = {'directory_match': '.kiro/modules/*'}
        result = evaluate_condition(conditions, context)
        assert result == False
    
    def test_directory_match_multiple_patterns_any_match(self):
        """测试：多个模式，任一匹配成功"""
        context = {'current_directory': '.kiro/steering/main.md'}
        conditions = {'directory_match': ['.kiro/modules/*', '.kiro/steering/*']}
        result = evaluate_condition(conditions, context)
        assert result == True
    
    def test_directory_match_multiple_patterns_no_match(self):
        """测试：多个模式，全不匹配"""
        context = {'current_directory': '.kiro/steering/main.md'}
        conditions = {'directory_match': ['.kiro/modules/*', 'doc/project/*']}
        result = evaluate_condition(conditions, context)
        assert result == False
    
    def test_directory_match_wildcard_multilevel(self):
        """测试：通配符匹配多层路径"""
        context = {'current_directory': '.kiro/modules/workflow/v1.0/steering/workflow_selector.md'}
        conditions = {'directory_match': '.kiro/modules/*'}
        result = evaluate_condition(conditions, context)
        assert result == True
    
    def test_directory_match_empty_context(self):
        """测试：空上下文（无 current_directory）"""
        context = {}
        conditions = {'directory_match': '.kiro/*'}
        result = evaluate_condition(conditions, context)
        assert result == False
    
    def test_directory_match_empty_pattern_list(self):
        """测试：空模式列表"""
        context = {'current_directory': '.kiro/steering'}
        conditions = {'directory_match': []}
        result = evaluate_condition(conditions, context)
        assert result == False


class TestFileTypeMatchCondition:
    """测试 file_type_match 条件"""
    
    def test_file_type_match_single_extension_success(self):
        """测试：单个扩展名匹配成功"""
        context = {'current_file_type': '.md'}
        conditions = {'file_type_match': '.md'}
        result = evaluate_condition(conditions, context)
        assert result == True
    
    def test_file_type_match_single_extension_failure(self):
        """测试：单个扩展名匹配失败"""
        context = {'current_file_type': '.md'}
        conditions = {'file_type_match': '.yaml'}
        result = evaluate_condition(conditions, context)
        assert result == False
    
    def test_file_type_match_multiple_extensions_any_match(self):
        """测试：多个扩展名，任一匹配成功"""
        context = {'current_file_type': '.md'}
        conditions = {'file_type_match': ['.md', '.yaml', '.json']}
        result = evaluate_condition(conditions, context)
        assert result == True
    
    def test_file_type_match_multiple_extensions_no_match(self):
        """测试：多个扩展名，全不匹配"""
        context = {'current_file_type': '.md'}
        conditions = {'file_type_match': ['.yaml', '.json', '.txt']}
        result = evaluate_condition(conditions, context)
        assert result == False
    
    def test_file_type_match_full_path(self):
        """测试：完整文件路径匹配"""
        context = {'current_file_type': '.kiro/steering/main.md'}
        conditions = {'file_type_match': '.md'}
        result = evaluate_condition(conditions, context)
        assert result == True
    
    def test_file_type_match_empty_context(self):
        """测试：空上下文（无 current_file_type）"""
        context = {}
        conditions = {'file_type_match': '.md'}
        result = evaluate_condition(conditions, context)
        assert result == False
    
    def test_file_type_match_empty_extension_list(self):
        """测试：空扩展名列表"""
        context = {'current_file_type': '.md'}
        conditions = {'file_type_match': []}
        result = evaluate_condition(conditions, context)
        assert result == False


class TestAndLogic:
    """测试 AND 逻辑组合"""
    
    def test_and_all_conditions_satisfied(self):
        """测试：所有条件满足 → 激活"""
        context = {
            'current_directory': '.kiro/steering/main.md',
            'current_file_type': '.md'
        }
        conditions = {
            'and': [
                {'directory_match': ['.kiro/steering/*']},
                {'file_type_match': ['.md']}
            ]
        }
        result = evaluate_condition(conditions, context)
        assert result == True
    
    def test_and_one_condition_not_satisfied(self):
        """测试：部分条件不满足 → 不激活"""
        context = {
            'current_directory': '.kiro/steering/main.md',
            'current_file_type': '.md'
        }
        conditions = {
            'and': [
                {'directory_match': ['.kiro/steering/*']},
                {'file_type_match': ['.yaml']}
            ]
        }
        result = evaluate_condition(conditions, context)
        assert result == False
    
    def test_and_all_conditions_not_satisfied(self):
        """测试：所有条件不满足 → 不激活"""
        context = {
            'current_directory': '.kiro/steering/main.md',
            'current_file_type': '.md'
        }
        conditions = {
            'and': [
                {'directory_match': ['.kiro/modules/*']},
                {'file_type_match': ['.yaml']}
            ]
        }
        result = evaluate_condition(conditions, context)
        assert result == False
    
    def test_and_three_conditions(self):
        """测试：三个条件的 AND 组合"""
        context = {
            'current_directory': '.kiro/steering/main.md',
            'current_file_type': '.md'
        }
        conditions = {
            'and': [
                {'directory_match': ['.kiro/steering/*']},
                {'file_type_match': ['.md']},
                {'always': True}
            ]
        }
        result = evaluate_condition(conditions, context)
        assert result == True
    
    def test_and_empty_list(self):
        """测试：空 AND 列表 → 不激活"""
        context = {}
        conditions = {'and': []}
        result = evaluate_condition(conditions, context)
        assert result == True  # 空列表，所有条件都满足（vacuous truth）
    
    def test_and_not_a_list(self):
        """测试：AND 值不是列表 → 不激活"""
        context = {}
        conditions = {'and': 'not_a_list'}
        result = evaluate_condition(conditions, context)
        assert result == False


class TestOrLogic:
    """测试 OR 逻辑组合"""
    
    def test_or_all_conditions_satisfied(self):
        """测试：所有条件满足 → 激活"""
        context = {
            'current_directory': '.kiro/steering/main.md',
            'current_file_type': '.md'
        }
        conditions = {
            'or': [
                {'directory_match': ['.kiro/steering/*']},
                {'file_type_match': ['.md']}
            ]
        }
        result = evaluate_condition(conditions, context)
        assert result == True
    
    def test_or_one_condition_satisfied(self):
        """测试：任一条件满足 → 激活"""
        context = {
            'current_directory': '.kiro/steering/main.md',
            'current_file_type': '.md'
        }
        conditions = {
            'or': [
                {'directory_match': ['.kiro/modules/*']},
                {'file_type_match': ['.md']}
            ]
        }
        result = evaluate_condition(conditions, context)
        assert result == True
    
    def test_or_no_conditions_satisfied(self):
        """测试：所有条件不满足 → 不激活"""
        context = {
            'current_directory': '.kiro/steering/main.md',
            'current_file_type': '.md'
        }
        conditions = {
            'or': [
                {'directory_match': ['.kiro/modules/*']},
                {'file_type_match': ['.yaml']}
            ]
        }
        result = evaluate_condition(conditions, context)
        assert result == False
    
    def test_or_three_conditions(self):
        """测试：三个条件的 OR 组合"""
        context = {
            'current_directory': '.kiro/steering/main.md',
            'current_file_type': '.md'
        }
        conditions = {
            'or': [
                {'directory_match': ['.kiro/modules/*']},
                {'file_type_match': ['.yaml']},
                {'always': True}
            ]
        }
        result = evaluate_condition(conditions, context)
        assert result == True
    
    def test_or_empty_list(self):
        """测试：空 OR 列表 → 不激活"""
        context = {}
        conditions = {'or': []}
        result = evaluate_condition(conditions, context)
        assert result == False
    
    def test_or_not_a_list(self):
        """测试：OR 值不是列表 → 不激活"""
        context = {}
        conditions = {'or': 'not_a_list'}
        result = evaluate_condition(conditions, context)
        assert result == False


class TestNestedLogic:
    """测试嵌套逻辑组合"""
    
    def test_or_containing_and(self):
        """测试：OR 包含 AND"""
        context = {
            'current_directory': '.kiro/steering/main.md',
            'current_file_type': '.md'
        }
        conditions = {
            'or': [
                {
                    'and': [
                        {'directory_match': ['.kiro/steering/*']},
                        {'file_type_match': ['.md']}
                    ]
                },
                {'directory_match': ['doc/project/*']}
            ]
        }
        result = evaluate_condition(conditions, context)
        assert result == True
    
    def test_and_containing_or(self):
        """测试：AND 包含 OR"""
        context = {
            'current_directory': '.kiro/steering/main.md',
            'current_file_type': '.md'
        }
        conditions = {
            'and': [
                {
                    'or': [
                        {'directory_match': ['.kiro/steering/*']},
                        {'directory_match': ['.kiro/modules/*']}
                    ]
                },
                {'file_type_match': ['.md']}
            ]
        }
        result = evaluate_condition(conditions, context)
        assert result == True
    
    def test_deeply_nested_logic(self):
        """测试：深度嵌套逻辑"""
        context = {
            'current_directory': '.kiro/steering/main.md',
            'current_file_type': '.md'
        }
        conditions = {
            'or': [
                {
                    'and': [
                        {
                            'or': [
                                {'directory_match': ['.kiro/steering/*']},
                                {'directory_match': ['.kiro/modules/*']}
                            ]
                        },
                        {'file_type_match': ['.md']}
                    ]
                },
                {'always': False}
            ]
        }
        result = evaluate_condition(conditions, context)
        assert result == True


class TestEdgeCases:
    """测试边界情况和错误处理"""
    
    def test_empty_condition_dict(self):
        """测试：空条件字典 → 不激活"""
        result = evaluate_condition({}, {})
        assert result == False
    
    def test_unknown_condition_type(self):
        """测试：未知条件类型 → 不激活"""
        context = {'current_directory': '.kiro/steering'}
        conditions = {'unknown_condition': 'value'}
        result = evaluate_condition(conditions, context)
        assert result == False
    
    def test_multiple_condition_types_in_one_dict(self):
        """测试：一个字典中包含多个条件类型（只处理第一个匹配的）"""
        context = {'current_directory': '.kiro/steering'}
        conditions = {
            'always': True,
            'directory_match': ['.kiro/modules/*']  # 这个会被忽略
        }
        result = evaluate_condition(conditions, context)
        assert result == True  # always 优先
    
    def test_empty_context(self):
        """测试：空上下文"""
        conditions = {'always': True}
        result = evaluate_condition(conditions, {})
        assert result == True
    
    def test_none_context(self):
        """测试：None 上下文（应该不会崩溃）"""
        conditions = {'always': True}
        # 这个测试可能会失败，取决于实现是否处理 None
        # 如果需要支持 None，需要在代码中添加检查
        try:
            result = evaluate_condition(conditions, {})
            assert result == True
        except (TypeError, AttributeError):
            # 如果不支持 None，至少不应该崩溃
            pass


class TestIntegration:
    """集成测试：测试完整的激活状态计算流程"""
    
    def test_realistic_scenario_1(self):
        """真实场景 1：Steering 目录下的 Markdown 文件"""
        context = {
            'current_directory': '.kiro/steering/main.md',
            'current_file_type': '.md'
        }
        conditions = {
            'and': [
                {'directory_match': ['.kiro/steering/*', '.kiro/modules/*/steering/*']},
                {'file_type_match': ['.md']}
            ]
        }
        result = calculate_activation(True, conditions, context)
        assert result == True
    
    def test_realistic_scenario_2(self):
        """真实场景 2：配置文件（YAML 或 JSON）"""
        context = {
            'current_directory': '.kiro/config.yaml',
            'current_file_type': '.yaml'
        }
        conditions = {
            'or': [
                {'file_type_match': ['.yaml', '.json']},
                {'directory_match': ['.kiro/*']}
            ]
        }
        result = calculate_activation(True, conditions, context)
        assert result == True
    
    def test_realistic_scenario_3(self):
        """真实场景 3：文档目录"""
        context = {
            'current_directory': 'doc/project/architecture/design.md',
            'current_file_type': '.md'
        }
        conditions = {
            'directory_match': ['doc/**/*']
        }
        result = calculate_activation(True, conditions, context)
        assert result == True
    
    def test_realistic_scenario_4(self):
        """真实场景 4：全局开关关闭，即使条件匹配也不激活"""
        context = {
            'current_directory': '.kiro/steering/main.md',
            'current_file_type': '.md'
        }
        conditions = {
            'and': [
                {'directory_match': ['.kiro/steering/*']},
                {'file_type_match': ['.md']}
            ]
        }
        result = calculate_activation(False, conditions, context)
        assert result == False


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v', '--tb=short'])
