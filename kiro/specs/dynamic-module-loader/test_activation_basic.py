"""
激活状态计算器基础功能测试脚本

用于快速验证 activation_calculator.py 的核心功能
"""

import sys
sys.path.insert(0, 'src')

from activation_calculator import calculate_activation, evaluate_condition
from path_matcher import match_pattern


def test_global_switch():
    """测试全局开关过滤"""
    print("=" * 60)
    print("测试 1: 全局开关过滤")
    print("=" * 60)
    
    # 测试 1.1: 全局开关开启 + always 条件
    result = calculate_activation(True, {'always': True}, {})
    print(f"✓ 全局开关=True, 条件=always → {result} (预期: True)")
    assert result == True
    
    # 测试 1.2: 全局开关关闭 + always 条件
    result = calculate_activation(False, {'always': True}, {})
    print(f"✓ 全局开关=False, 条件=always → {result} (预期: False)")
    assert result == False
    
    # 测试 1.3: 全局开关开启 + 空条件（默认 always）
    result = calculate_activation(True, {}, {})
    print(f"✓ 全局开关=True, 条件=空 → {result} (预期: True)")
    assert result == True
    
    print("✅ 全局开关过滤测试通过\n")


def test_directory_match():
    """测试目录匹配条件"""
    print("=" * 60)
    print("测试 2: 目录匹配条件")
    print("=" * 60)
    
    context = {'current_directory': '.kiro/steering/main.md'}
    
    # 测试 2.1: 匹配成功
    result = evaluate_condition({'directory_match': ['.kiro/steering/*']}, context)
    print(f"✓ 目录='.kiro/steering/main.md', 模式='.kiro/steering/*' → {result} (预期: True)")
    assert result == True
    
    # 测试 2.2: 匹配失败
    result = evaluate_condition({'directory_match': ['.kiro/modules/*']}, context)
    print(f"✓ 目录='.kiro/steering/main.md', 模式='.kiro/modules/*' → {result} (预期: False)")
    assert result == False
    
    # 测试 2.3: 多个模式（任一匹配）
    result = evaluate_condition({
        'directory_match': ['.kiro/modules/*', '.kiro/steering/*']
    }, context)
    print(f"✓ 目录='.kiro/steering/main.md', 模式=['modules/*', 'steering/*'] → {result} (预期: True)")
    assert result == True
    
    print("✅ 目录匹配测试通过\n")


def test_file_type_match():
    """测试文件类型匹配条件"""
    print("=" * 60)
    print("测试 3: 文件类型匹配条件")
    print("=" * 60)
    
    context = {'current_file_type': '.md'}
    
    # 测试 3.1: 匹配成功
    result = evaluate_condition({'file_type_match': ['.md']}, context)
    print(f"✓ 文件类型='.md', 模式=['.md'] → {result} (预期: True)")
    assert result == True
    
    # 测试 3.2: 匹配失败
    result = evaluate_condition({'file_type_match': ['.yaml']}, context)
    print(f"✓ 文件类型='.md', 模式=['.yaml'] → {result} (预期: False)")
    assert result == False
    
    # 测试 3.3: 多个模式（任一匹配）
    result = evaluate_condition({'file_type_match': ['.md', '.yaml', '.json']}, context)
    print(f"✓ 文件类型='.md', 模式=['.md', '.yaml', '.json'] → {result} (预期: True)")
    assert result == True
    
    print("✅ 文件类型匹配测试通过\n")


def test_and_logic():
    """测试 AND 逻辑组合"""
    print("=" * 60)
    print("测试 4: AND 逻辑组合")
    print("=" * 60)
    
    context = {
        'current_directory': '.kiro/steering/main.md',
        'current_file_type': '.md'
    }
    
    # 测试 4.1: 所有条件满足
    result = evaluate_condition({
        'and': [
            {'directory_match': ['.kiro/steering/*']},
            {'file_type_match': ['.md']}
        ]
    }, context)
    print(f"✓ AND [目录匹配, 文件类型匹配] → {result} (预期: True)")
    assert result == True
    
    # 测试 4.2: 部分条件不满足
    result = evaluate_condition({
        'and': [
            {'directory_match': ['.kiro/steering/*']},
            {'file_type_match': ['.yaml']}
        ]
    }, context)
    print(f"✓ AND [目录匹配, 文件类型不匹配] → {result} (预期: False)")
    assert result == False
    
    print("✅ AND 逻辑测试通过\n")


