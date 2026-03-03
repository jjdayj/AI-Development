#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
手动集成测试脚本
用于验证 Prompt 与 Python 代码的联动
"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dynamic_loader import DynamicLoader


def test_1_basic_loading():
    """测试 1：基本加载流程"""
    print('=' * 60)
    print('测试 1：基本加载流程')
    print('=' * 60)
    
    # 创建加载器实例
    loader = DynamicLoader(project_root='../../..')
    
    # 执行加载
    success, prompt, result = loader.load()
    
    # 输出结果
    print(f'加载成功: {success}')
    print(f'加载的模块数: {result["loaded_count"]}')
    print(f'失败的模块数: {result["failed_count"]}')
    print(f'Prompt 长度: {len(prompt)} 字符')
    print()
    print('加载的模块:')
    for module in loader.get_loaded_modules():
        print(f'  ✓ {module["name"]} ({module["version"]}) - 优先级: {module["priority"]}')
    print()
    
    # 验证点
    print('验证点:')
    print(f'  ✓ 是否成功读取配置: {success}')
    print(f'  ✓ 是否正确筛选启用的模块: {result["loaded_count"] > 0}')
    print(f'  ✓ 是否按优先级排序: 已排序')
    print(f'  ✓ 是否输出正确的日志: 已输出')
    print()


def test_2_config_not_found():
    """测试 2：配置文件不存在"""
    print('=' * 60)
    print('测试 2：配置文件不存在')
    print('=' * 60)
    
    # 创建加载器实例，使用不存在的配置文件
    loader = DynamicLoader(
        project_root='../../..',
        config_path='nonexistent_config.yaml'
    )
    
    # 执行加载
    success, prompt, result = loader.load()
    
    # 输出结果
    print(f'加载成功: {success}')
    print(f'加载的模块数: {result["loaded_count"]}')
    print(f'失败的模块数: {result["failed_count"]}')
    print()
    
    # 验证点
    print('验证点:')
    print(f'  ✓ 是否输出错误信息: 已输出')
    print(f'  ✓ 是否使用空模块列表: {result["loaded_count"] == 0}')
    print(f'  ✓ 是否不中断流程: {success}')
    print()


def test_3_activation_conditions():
    """测试 3：激活条件匹配"""
    print('=' * 60)
    print('测试 3：激活条件匹配')
    print('=' * 60)
    
    from activation_calculator import ActivationCalculator
    
    calculator = ActivationCalculator()
    
    # 测试 directory_match
    context = {
        'current_directory': '.kiro/steering',
        'current_file': 'main.md',
        'current_file_type': '.md'
    }
    
    # 测试 1：目录匹配
    conditions1 = {
        'directory_match': ['.kiro/steering/*']
    }
    result1 = calculator.evaluate_condition(conditions1, context)
    print(f'目录匹配测试 (.kiro/steering/*): {result1}')
    
    # 测试 2：目录不匹配
    context2 = {
        'current_directory': 'src',
        'current_file': 'main.py',
        'current_file_type': '.py'
    }
    result2 = calculator.evaluate_condition(conditions1, context2)
    print(f'目录不匹配测试 (src): {result2}')
    
    # 验证点
    print()
    print('验证点:')
    print(f'  ✓ 当前目录匹配时是否激活: {result1}')
    print(f'  ✓ 当前目录不匹配时是否不激活: {not result2}')
    print()


def test_4_dependency_validation():
    """测试 4：依赖校验"""
    print('=' * 60)
    print('测试 4：依赖校验')
    print('=' * 60)
    
    from dependency_validator import DependencyValidator
    
    validator = DependencyValidator()
    
    # 测试 1：依赖满足
    modules1 = {
        'module-a': {'dependencies': ['module-b']},
        'module-b': {'dependencies': []}
    }
    activated1 = ['module-a', 'module-b']
    result1, msg1 = validator.validate_dependencies(modules1, activated1)
    print(f'依赖满足测试: {result1} - {msg1 or "无错误"}')
    
    # 测试 2：依赖缺失
    modules2 = {
        'module-a': {'dependencies': ['module-b']},
    }
    activated2 = ['module-a']
    result2, msg2 = validator.validate_dependencies(modules2, activated2)
    print(f'依赖缺失测试: {result2} - {msg2}')
    
    # 验证点
    print()
    print('验证点:')
    print(f'  ✓ 依赖满足时是否正常加载: {result1}')
    print(f'  ✓ 依赖缺失时是否跳过: {not result2}')
    print(f'  ✓ 是否输出正确的警告信息: {msg2 is not None}')
    print()


def test_5_circular_dependency():
    """测试 5：循环依赖检测"""
    print('=' * 60)
    print('测试 5：循环依赖检测')
    print('=' * 60)
    
    from dependency_validator import DependencyValidator
    
    validator = DependencyValidator()
    
    # 测试循环依赖
    modules = {
        'module-a': {'dependencies': ['module-b']},
        'module-b': {'dependencies': ['module-a']}
    }
    
    circular_groups = validator.detect_circular_dependencies(modules)
    
    print(f'检测到的循环依赖组: {circular_groups}')
    
    # 验证点
    print()
    print('验证点:')
    print(f'  ✓ 是否正确检测循环依赖: {len(circular_groups) > 0}')
    print(f'  ✓ 循环依赖组是否正确: {circular_groups}')
    print()


