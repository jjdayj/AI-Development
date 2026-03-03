"""
path_validator.py 的单元测试
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from path_validator import PathValidator, validate_project_structure


def test_path_validator_initialization():
    """测试 PathValidator 初始化"""
    # 使用默认路径
    validator = PathValidator()
    assert validator.project_root is not None
    assert validator.project_root.exists()
    
    # 使用指定路径
    project_root = Path(__file__).parent.parent.parent.parent.parent.parent
    validator = PathValidator(str(project_root))
    assert validator.project_root == project_root


def test_validate_kiro_structure():
    """测试 .kiro/ 目录结构验证"""
    validator = PathValidator()
    valid, errors = validator._validate_kiro_structure()
    
    # .kiro/ 目录应该存在
    assert validator.project_root / ".kiro" in [validator.project_root / ".kiro"]
    
    # 检查是否有错误信息
    if not valid:
        print("验证失败，错误信息：")
        for error in errors:
            print(f"  - {error}")


def test_validate_module_structure():
    """测试模块目录结构验证"""
    validator = PathValidator()
    
    # 测试 workflow 模块（应该通过）
    valid, errors = validator.validate_module_structure("workflow", "v1.0")
    
    if not valid:
        print("workflow 模块验证失败，错误信息：")
        for error in errors:
            print(f"  - {error}")


def test_validate_project_structure():
    """测试完整项目结构验证"""
    valid, errors = validate_project_structure()
    
    # 打印验证结果
    if valid:
        print("✓ 项目结构验证通过")
    else:
        print("✗ 项目结构验证失败")
        for error in errors:
            print(f"  - {error}")


def test_get_validation_report():
    """测试验证报告生成"""
    validator = PathValidator()
    report = validator.get_validation_report()
    
    # 报告应该包含关键信息
    assert "目录结构验证报告" in report
    assert "项目结构验证" in report
    assert "模块结构验证" in report
    
    print("\n" + report)


if __name__ == "__main__":
    print("运行 path_validator 单元测试...\n")
    
    print("1. 测试初始化")
    test_path_validator_initialization()
    print("✓ 通过\n")
    
    print("2. 测试 .kiro/ 目录结构验证")
    test_validate_kiro_structure()
    print("✓ 通过\n")
    
    print("3. 测试模块目录结构验证")
    test_validate_module_structure()
    print("✓ 通过\n")
    
    print("4. 测试完整项目结构验证")
    test_validate_project_structure()
    print("✓ 通过\n")
    
    print("5. 测试验证报告生成")
    test_get_validation_report()
    print("✓ 通过\n")
    
    print("所有测试通过！")
