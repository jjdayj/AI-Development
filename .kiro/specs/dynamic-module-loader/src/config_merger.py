"""
配置合并器模块

本模块提供配置合并功能，用于处理顶层配置和模块配置之间的冲突。

需求追溯：
- 隐含需求：配置冲突处理

合并规则：
1. 顶层配置的全局开关（enabled）优先
2. 顶层配置的优先级（priority）优先
3. 模块配置的激活条件（activation_conditions）优先
4. 其他字段进行深度合并
"""

from typing import Dict, Any, Optional
from copy import deepcopy


def merge_configs(
    top_level_config: Dict[str, Any],
    module_config: Dict[str, Any],
    module_name: str
) -> Dict[str, Any]:
    """
    合并顶层配置和模块配置
    
    合并规则：
    1. 顶层配置的 enabled 字段优先（全局开关）
    2. 顶层配置的 priority 字段优先（优先级管理）
    3. 顶层配置的 version 字段优先（版本管理）
    4. 模块配置的 activation_conditions 字段优先（激活条件）
    5. 其他字段进行深度合并（模块配置覆盖顶层配置）
    
    Args:
        top_level_config: 顶层配置（来自 .kiro/config.yaml）
        module_config: 模块配置（来自 .kiro/modules/{module}/{version}/config.yaml）
        module_name: 模块名称（用于日志）
    
    Returns:
        合并后的配置字典
    
    需求追溯：隐含需求（配置冲突处理）
    
    示例：
        >>> top_config = {
        ...     "enabled": True,
        ...     "version": "v1.0",
        ...     "priority": 200,
        ...     "custom_field": "top_value"
        ... }
        >>> module_config = {
        ...     "activation_conditions": {"always": True},
        ...     "custom_field": "module_value",
        ...     "module_specific": "value"
        ... }
        >>> result = merge_configs(top_config, module_config, "test-module")
        >>> result["enabled"]  # 顶层配置优先
        True
        >>> result["activation_conditions"]  # 模块配置优先
        {'always': True}
        >>> result["custom_field"]  # 模块配置覆盖
        'module_value'
    """
    # 创建深拷贝，避免修改原始配置
    merged = deepcopy(module_config)
    
    # 规则 1: 顶层配置的 enabled 字段优先
    if "enabled" in top_level_config:
        merged["enabled"] = top_level_config["enabled"]
    
    # 规则 2: 顶层配置的 priority 字段优先
    if "priority" in top_level_config:
        merged["priority"] = top_level_config["priority"]
    
    # 规则 3: 顶层配置的 version 字段优先
    if "version" in top_level_config:
        merged["version"] = top_level_config["version"]
    
    # 规则 4: 模块配置的 activation_conditions 字段优先（已经在 merged 中）
    # 不需要额外处理
    
    # 规则 5: 其他字段进行深度合并
    for key, value in top_level_config.items():
        # 跳过已处理的优先字段
        if key in ["enabled", "priority", "version"]:
            continue
        
        # 跳过模块配置中的 activation_conditions
        if key == "activation_conditions":
            continue
        
        # 如果模块配置中没有该字段，直接使用顶层配置的值
        if key not in merged:
            merged[key] = deepcopy(value)
        # 如果两者都是字典，进行深度合并
        elif isinstance(value, dict) and isinstance(merged[key], dict):
            merged[key] = deep_merge(value, merged[key])
        # 否则，模块配置覆盖顶层配置（已经在 merged 中）
    
    return merged


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    深度合并两个字典
    
    Args:
        base: 基础字典
        override: 覆盖字典（优先级更高）
    
    Returns:
        合并后的字典
    
    规则：
    - 如果两者都是字典，递归合并
    - 否则，override 的值覆盖 base 的值
    
    示例：
        >>> base = {"a": 1, "b": {"c": 2, "d": 3}}
        >>> override = {"b": {"c": 20, "e": 4}, "f": 5}
        >>> result = deep_merge(base, override)
        >>> result
        {'a': 1, 'b': {'c': 20, 'd': 3, 'e': 4}, 'f': 5}
    """
    result = deepcopy(base)
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # 递归合并字典
            result[key] = deep_merge(result[key], value)
        else:
            # 覆盖值
            result[key] = deepcopy(value)
    
    return result


def validate_merged_config(config: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    验证合并后的配置是否有效
    
    Args:
        config: 合并后的配置字典
    
    Returns:
        (是否有效, 错误消息列表)
    
    验证规则：
    1. 必须包含 enabled 字段
    2. 必须包含 version 字段
    3. 必须包含 priority 字段
    4. enabled 必须是布尔值
    5. priority 必须是数字
    6. version 必须是字符串
    
    示例：
        >>> config = {"enabled": True, "version": "v1.0", "priority": 100}
        >>> is_valid, errors = validate_merged_config(config)
        >>> is_valid
        True
        >>> errors
        []
    """
    errors = []
    
    # 检查必需字段
    required_fields = ["enabled", "version", "priority"]
    for field in required_fields:
        if field not in config:
            errors.append(f"缺少必需字段: {field}")
    
    # 检查字段类型
    if "enabled" in config and not isinstance(config["enabled"], bool):
        errors.append(f"enabled 字段必须是布尔值，当前类型: {type(config['enabled']).__name__}")
    
    if "priority" in config and not isinstance(config["priority"], (int, float)):
        errors.append(f"priority 字段必须是数字，当前类型: {type(config['priority']).__name__}")
    
    if "version" in config and not isinstance(config["version"], str):
        errors.append(f"version 字段必须是字符串，当前类型: {type(config['version']).__name__}")
    
    return len(errors) == 0, errors


