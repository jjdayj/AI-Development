"""
激活状态计算器模块

该模块负责计算模块的最终激活状态，支持全局开关过滤和条件评估。

计算规则：
    Activation_State = Global_Switch AND Module_Condition

支持的条件类型：
    - always: 始终激活
    - directory_match: 按目录路径匹配（支持通配符）
    - file_type_match: 按文件类型匹配
    - and: 逻辑与组合（所有子条件都满足）
    - or: 逻辑或组合（任一子条件满足）

作者: yangzhuo
日期: 2026-03-03
版本: v1.0
"""

from typing import Dict, Any
from path_matcher import match_directory, match_file_type


def calculate_activation(
    global_switch: bool,
    activation_conditions: Dict[str, Any],
    context: Dict[str, Any]
) -> bool:
    """
    计算模块激活状态
    
    Args:
        global_switch: 全局开关状态（config.yaml 中的 enabled 字段）
        activation_conditions: 激活条件配置（模块 config.yaml 中的 activation_conditions）
        context: 当前上下文（目录、文件类型等）
        
    Returns:
        是否激活（True/False）
        
    Examples:
        >>> calculate_activation(True, {'always': True}, {})
        True
        
        >>> calculate_activation(False, {'always': True}, {})
        False
        
        >>> context = {'current_directory': '.kiro/steering', 'current_file_type': '.md'}
        >>> conditions = {'directory_match': ['.kiro/steering/*']}
        >>> calculate_activation(True, conditions, context)
        True
    """
    # 如果全局开关关闭，直接返回 False
    if not global_switch:
        return False
    
    # 如果没有配置激活条件，默认为 always: true
    if not activation_conditions:
        return True
    
    # 计算条件匹配结果
    return evaluate_condition(activation_conditions, context)


def evaluate_condition(condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """
    递归评估激活条件
    
    Args:
        condition: 条件配置（可能是单个条件或组合条件）
        context: 当前上下文
        
    Returns:
        条件是否满足
        
    Examples:
        >>> evaluate_condition({'always': True}, {})
        True
        
        >>> context = {'current_directory': '.kiro/steering'}
        >>> evaluate_condition({'directory_match': ['.kiro/steering/*']}, context)
        True
        
        >>> context = {'current_file_type': '.md'}
        >>> evaluate_condition({'file_type_match': ['.md', '.yaml']}, context)
        True
    """
    # 情况 1：always 条件
    if condition.get('always'):
        return True
    
    # 情况 2：directory_match 条件
    if 'directory_match' in condition:
        patterns = condition['directory_match']
        current_dir = context.get('current_directory', '')
        return match_directory(current_dir, patterns)
    
    # 情况 3：file_type_match 条件
    if 'file_type_match' in condition:
        patterns = condition['file_type_match']
        current_file = context.get('current_file_type', '')
        return match_file_type(current_file, patterns)
    
    # 情况 4：AND 逻辑组合
    if 'and' in condition:
        sub_conditions = condition['and']
        if not isinstance(sub_conditions, list):
            return False
        
        # 所有子条件都必须满足
        for sub_condition in sub_conditions:
            if not evaluate_condition(sub_condition, context):
                return False
        return True
    
    # 情况 5：OR 逻辑组合
    if 'or' in condition:
        sub_conditions = condition['or']
        if not isinstance(sub_conditions, list):
            return False
        
        # 任一子条件满足即可
        for sub_condition in sub_conditions:
            if evaluate_condition(sub_condition, context):
                return True
        return False
    
    # 如果没有匹配任何条件类型，返回 False
    return False
