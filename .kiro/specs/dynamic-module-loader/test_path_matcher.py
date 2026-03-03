"""
路径匹配器专项测试脚本

用于验证 path_matcher.py 的所有功能
"""

import sys
sys.path.insert(0, 'src')

from path_matcher import match_directory, match_file_type, match_pattern, normalize_path


def test_match_directory():
    """测试目录匹配功能"""
    print("=" * 60)
    print("测试 1: match_directory() - 目录路径匹配")
    print("=" * 60)
    
    # 测试 1.1: 单个模式匹配成功
    result = match_directory('.kiro/steering/main.md', '.kiro/steering/*')
    print(f"✓ 路径='.kiro/steering/main.md', 模式='.kiro/steering/*' → {result} (预期: True)")
    assert result == True
    
    # 测试 1.2: 单个模式匹配失败
    result = match_directory('.kiro/steering/main.md', '.kiro/modules/*')
    print(f"✓ 路径='.kiro/steering/main.md', 模式='.kiro/modules/*' → {result} (预期: False)")
    assert result == False
    
    # 测试 1.3: 多个模式（列表）- 任一匹配
    result = match_directory('.kiro/steering/main.md', ['.kiro/modules/*', '.kiro/steering/*'])
    print(f"✓ 路径='.kiro/steering/main.md', 模式=['modules/*', 'steering/*'] → {result} (预期: True)")
    assert result == True
    
    # 测试 1.4: 多个模式（列表）- 全不匹配
    result = match_directory('.kiro/steering/main.md', ['.kiro/modules/*', 'doc/project/*'])
    print(f"✓ 路径='.kiro/steering/main.md', 模式=['modules/*', 'doc/*'] → {result} (预期: False)")
    assert result == False
    
    # 测试 1.5: 通配符匹配多层路径
    result = match_directory('.kiro/modules/workflow/v1.0/steering/workflow_selector.md', '.kiro/modules/*')
    print(f"✓ 路径='.kiro/modules/workflow/v1.0/...', 模式='.kiro/modules/*' → {result} (预期: True)")
    assert result == True
    
    # 测试 1.6: 精确匹配（无通配符）
    result = match_directory('.kiro/steering', '.kiro/steering')
    print(f"✓ 路径='.kiro/steering', 模式='.kiro/steering' → {result} (预期: True)")
    assert result == True
    
    print("✅ match_directory() 测试通过\n")


def test_match_file_type():
    """测试文件类型匹配功能"""
    print("=" * 60)
    print("测试 2: match_file_type() - 文件类型匹配")
    print("=" * 60)
    
    # 测试 2.1: 单个扩展名匹配成功
    result = match_file_type('.md', '.md')
    print(f"✓ 文件='.md', 扩展名='.md' → {result} (预期: True)")
    assert result == True
    
    # 测试 2.2: 单个扩展名匹配失败
    result = match_file_type('.md', '.yaml')
    print(f"✓ 文件='.md', 扩展名='.yaml' → {result} (预期: False)")
    assert result == False
    
    # 测试 2.3: 多个扩展名（列表）- 任一匹配
    result = match_file_type('.md', ['.md', '.yaml', '.json'])
    print(f"✓ 文件='.md', 扩展名=['.md', '.yaml', '.json'] → {result} (预期: True)")
    assert result == True
    
    # 测试 2.4: 多个扩展名（列表）- 全不匹配
    result = match_file_type('.md', ['.yaml', '.json', '.txt'])
    print(f"✓ 文件='.md', 扩展名=['.yaml', '.json', '.txt'] → {result} (预期: False)")
    assert result == False
    
    # 测试 2.5: 完整文件路径匹配
    result = match_file_type('config.yaml', '.yaml')
    print(f"✓ 文件='config.yaml', 扩展名='.yaml' → {result} (预期: True)")
    assert result == True
    
    # 测试 2.6: 完整文件路径匹配（多层）
    result = match_file_type('.kiro/steering/main.md', '.md')
    print(f"✓ 文件='.kiro/steering/main.md', 扩展名='.md' → {result} (预期: True)")
    assert result == True
    
    # 测试 2.7: 完整文件路径不匹配
    result = match_file_type('.kiro/steering/main.md', '.yaml')
    print(f"✓ 文件='.kiro/steering/main.md', 扩展名='.yaml' → {result} (预期: False)")
    assert result == False
    
    print("✅ match_file_type() 测试通过\n")