def test_or_logic():
    """测试 OR 逻辑组合"""
    print("=" * 60)
    print("测试 5: OR 逻辑组合")
    print("=" * 60)
    
    context = {
        'current_directory': '.kiro/steering/main.md',
        'current_file_type': '.md'
    }
    
    # 测试 5.1: 所有条件满足
    result = evaluate_condition({
        'or': [
            {'directory_match': ['.kiro/steering/*']},
            {'file_type_match': ['.yaml']}
        ]
    }, context)
    print(f"✓ OR [目录匹配, 文件类型不匹配] → {result} (预期: True)")
    assert result == True
    
    # 测试 5.2: 任一条件满足
    result = evaluate_condition({
        'or': [
            {'directory_match': ['.kiro/modules/*']},
            {'file_type_match': ['.md']}
        ]
    }, context)
    print(f"✓ OR [目录不匹配, 文件类型匹配] → {result} (预期: True)")
    assert result == True
    
    # 测试 5.3: 所有条件不满足
    result = evaluate_condition({
        'or': [
            {'directory_match': ['.kiro/modules/*']},
            {'file_type_match': ['.yaml']}
        ]
    }, context)
    print(f"✓ OR [目录不匹配, 文件类型不匹配] → {result} (预期: False)")
    assert result == False
    
    print("✅ OR 逻辑测试通过\n")


def test_nested_logic():
    """测试嵌套逻辑组合"""
    print("=" * 60)
    print("测试 6: 嵌套逻辑组合")
    print("=" * 60)
    
    context = {
        'current_directory': '.kiro/steering/main.md',
        'current_file_type': '.md'
    }
    
    # 测试 6.1: OR 包含 AND
    result = evaluate_condition({
        'or': [
            {
                'and': [
                    {'directory_match': ['.kiro/steering/*']},
                    {'file_type_match': ['.md']}
                ]
            },
            {'directory_match': ['doc/project/*']}
        ]
    }, context)
    print(f"✓ OR [AND[目录匹配, 文件类型匹配], 目录匹配2] → {result} (预期: True)")
    assert result == True
    
    print("✅ 嵌套逻辑测试通过\n")


def test_pattern_matching():
    """测试路径模式匹配"""
    print("=" * 60)
    print("测试 7: 路径模式匹配")
    print("=" * 60)
    
    # 测试 7.1: 单层通配符
    result = match_pattern('.kiro/steering', '.kiro/*')
    print(f"✓ 路径='.kiro/steering', 模式='.kiro/*' → {result} (预期: True)")
    assert result == True
    
    # 测试 7.2: 多层通配符
    result = match_pattern('.kiro/modules/workflow/v1.0', '.kiro/modules/*')
    print(f"✓ 路径='.kiro/modules/workflow/v1.0', 模式='.kiro/modules/*' → {result} (预期: True)")
    assert result == True
    
    # 测试 7.3: 不匹配
    result = match_pattern('src/main.py', '.kiro/*')
    print(f"✓ 路径='src/main.py', 模式='.kiro/*' → {result} (预期: False)")
    assert result == False
    
    print("✅ 路径模式匹配测试通过\n")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("激活状态计算器 - 基础功能测试")
    print("=" * 60 + "\n")
    
    try:
        test_global_switch()
        test_directory_match()
        test_file_type_match()
        test_and_logic()
        test_or_logic()
        test_nested_logic()
        test_pattern_matching()
        
        print("=" * 60)
        print("🎉 所有测试通过！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
