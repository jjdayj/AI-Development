"""
config_reader.py 的单元测试
"""

import sys
import tempfile
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from config_reader import ConfigReader, read_config, validate_semver


def test_config_reader_initialization():
    """测试 ConfigReader 初始化"""
    reader = ConfigReader()
    assert reader.project_root is not None
    assert reader.project_root.exists()
    print(f"✓ 项目根目录: {reader.project_root}")


def test_validate_semver():
    """测试版本号验证"""
    reader = ConfigReader()
    
    # 有效的版本号
    valid_versions = [
        "1.0.0",
        "v1.0.0",
        "1.0.0-alpha",
        "v1.0.0-alpha",
        "1.0.0-simple",
        "v1.0.0-simple",
        "1.0.0+build",
        "v1.0.0+build",
        "1.0.0-alpha.1",
        "2.3.4-beta.2+build.123",
        "1.0",  # 简化版本
        "v1.0",
    ]
    
    print("✓ 测试有效版本号：")
    for version in valid_versions:
        result = reader.validate_semver(version)
        if result:
            print(f"  ✓ {version}")
        else:
            print(f"  ✗ {version} (应该有效但验证失败)")
            assert False, f"版本号 {version} 应该有效"
    
    # 无效的版本号
    invalid_versions = [
        "",
        "1",
        "1.0.0.0",
        "v1.0.0.0",
        "invalid",
        "1.0.0-",
        "1.0.0+",
    ]
    
    print("\n✓ 测试无效版本号：")
    for version in invalid_versions:
        result = reader.validate_semver(version)
        if not result:
            print(f"  ✓ {version} (正确识别为无效)")
        else:
            print(f"  ✗ {version} (应该无效但验证通过)")


def test_read_config():
    """测试读取配置文件"""
    reader = ConfigReader()
    
    # 读取实际的配置文件
    success, config, error = reader.read_config()
    
    if success:
        print(f"✓ 配置读取成功")
        print(f"  配置版本: {config.get('version')}")
        print(f"  模块数量: {len(config.get('modules', {}))}")
        
        # 验证配置结构
        assert 'modules' in config
        assert isinstance(config['modules'], dict)
        
        # 验证模块配置
        for module_name, module_config in config['modules'].items():
            assert 'enabled' in module_config
            assert 'version' in module_config
            assert 'priority' in module_config
            print(f"  ✓ 模块 {module_name} 配置完整")
    else:
        print(f"✗ 配置读取失败: {error}")
        assert False, f"配置读取失败: {error}"


def test_get_enabled_modules():
    """测试获取启用的模块"""
    reader = ConfigReader()
    success, config, error = reader.read_config()
    
    assert success, f"配置读取失败: {error}"
    
    enabled_modules = reader.get_enabled_modules(config)
    
    print(f"✓ 找到 {len(enabled_modules)} 个启用的模块")
    
    for module in enabled_modules:
        assert 'name' in module
        assert 'version' in module
        assert 'priority' in module
        assert 'enabled' in module
        assert module['enabled'] is True
        print(f"  ✓ {module['name']} (v{module['version']}) - 优先级: {module['priority']}")


def test_get_module_config():
    """测试读取模块配置"""
    reader = ConfigReader()
    
    # 测试读取 workflow 模块配置
    success, module_config, error = reader.get_module_config("workflow", "v1.0")
    
    if success:
        print(f"✓ workflow 模块配置读取成功")
        print(f"  激活条件: {module_config.get('activation_conditions')}")
    else:
        print(f"✗ workflow 模块配置读取失败: {error}")


def test_invalid_config():
    """测试无效配置处理"""
    reader = ConfigReader()
    
    # 测试不存在的配置文件
    success, config, error = reader.read_config("/nonexistent/config.yaml")
    
    if not success:
        print(f"✓ 正确处理不存在的配置文件")
        print(f"  错误信息: {error}")
    else:
        print(f"✗ 应该失败但成功了")
        assert False


def test_config_validation():
    """测试配置验证"""
    reader = ConfigReader()
    
    # 创建测试配置
    test_config = {
        'version': '2.0',
        'modules': {
            'valid-module': {
                'enabled': True,
                'version': 'v1.0.0',
                'priority': 100
            },
            'invalid-version': {
                'enabled': True,
                'version': 'invalid',
                'priority': 90
            },
            'missing-priority': {
                'enabled': True,
                'version': 'v1.0.0'
            }
        }
    }
    
    validated_config = reader._validate_modules(test_config)
    
    # 应该只有 valid-module 通过验证
    assert 'valid-module' in validated_config['modules']
    assert 'invalid-version' not in validated_config['modules']
    assert 'missing-priority' not in validated_config['modules']
    
    print(f"✓ 配置验证正确")
    print(f"  有效模块: {list(validated_config['modules'].keys())}")


if __name__ == "__main__":
    print("运行 config_reader 单元测试...\n")
    
    print("1. 测试初始化")
    test_config_reader_initialization()
    print()
    
    print("2. 测试版本号验证")
    test_validate_semver()
    print()
    
    print("3. 测试读取配置文件")
    test_read_config()
    print()
    
    print("4. 测试获取启用的模块")
    test_get_enabled_modules()
    print()
    
    print("5. 测试读取模块配置")
    test_get_module_config()
    print()
    
    print("6. 测试无效配置处理")
    test_invalid_config()
    print()
    
    print("7. 测试配置验证")
    test_config_validation()
    print()
    
    print("所有测试通过！")