def test_match_pattern():
    """测试通用模式匹配功能"""
    print("=" * 60)
    print("测试 3: match_pattern() - 通用模式匹配")
    print("=" * 60)
    
    # 测试 3.1: 单层通配符
    result = match_pattern('.kiro/steering', '.kiro/*')
    print(f"✓ 路径='.kiro/steering', 模式='.kiro/*' → {result} (预期: True)")
    assert result == True
    
    # 测试 3.2: 多层通配符
    result = match_pattern('.kiro/modules/workflow/v1.0', '.kiro/modules/*')
    print(f"✓ 路径='.kiro/modules/workflow/v1.0', 模式='.kiro/modules/*' → {result} (预期: True)")
    assert result == True
    
    # 测试 3.3: 不匹配
    result = match_pattern('src/main.py', '.kiro/*')
    print(f"✓ 路径='src/main.py', 模式='.kiro/*' → {result} (预期: False)")
    assert result == False
    
    # 测试 3.4: 精确匹配
    result = match_pattern('.kiro/config.yaml', '.kiro/config.yaml')
    print(f"✓ 路径='.kiro/config.yaml', 模式='.kiro/config.yaml' → {result} (预期: True)")
    assert result == True
    
    # 测试 3.5: 通配符在中间
    result = match_pattern('.kiro/modules/workflow/v1.0', '.kiro/*/workflow/*')
    print(f"✓ 路径='.kiro/modules/workflow/v1.0', 模式='.kiro/*/workflow/*' → {result} (预期: True)")
    assert result == True
    
    # 测试 3.6: 通配符在开头
    result = match_pattern('.kiro/steering/main.md', '*/main.md')
    print(f"✓ 路径='.kiro/steering/main.md', 模式='*/main.md' → {result} (预期: True)")
    assert result == True
    
    print("✅ match_pattern() 测试通过\n")


def test_normalize_path():
    """测试路径规范化功能"""
    print("=" * 60)
    print("测试 4: normalize_path() - 路径规范化")
    print("=" * 60)
    
    # 测试 4.1: Windows 路径转换
    result = normalize_path('.kiro\\steering\\main.md')
    print(f"✓ 路径='.kiro\\steering\\main.md' → '{result}' (预期: '.kiro/steering/main.md')")
    assert result == '.kiro/steering/main.md'
    
    # 测试 4.2: Unix 路径保持不变
    result = normalize_path('.kiro/steering/main.md')
    print(f"✓ 路径='.kiro/steering/main.md' → '{result}' (预期: '.kiro/steering/main.md')")
    assert result == '.kiro/steering/main.md'
    
    # 测试 4.3: 混合路径分隔符
    result = normalize_path('.kiro\\modules/workflow\\v1.0')
    print(f"✓ 路径='.kiro\\modules/workflow\\v1.0' → '{result}' (预期: '.kiro/modules/workflow/v1.0')")
    assert result == '.kiro/modules/workflow/v1.0'
    
    # 测试 4.4: 空路径
    result = normalize_path('')
    print(f"✓ 路径='' → '{result}' (预期: '')")
    assert result == ''
    
    print("✅ normalize_path() 测试通过\n")


def test_edge_cases():
    """测试边界情况"""
    print("=" * 60)
    print("测试 5: 边界情况测试")
    print("=" * 60)
    
    # 测试 5.1: 空路径匹配
    result = match_directory('', '.kiro/*')
    print(f"✓ 空路径匹配 → {result} (预期: False)")
    assert result == False
    
    # 测试 5.2: 空模式列表
    result = match_directory('.kiro/steering', [])
    print(f"✓ 空模式列表 → {result} (预期: False)")
    assert result == False
    
    # 测试 5.3: 空扩展名匹配
    result = match_file_type('', '.md')
    print(f"✓ 空文件名匹配 → {result} (预期: False)")
    assert result == False
    
    # 测试 5.4: 空扩展名列表
    result = match_file_type('.md', [])
    print(f"✓ 空扩展名列表 → {result} (预期: False)")
    assert result == False
    
    # 测试 5.5: 特殊字符路径
    result = match_pattern('.kiro/test-file_v1.0.md', '.kiro/*')
    print(f"✓ 特殊字符路径匹配 → {result} (预期: True)")
    assert result == True
    
    print("✅ 边界情况测试通过\n")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("路径匹配器 - 专项功能测试")
    print("=" * 60 + "\n")
    
    try:
        test_match_directory()
        test_match_file_type()
        test_match_pattern()
        test_normalize_path()
        test_edge_cases()
        
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