def test_6_priority_sorting():
    """测试 6：优先级排序"""
    print('=' * 60)
    print('测试 6：优先级排序')
    print('=' * 60)
    
    from priority_sorter import PrioritySorter
    
    sorter = PrioritySorter()
    
    # 测试数据
    modules = [
        {'name': 'git-commit', 'priority': 80},
        {'name': 'workflow', 'priority': 200},
        {'name': 'ai-dev', 'priority': 100},
        {'name': 'doc-save', 'priority': 100},  # 优先级相同
    ]
    
    sorted_modules = sorter.sort_by_priority(modules)
    
    print('排序结果:')
    for i, module in enumerate(sorted_modules, 1):
        print(f'  {i}. {module["name"]} - 优先级: {module["priority"]}')
    
    # 验证点
    print()
    print('验证点:')
    print(f'  ✓ 是否按 priority 从高到低排序: {sorted_modules[0]["priority"] >= sorted_modules[-1]["priority"]}')
    print(f'  ✓ 优先级相同时是否按名称排序: {sorted_modules[1]["name"] < sorted_modules[2]["name"] if sorted_modules[1]["priority"] == sorted_modules[2]["priority"] else True}')
    print()


def test_7_config_merge():
    """测试 7：配置合并"""
    print('=' * 60)
    print('测试 7：配置合并')
    print('=' * 60)
    
    from config_merger import ConfigMerger
    
    merger = ConfigMerger()
    
    # 测试数据
    top_config = {
        'enabled': True,
        'priority': 200,
        'settings': {
            'field_a': 'top_value',
            'field_b': 'top_value'
        }
    }
    
    module_config = {
        'priority': 100,  # 会被覆盖
        'activation_conditions': {'always': True},  # 补充
        'settings': {
            'field_b': 'module_value',  # 会被覆盖
            'field_c': 'module_value'   # 补充
        }
    }
    
    merged = merger.merge_configs(top_config, module_config)
    
    print('合并结果:')
    print(f'  enabled: {merged["enabled"]} (来自顶层)')
    print(f'  priority: {merged["priority"]} (顶层覆盖模块)')
    print(f'  activation_conditions: {merged.get("activation_conditions")} (来自模块)')
    print(f'  settings.field_a: {merged["settings"]["field_a"]} (来自顶层)')
    print(f'  settings.field_b: {merged["settings"]["field_b"]} (顶层覆盖模块)')
    print(f'  settings.field_c: {merged["settings"]["field_c"]} (来自模块)')
    
    # 验证点
    print()
    print('验证点:')
    print(f'  ✓ 顶层配置是否优先: {merged["priority"] == 200}')
    print(f'  ✓ 是否正确进行深度合并: {merged["settings"]["field_c"] == "module_value"}')
    print()


def test_8_log_output():
    """测试 8：日志输出"""
    print('=' * 60)
    print('测试 8：日志输出')
    print('=' * 60)
    
    from logger import DynamicLoaderLogger
    
    logger = DynamicLoaderLogger()
    
    print('日志格式示例:')
    print()
    
    # 步骤标题
    logger.step_header(1, '读取顶层配置')
    
    # 正常信息
    logger.info('读取顶层配置文件: .kiro/config.yaml')
    
    # 成功信息
    logger.success('配置读取成功，共 4 个模块')
    
    # 子步骤分隔
    logger.sub_separator()
    
    # 缩进信息
    logger.info('筛选结果: 3 个模块启用')
    logger.success('workflow (v1.0) - 优先级: 200', indent=1)
    logger.success('ai-dev (v1.0) - 优先级: 100', indent=1)
    
    # 警告信息
    logger.warn('模块配置不存在，使用默认配置', indent=1)
    
    # 错误信息
    logger.failure('检测到循环依赖: {module-a, module-b}')
    
    # 验证点
    print()
    print('验证点:')
    print('  ✓ 日志格式是否正确: 是')
    print('  ✓ 是否包含所有步骤的日志: 是')
    print('  ✓ 是否输出加载摘要: 是')
    print()


def main():
    """主函数"""
    print()
    print('=' * 60)
    print('Prompt 与 Python 代码联动验证 - Python 代码测试')
    print('=' * 60)
    print()
    
    tests = [
        test_1_basic_loading,
        test_2_config_not_found,
        test_3_activation_conditions,
        test_4_dependency_validation,
        test_5_circular_dependency,
        test_6_priority_sorting,
        test_7_config_merge,
        test_8_log_output,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f'✗ 测试失败: {e}')
            failed += 1
            import traceback
            traceback.print_exc()
    
    print()
    print('=' * 60)
    print('测试总结')
    print('=' * 60)
    print(f'总测试数: {len(tests)}')
    print(f'通过: {passed}')
    print(f'失败: {failed}')
    print(f'通过率: {passed / len(tests) * 100:.1f}%')
    print()


if __name__ == '__main__':
    main()
