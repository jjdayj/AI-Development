"""
优先级排序器模块

该模块负责按优先级对激活的模块进行排序。

排序规则：
1. 按 priority 从高到低排序
2. 如果 priority 相同，按模块名称字母顺序排序

需求追溯：
- 需求 6.1：按 Priority 从高到低排序
- 需求 6.2：Priority 相同时按模块名称字母顺序排序
"""

from typing import List, Dict, Any


def sort_by_priority(modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    按优先级排序模块
    
    Args:
        modules: 模块列表，每个元素包含 name, version, priority 等字段
        
    Returns:
        排序后的模块列表
        
    排序规则：
        1. 按 priority 从高到低排序（使用负数实现降序）
        2. 如果 priority 相同，按模块名称字母顺序排序
        
    示例：
        >>> modules = [
        ...     {'name': 'git-commit', 'version': 'v1.0', 'priority': 80},
        ...     {'name': 'workflow', 'version': 'v1.0', 'priority': 200},
        ...     {'name': 'ai-dev', 'version': 'v1.0', 'priority': 100},
        ...     {'name': 'git-rollback', 'version': 'v1.0', 'priority': 80}
        ... ]
        >>> sorted_modules = sort_by_priority(modules)
        >>> [m['name'] for m in sorted_modules]
        ['workflow', 'ai-dev', 'git-commit', 'git-rollback']
    """
    if not modules:
        return []
    
    # 验证输入数据
    for module in modules:
        if not isinstance(module, dict):
            raise TypeError(f"模块必须是字典类型，实际类型: {type(module)}")
        
        if 'name' not in module:
            raise KeyError(f"模块缺少必需字段 'name': {module}")
        
        if 'priority' not in module:
            raise KeyError(f"模块缺少必需字段 'priority': {module}")
        
        if not isinstance(module['priority'], (int, float)):
            raise TypeError(f"模块 {module['name']} 的 priority 必须是数字类型，实际类型: {type(module['priority'])}")
    
    # 按优先级排序
    # key 函数返回元组：(-priority, name)
    # -priority 实现从高到低排序，name 实现字母顺序排序
    return sorted(
        modules,
        key=lambda m: (-m['priority'], m['name'])
    )


def validate_module_data(modules: List[Dict[str, Any]]) -> List[str]:
    """
    验证模块数据的完整性
    
    Args:
        modules: 模块列表
        
    Returns:
        错误信息列表，如果为空则表示验证通过
    """
    errors = []
    
    if not isinstance(modules, list):
        errors.append(f"modules 必须是列表类型，实际类型: {type(modules)}")
        return errors
    
    for i, module in enumerate(modules):
        if not isinstance(module, dict):
            errors.append(f"模块 {i} 必须是字典类型，实际类型: {type(module)}")
            continue
        
        # 检查必需字段
        required_fields = ['name', 'priority']
        for field in required_fields:
            if field not in module:
                errors.append(f"模块 {i} 缺少必需字段 '{field}': {module}")
        
        # 检查字段类型
        if 'name' in module and not isinstance(module['name'], str):
            errors.append(f"模块 {i} 的 'name' 必须是字符串类型，实际类型: {type(module['name'])}")
        
        if 'priority' in module and not isinstance(module['priority'], (int, float)):
            errors.append(f"模块 {i} 的 'priority' 必须是数字类型，实际类型: {type(module['priority'])}")
    
    return errors


def get_sorting_key(module: Dict[str, Any]) -> tuple:
    """
    获取模块的排序键
    
    Args:
        module: 模块字典
        
    Returns:
        排序键元组 (-priority, name)
    """
    return (-module['priority'], module['name'])


def sort_by_priority_with_validation(modules: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[str]]:
    """
    带验证的优先级排序
    
    Args:
        modules: 模块列表
        
    Returns:
        (排序后的模块列表, 错误信息列表)
    """
    # 验证输入数据
    errors = validate_module_data(modules)
    if errors:
        return [], errors
    
    try:
        sorted_modules = sort_by_priority(modules)
        return sorted_modules, []
    except Exception as e:
        return [], [f"排序过程中发生错误: {str(e)}"]