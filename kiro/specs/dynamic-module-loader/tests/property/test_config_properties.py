"""
配置读取器的属性测试

使用 Hypothesis 框架进行基于属性的测试，验证：
- 属性 1：配置文件解析正确性
- 属性 13：版本号格式校验正确性
"""

import sys
import tempfile
from pathlib import Path
from hypothesis import given, strategies as st, settings, example

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from config_reader import ConfigReader


# ============================================================
# 属性 13：版本号格式校验正确性
# ============================================================

# 生成有效的 SemVer 版本号
@st.composite
def valid_semver(draw):
    """生成有效的 SemVer 版本号"""
    major = draw(st.integers(min_value=0, max_value=100))
    minor = draw(st.integers(min_value=0, max_value=100))
    patch = draw(st.integers(min_value=0, max_value=100))
    
    # 基础版本
    version = f"{major}.{minor}.{patch}"
    
    # 可选的 v 前缀
    if draw(st.booleans()):
        version = f"v{version}"
    
    # 可选的预发布标签
    if draw(st.booleans()):
        prerelease = draw(st.sampled_from([
            "alpha", "beta", "rc", "simple", "complex",
            "alpha.1", "beta.2", "rc.3"
        ]))
        version = f"{version}-{prerelease}"
    
    # 可选的构建元数据
    if draw(st.booleans()):
        build = draw(st.sampled_from([
            "build", "build.123", "20130313144700"
        ]))
        version = f"{version}+{build}"
    
    return version


# 生成无效的版本号
@st.composite
def invalid_semver(draw):
    """生成无效的版本号"""
    return draw(st.sampled_from([
        "",  # 空字符串
        "1",  # 只有主版本号
        "1.0.0.0",  # 四段版本号
        "v1.0.0.0",  # 带 v 的四段版本号
        "invalid",  # 完全无效
        "1.0.0-",  # 预发布标签为空
        "1.0.0+",  # 构建元数据为空
        "a.b.c",  # 非数字版本号
        "1.a.0",  # 部分非数字
    ]))


@given(version=valid_semver())
@settings(max_examples=100, deadline=None)
@example(version="1.0.0")
@example(version="v1.0.0")
@example(version="1.0.0-alpha")
@example(version="v1.0.0-simple")
def test_property_13_valid_semver(version):
    """
    属性 13：版本号格式校验正确性（有效版本）
    
    Feature: dynamic-module-loader
    Property 13: 版本号格式校验正确性
    
    对于任意有效的 SemVer 版本号，validate_semver() 应该返回 True
    """
    reader = ConfigReader()
    assert reader.validate_semver(version), f"有效版本号 {version} 被错误地拒绝"


@given(version=invalid_semver())
@settings(max_examples=100, deadline=None)
@example(version="")
@example(version="invalid")
def test_property_13_invalid_semver(version):
    """
    属性 13：版本号格式校验正确性（无效版本）
    
    Feature: dynamic-module-loader
    Property 13: 版本号格式校验正确性
    
    对于任意无效的版本号，validate_semver() 应该返回 False
    """
    reader = ConfigReader()
    assert not reader.validate_semver(version), f"无效版本号 {version} 被错误地接受"


# ============================================================
# 属性 1：配置文件解析正确性
# ============================================================

# 生成模块配置
@st.composite
def module_config(draw):
    """生成模块配置"""
    return {
        'enabled': draw(st.booleans()),
        'version': draw(valid_semver()),
        'priority': draw(st.integers(min_value=0, max_value=1000))
    }


# 生成完整配置
@st.composite
def full_config(draw):
    """生成完整的配置对象"""
    num_modules = draw(st.integers(min_value=0, max_value=10))
    
    modules = {}
    for i in range(num_modules):
        module_name = f"module-{i}"
        modules[module_name] = draw(module_config())
    
    return {
        'version': '2.0',
        'modules': modules
    }


@given(config=full_config())
@settings(max_examples=100, deadline=None)
@example(config={'version': '2.0', 'modules': {}})
@example(config={
    'version': '2.0',
    'modules': {
        'test-module': {
            'enabled': True,
            'version': 'v1.0.0',
            'priority': 100
        }
    }
})
def test_property_1_config_parsing(config):
    """
    属性 1：配置文件解析正确性
    
    Feature: dynamic-module-loader
    Property 1: 配置文件解析正确性
    
    对于任意有效的配置对象，_validate_modules() 应该：
    1. 返回一个配置对象
    2. 只包含有效的模块（有 enabled、version、priority 字段）
    3. 所有模块的版本号都符合 SemVer 规范
    """
    reader = ConfigReader()
    
    # 验证配置
    validated_config = reader._validate_modules(config)
    
    # 验证返回的是字典
    assert isinstance(validated_config, dict), "返回值应该是字典"
    
    # 验证包含 modules 字段
    assert 'modules' in validated_config, "应该包含 modules 字段"
    
    # 验证所有模块都有必需字段
    for module_name, module_config in validated_config['modules'].items():
        assert 'enabled' in module_config, f"模块 {module_name} 应该有 enabled 字段"
        assert 'version' in module_config, f"模块 {module_name} 应该有 version 字段"
        assert 'priority' in module_config, f"模块 {module_name} 应该有 priority 字段"
        
        # 验证版本号格式
        version = module_config['version']
        assert reader.validate_semver(version), f"模块 {module_name} 的版本号 {version} 应该有效"
        
        # 验证优先级是整数
        priority = module_config['priority']
        assert isinstance(priority, int), f"模块 {module_name} 的优先级应该是整数"


# ============================================================
# 属性 1 扩展：配置解析的幂等性
# ============================================================

@given(config=full_config())
@settings(max_examples=50, deadline=None)
def test_property_1_idempotence(config):
    """
    属性 1 扩展：配置解析的幂等性
    
    Feature: dynamic-module-loader
    Property 1: 配置文件解析正确性（幂等性）
    
    对于任意配置对象，多次调用 _validate_modules() 应该得到相同的结果
    """
    reader = ConfigReader()
    
    # 第一次验证
    result1 = reader._validate_modules(config)
    
    # 第二次验证
    result2 = reader._validate_modules(config)
    
    # 验证结果相同
    assert result1.keys() == result2.keys(), "两次验证的键应该相同"
    assert result1['modules'].keys() == result2['modules'].keys(), "两次验证的模块列表应该相同"


# ============================================================
# 属性 1 扩展：启用模块过滤正确性
# ============================================================

@given(config=full_config())
@settings(max_examples=50, deadline=None)
def test_property_1_enabled_filter(config):
    """
    属性 1 扩展：启用模块过滤正确性
    
    Feature: dynamic-module-loader
    Property 1: 配置文件解析正确性（启用模块过滤）
    
    get_enabled_modules() 返回的所有模块都应该是 enabled=True
    """
    reader = ConfigReader()
    
    # 验证配置
    validated_config = reader._validate_modules(config)
    
    # 获取启用的模块
    enabled_modules = reader.get_enabled_modules(validated_config)
    
    # 验证所有返回的模块都是启用的
    for module in enabled_modules:
        assert module['enabled'] is True, f"模块 {module['name']} 应该是启用的"
        
        # 验证模块在原始配置中确实是启用的
        original_module = validated_config['modules'][module['name']]
        assert original_module['enabled'] is True, f"模块 {module['name']} 在原始配置中应该是启用的"


# ============================================================
# 运行测试
# ============================================================

if __name__ == "__main__":
    import pytest
    
    print("=" * 60)
    print("运行配置读取器属性测试")
    print("=" * 60)
    print()
    
    # 运行 pytest
    pytest.main([__file__, "-v", "--tb=short"])
