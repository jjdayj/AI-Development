"""
Prompt 整合器（Prompt Integrator）

负责将多个激活模块的 Steering 内容整合为一个完整的 Prompt 上下文，
包括层级结构说明、激活模块列表和按优先级排序的内容拼接。

需求追溯：需求 15.3
"""

from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional


class PromptIntegrator:
    """Prompt 整合器
    
    负责将多个模块的 Steering 内容整合为完整的 Prompt 上下文。
    """
    
    def __init__(self):
        """初始化 Prompt 整合器"""
        pass
    
    def integrate_prompts(self, 
                         steering_contents: List[Tuple[str, str, int, Dict[str, Any], str]],
                         include_hierarchy: bool = True,
                         include_module_list: bool = True) -> str:
        """整合多个模块的 Steering 内容
        
        将按优先级排序的 Steering 内容整合为一个完整的 Prompt 上下文。
        
        Args:
            steering_contents: 模块 Steering 内容列表，每个元素为 
                             (module_name, version, priority, conditions, content)
            include_hierarchy: 是否包含层级结构说明
            include_module_list: 是否包含激活模块列表
            
        Returns:
            str: 整合后的完整 Prompt 内容
            
        需求追溯：需求 15.3
        """
        if not steering_contents:
            return self._create_empty_prompt()
        
        # 构建整合后的 Prompt
        prompt_parts = []
        
        # 1. 添加层级结构说明
        if include_hierarchy:
            hierarchy_section = self._create_hierarchy_section()
            prompt_parts.append(hierarchy_section)
        
        # 2. 添加激活模块列表
        if include_module_list:
            module_list_section = self._create_module_list_section(steering_contents)
            prompt_parts.append(module_list_section)
        
        # 3. 按优先级顺序拼接 Steering 内容
        content_section = self._create_content_section(steering_contents)
        prompt_parts.append(content_section)
        
        # 4. 添加整合完成标记
        completion_section = self._create_completion_section(len(steering_contents))
        prompt_parts.append(completion_section)
        
        return '\n\n'.join(prompt_parts)
    
    def _create_hierarchy_section(self) -> str:
        """创建层级结构说明部分
        
        Returns:
            str: 层级结构说明内容
        """
        return """# Kiro Prompt 层级结构

本 Prompt 采用三层架构：

- **L0 (顶层入口)**: `.kiro/steering/main.md` - 主入口 Prompt
- **L1 (加载器逻辑)**: 动态模块加载器 - 负责读取配置、筛选和加载模块
- **L2 (模块规则)**: 激活的模块 Steering 规则 - 按优先级从高到低应用

**优先级规则**: L0 > L1 > L2，高优先级规则可覆盖低优先级规则。"""
    
    def _create_module_list_section(self, 
                                   steering_contents: List[Tuple[str, str, int, Dict[str, Any], str]]) -> str:
        """创建激活模块列表部分
        
        Args:
            steering_contents: 模块 Steering 内容列表
            
        Returns:
            str: 激活模块列表内容
        """
        if not steering_contents:
            return "# 激活的模块\n\n当前没有激活的模块。"
        
        lines = ["# 激活的模块", ""]
        lines.append(f"共激活 {len(steering_contents)} 个模块，按优先级排序：")
        lines.append("")
        
        for i, (module_name, version, priority, conditions, _) in enumerate(steering_contents, 1):
            # 格式化激活条件
            conditions_str = self._format_activation_conditions(conditions)
            
            lines.append(f"{i}. **{module_name}** ({version})")
            lines.append(f"   - 优先级: {priority}")
            lines.append(f"   - 激活条件: {conditions_str}")
            lines.append("")
        
        return '\n'.join(lines).rstrip()
    
    def _create_content_section(self, 
                               steering_contents: List[Tuple[str, str, int, Dict[str, Any], str]]) -> str:
        """创建 Steering 内容部分
        
        Args:
            steering_contents: 模块 Steering 内容列表
            
        Returns:
            str: 拼接后的 Steering 内容
        """
        if not steering_contents:
            return ""
        
        lines = ["# 模块 Steering 规则", ""]
        lines.append("以下是按优先级顺序加载的模块 Steering 规则：")
        lines.append("")
        
        for module_name, version, priority, conditions, content in steering_contents:
            # 添加模块分隔符
            separator = f"## {module_name} ({version}) - 优先级 {priority}"
            lines.append(separator)
            lines.append("")
            
            # 添加模块内容
            if content.strip():
                lines.append(content.strip())
            else:
                lines.append("*此模块没有 Steering 内容*")
            
            lines.append("")
            lines.append("---")  # 模块间分隔线
            lines.append("")
        
        # 移除最后的分隔线
        if lines and lines[-2] == "---":
            lines = lines[:-2]
        
        return '\n'.join(lines).rstrip()
    
    def _create_completion_section(self, module_count: int) -> str:
        """创建整合完成标记部分
        
        Args:
            module_count: 激活的模块数量
            
        Returns:
            str: 整合完成标记内容
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        lines = [
            "# Prompt 整合完成",
            "",
            f"- **整合时间**: {timestamp}",
            f"- **激活模块数**: {module_count}",
            f"- **整合状态**: ✅ 完成",
            "",
            "所有激活的模块 Steering 规则已按优先级顺序整合完成。"
        ]
        
        return '\n'.join(lines)
    
    def _create_empty_prompt(self) -> str:
        """创建空 Prompt（当没有激活模块时）
        
        Returns:
            str: 空 Prompt 内容
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return f"""# Kiro Prompt 层级结构

本 Prompt 采用三层架构：

- **L0 (顶层入口)**: `.kiro/steering/main.md` - 主入口 Prompt
- **L1 (加载器逻辑)**: 动态模块加载器 - 负责读取配置、筛选和加载模块
- **L2 (模块规则)**: 激活的模块 Steering 规则 - 按优先级从高到低应用

**优先级规则**: L0 > L1 > L2，高优先级规则可覆盖低优先级规则。

# 激活的模块

当前没有激活的模块。

# Prompt 整合完成

- **整合时间**: {timestamp}
- **激活模块数**: 0
- **整合状态**: ✅ 完成

当前没有激活的模块需要整合。"""
    
    def _format_activation_conditions(self, conditions: Dict[str, Any]) -> str:
        """格式化激活条件为可读字符串
        
        Args:
            conditions: 激活条件字典
            
        Returns:
            str: 格式化的条件字符串
        """
        if not conditions:
            return "无条件"
        
        # 处理简单条件
        if conditions.get('always'):
            return "始终激活"
        
        if 'directory_match' in conditions:
            patterns = conditions['directory_match']
            if isinstance(patterns, list):
                return f"目录匹配: {', '.join(patterns)}"
            else:
                return f"目录匹配: {patterns}"
        
        if 'file_type_match' in conditions:
            patterns = conditions['file_type_match']
            if isinstance(patterns, list):
                return f"文件类型: {', '.join(patterns)}"
            else:
                return f"文件类型: {patterns}"
        
        # 处理复合条件
        if 'and' in conditions:
            sub_conditions = conditions['and']
            sub_strs = [self._format_activation_conditions(cond) for cond in sub_conditions]
            return f"AND({', '.join(sub_strs)})"
        
        if 'or' in conditions:
            sub_conditions = conditions['or']
            sub_strs = [self._format_activation_conditions(cond) for cond in sub_conditions]
            return f"OR({', '.join(sub_strs)})"
        
        # 默认情况
        return "自定义条件"
    
    def get_integration_summary(self, 
                               steering_contents: List[Tuple[str, str, int, Dict[str, Any], str]]) -> Dict[str, Any]:
        """获取整合摘要信息
        
        Args:
            steering_contents: 模块 Steering 内容列表
            
        Returns:
            Dict[str, Any]: 整合摘要信息
        """
        if not steering_contents:
            return {
                'total_modules': 0,
                'total_content_length': 0,
                'modules': [],
                'priority_range': None,
                'integration_time': datetime.now().isoformat()
            }
        
        modules = []
        total_content_length = 0
        priorities = []
        
        for module_name, version, priority, conditions, content in steering_contents:
            modules.append({
                'name': module_name,
                'version': version,
                'priority': priority,
                'conditions': conditions,
                'content_length': len(content) if content else 0
            })
            
            total_content_length += len(content) if content else 0
            priorities.append(priority)
        
        return {
            'total_modules': len(steering_contents),
            'total_content_length': total_content_length,
            'modules': modules,
            'priority_range': {
                'min': min(priorities),
                'max': max(priorities)
            } if priorities else None,
            'integration_time': datetime.now().isoformat()
        }
    
    def validate_integration_input(self, 
                                  steering_contents: List[Tuple[str, str, int, Dict[str, Any], str]]) -> Tuple[bool, Optional[str]]:
        """验证整合输入的有效性
        
        Args:
            steering_contents: 模块 Steering 内容列表
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        if not isinstance(steering_contents, list):
            return False, "steering_contents 必须是列表类型"
        
        for i, item in enumerate(steering_contents):
            if not isinstance(item, tuple) or len(item) != 5:
                return False, f"第 {i+1} 个元素必须是包含 5 个元素的元组"
            
            module_name, version, priority, conditions, content = item
            
            if not isinstance(module_name, str) or not module_name.strip():
                return False, f"第 {i+1} 个元素的模块名称必须是非空字符串"
            
            if not isinstance(version, str) or not version.strip():
                return False, f"第 {i+1} 个元素的版本必须是非空字符串"
            
            if not isinstance(priority, int):
                return False, f"第 {i+1} 个元素的优先级必须是整数"
            
            if not isinstance(conditions, dict):
                return False, f"第 {i+1} 个元素的激活条件必须是字典"
            
            if not isinstance(content, str):
                return False, f"第 {i+1} 个元素的内容必须是字符串"
        
        return True, None


# 便捷函数
def integrate_steering_contents(steering_contents: List[Tuple[str, str, int, Dict[str, Any], str]],
                               include_hierarchy: bool = True,
                               include_module_list: bool = True) -> str:
    """整合 Steering 内容（便捷函数）
    
    Args:
        steering_contents: 模块 Steering 内容列表
        include_hierarchy: 是否包含层级结构说明
        include_module_list: 是否包含激活模块列表
        
    Returns:
        str: 整合后的 Prompt 内容
    """
    integrator = PromptIntegrator()
    return integrator.integrate_prompts(steering_contents, include_hierarchy, include_module_list)


def get_integration_summary(steering_contents: List[Tuple[str, str, int, Dict[str, Any], str]]) -> Dict[str, Any]:
    """获取整合摘要信息（便捷函数）
    
    Args:
        steering_contents: 模块 Steering 内容列表
        
    Returns:
        Dict[str, Any]: 整合摘要信息
    """
    integrator = PromptIntegrator()
    return integrator.get_integration_summary(steering_contents)


def validate_integration_input(steering_contents: List[Tuple[str, str, int, Dict[str, Any], str]]) -> Tuple[bool, Optional[str]]:
    """验证整合输入（便捷函数）
    
    Args:
        steering_contents: 模块 Steering 内容列表
        
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    integrator = PromptIntegrator()
    return integrator.validate_integration_input(steering_contents)