def merge_multiple_configs(
    configs: list[tuple[str, Dict[str, Any]]],
    priority_order: Optional[list[str]] = None
) -> Dict[str, Any]:
    """
    合并多个配置
    
    Args:
        configs: 配置列表，每个元素是 (配置名称, 配置字典) 的元组
        priority_order: 优先级顺序列表（可选），列表中靠前的配置优先级更高
    
    Returns:
        合并后的配置字典
    
    规则：
    - 如果指定了 priority_order，按照该顺序合并（优先级高的最后合并，覆盖优先级低的）
    - 否则，按照 configs 列表的顺序合并（后面的覆盖前面的）
    
    示例：
        >>> configs = [
        ...     ("default", {"a": 1, "b": 2}),
        ...     ("user", {"b": 20, "c": 3}),
        ...     ("local", {"c": 30, "d": 4})
        ... ]
        >>> result = merge_multiple_configs(configs)
        >>> result
        {'a': 1, 'b': 20, 'c': 30, 'd': 4}
    """
    if not configs:
        return {}
    
    # 如果指定了优先级顺序，重新排序配置
    if priority_order:
        config_dict = {name: config for name, config in configs}
        ordered_configs = []
        
        # 添加未在优先级列表中的配置（优先级最低）
        for name, config in configs:
            if name not in priority_order:
                ordered_configs.append((name, config))
        
        # 按优先级顺序添加配置（反向，优先级高的最后添加）
        for name in reversed(priority_order):
            if name in config_dict:
                ordered_configs.append((name, config_dict[name]))
        
        configs = ordered_configs
    
    # 从第一个配置开始
    result = deepcopy(configs[0][1])
    
    # 依次合并后续配置
    for name, config in configs[1:]:
        result = deep_merge(result, config)
    
    return result


def get_merge_summary(
    top_level_config: Dict[str, Any],
    module_config: Dict[str, Any],
    merged_config: Dict[str, Any]
) -> str:
    """
    生成配置合并摘要
    
    Args:
        top_level_config: 顶层配置
        module_config: 模块配置
        merged_config: 合并后的配置
    
    Returns:
        合并摘要字符串
    
    示例：
        >>> top_config = {"enabled": True, "priority": 200}
        >>> module_config = {"activation_conditions": {"always": True}}
        >>> merged = merge_configs(top_config, module_config, "test")
        >>> summary = get_merge_summary(top_config, module_config, merged)
        >>> "enabled: 顶层配置" in summary
        True
    """
    lines = []
    lines.append("配置合并摘要：")
    lines.append("")
    
    # 分析每个字段的来源
    all_keys = set(top_level_config.keys()) | set(module_config.keys())
    
    for key in sorted(all_keys):
        in_top = key in top_level_config
        in_module = key in module_config
        
        if in_top and in_module:
            # 两者都有，判断使用了哪个
            if key in ["enabled", "priority", "version"]:
                lines.append(f"  {key}: 顶层配置优先")
            elif key == "activation_conditions":
                lines.append(f"  {key}: 模块配置优先")
            else:
                lines.append(f"  {key}: 深度合并")
        elif in_top:
            lines.append(f"  {key}: 来自顶层配置")
        else:
            # 只在模块配置中
            if key == "activation_conditions":
                lines.append(f"  {key}: 模块配置优先")
            else:
                lines.append(f"  {key}: 来自模块配置")
    
    return "\n".join(lines)
