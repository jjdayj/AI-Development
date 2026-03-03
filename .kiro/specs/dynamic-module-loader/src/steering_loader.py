"""
Steering 加载器（Steering Loader）

负责构建模块 Steering 文件路径和加载 Steering 文件内容，
支持标准模块和 workflow 模块的特殊处理。

需求追溯：需求 7.1, 7.3, 8.1, 8.2, 8.3, 14.3
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


class SteeringLoader:
    """Steering 加载器
    
    负责构建 Steering 文件路径和加载 Steering 文件内容。
    """
    
    def __init__(self, base_path: str = ".kiro/modules"):
        """初始化 Steering 加载器
        
        Args:
            base_path: 模块基础路径，默认为 ".kiro/modules"
        """
        self.base_path = Path(base_path)
    
    def build_steering_path(self, module_name: str, module_version: str) -> str:
        """构建 Steering 文件路径
        
        根据模块名称和版本构建 Steering 文件的完整路径。
        对于 workflow 模块使用特殊文件名 workflow_selector.md。
        
        Args:
            module_name: 模块名称
            module_version: 模块版本
            
        Returns:
            str: Steering 文件的完整路径
            
        需求追溯：需求 7.1, 7.3
        """
        # 处理 workflow 模块的特殊文件名
        if module_name == 'workflow':
            filename = 'workflow_selector.md'
        else:
            filename = f'{module_name}.md'
        
        # 构建完整路径：.kiro/modules/{module}/{version}/steering/{filename}
        steering_path = self.base_path / module_name / module_version / 'steering' / filename
        
        return str(steering_path)
    
    def validate_path_format(self, path: str) -> bool:
        """验证路径格式是否正确
        
        验证构建的路径是否符合预期的格式规范。
        
        Args:
            path: 要验证的路径
            
        Returns:
            bool: 路径格式是否正确
            
        需求追溯：需求 7.1
        """
        try:
            if not path or not path.strip():
                return False
                
            path_obj = Path(path)
            parts = path_obj.parts
            
            # 验证路径结构：应该包含 {module}, {version}, steering, {filename}
            if len(parts) < 4:
                return False
            
            # 验证必须包含 steering 目录
            if 'steering' not in parts:
                return False
            
            # 验证文件扩展名
            if not path.endswith('.md'):
                return False
            
            # 验证 steering 目录的位置（应该在倒数第二个位置）
            steering_index = -1
            for i, part in enumerate(parts):
                if part == 'steering':
                    steering_index = i
                    break
            
            # steering 目录后面应该只有一个文件名
            if steering_index == -1 or steering_index != len(parts) - 2:
                return False
            
            # 对于标准路径，还需要验证是否包含 modules（但对于测试路径可能不包含）
            # 如果路径包含 .kiro，则必须包含 modules
            if '.kiro' in parts and 'modules' not in parts:
                return False
            
            # 如果路径太短（只有 module/version/steering/file），可能是无效的基础路径
            # 正常情况下应该有更长的路径结构
            if len(parts) == 4:
                # 检查是否是绝对路径或包含合理的基础路径
                first_part = parts[0]
                if not (first_part.startswith('.') or first_part.startswith('/') or 
                       len(first_part) > 1 and first_part[1] == ':'):  # Windows drive letter
                    return False
            
            return True
            
        except Exception:
            return False
    
    def load_steering_content(self, steering_path: str) -> Tuple[bool, str, Optional[str]]:
        """加载 Steering 文件内容
        
        读取指定路径的 Steering 文件内容，处理文件不存在和读取失败的情况。
        
        Args:
            steering_path: Steering 文件路径
            
        Returns:
            Tuple[bool, str, Optional[str]]: (是否成功, 内容或错误信息, 错误类型)
            - 成功时：(True, 文件内容, None)
            - 失败时：(False, 错误信息, 错误类型)
            
        需求追溯：需求 8.1, 8.2, 8.3
        """
        try:
            path_obj = Path(steering_path)
            
            # 检查文件是否存在
            if not path_obj.exists():
                return False, f"Steering 文件不存在: {steering_path}", "FileNotFound"
            
            # 检查是否为文件
            if not path_obj.is_file():
                return False, f"路径不是文件: {steering_path}", "NotAFile"
            
            # 读取文件内容
            with open(path_obj, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return True, content, None
            
        except PermissionError:
            return False, f"没有权限读取文件: {steering_path}", "PermissionError"
        except UnicodeDecodeError as e:
            return False, f"文件编码错误: {steering_path}, 错误: {e}", "EncodingError"
        except FileNotFoundError:
            return False, f"Steering 文件不存在: {steering_path}", "FileNotFound"
        except IOError as e:
            return False, f"文件读取失败: {steering_path}, 错误: {e}", "IOError"
        except Exception as e:
            return False, f"未知错误: {steering_path}, 错误: {e}", "UnknownError"
    
    def create_module_comment(self, 
                            module_name: str, 
                            module_version: str, 
                            module_priority: int, 
                            activation_conditions: Dict[str, Any]) -> str:
        """创建模块标识注释
        
        为 Steering 文件内容添加模块标识注释，包含模块信息和激活条件。
        
        Args:
            module_name: 模块名称
            module_version: 模块版本
            module_priority: 模块优先级
            activation_conditions: 激活条件
            
        Returns:
            str: 模块标识注释
            
        需求追溯：需求 14.3
        """
        # 格式化激活条件为简洁的字符串
        conditions_str = self._format_activation_conditions(activation_conditions)
        
        comment = (
            f"<!-- Module: {module_name} | "
            f"Version: {module_version} | "
            f"Priority: {module_priority} | "
            f"Activated: {conditions_str} -->\n\n"
        )
        
        return comment
    
    def load_steering(self, 
                     module_name: str, 
                     module_version: str, 
                     module_priority: int, 
                     activation_conditions: Dict[str, Any]) -> Tuple[bool, str, Optional[str]]:
        """加载模块的 Steering 文件
        
        完整的 Steering 加载流程：构建路径 → 验证格式 → 读取内容 → 添加注释。
        
        Args:
            module_name: 模块名称
            module_version: 模块版本
            module_priority: 模块优先级
            activation_conditions: 激活条件
            
        Returns:
            Tuple[bool, str, Optional[str]]: (是否成功, 内容或错误信息, 错误类型)
            - 成功时：(True, 带注释的 Steering 内容, None)
            - 失败时：(False, 错误信息, 错误类型)
            
        需求追溯：需求 7.1, 8.1, 8.2, 8.3, 14.3
        """
        # 1. 构建 Steering 文件路径
        steering_path = self.build_steering_path(module_name, module_version)
        
        # 2. 验证路径格式
        if not self.validate_path_format(steering_path):
            return False, f"路径格式无效: {steering_path}", "InvalidPath"
        
        # 3. 加载文件内容
        success, content, error_type = self.load_steering_content(steering_path)
        
        if not success:
            return False, content, error_type
        
        # 4. 添加模块标识注释
        comment = self.create_module_comment(
            module_name, module_version, module_priority, activation_conditions
        )
        
        final_content = comment + content
        
        return True, final_content, None
    
    def _format_activation_conditions(self, conditions: Dict[str, Any]) -> str:
        """格式化激活条件为简洁字符串
        
        将激活条件字典转换为简洁的字符串表示。
        
        Args:
            conditions: 激活条件字典
            
        Returns:
            str: 格式化的条件字符串
        """
        if not conditions:
            return "always"
        
        # 处理简单条件
        if conditions.get('always'):
            return "always"
        
        if 'directory_match' in conditions:
            patterns = conditions['directory_match']
            if isinstance(patterns, list):
                return f"dir:{','.join(patterns[:2])}{'...' if len(patterns) > 2 else ''}"
            else:
                return f"dir:{patterns}"
        
        if 'file_type_match' in conditions:
            patterns = conditions['file_type_match']
            if isinstance(patterns, list):
                return f"type:{','.join(patterns[:2])}{'...' if len(patterns) > 2 else ''}"
            else:
                return f"type:{patterns}"
        
        # 处理复合条件
        if 'and' in conditions:
            return "and_logic"
        
        if 'or' in conditions:
            return "or_logic"
        
        # 默认情况
        return "custom"
    
    def get_module_info(self, steering_path: str) -> Optional[Dict[str, str]]:
        """从路径中提取模块信息
        
        从 Steering 文件路径中解析出模块名称和版本信息。
        
        Args:
            steering_path: Steering 文件路径
            
        Returns:
            Optional[Dict[str, str]]: 模块信息字典，包含 module_name 和 version
            如果解析失败返回 None
        """
        try:
            path_obj = Path(steering_path)
            parts = path_obj.parts
            
            # 查找 modules 的位置
            modules_index = -1
            for i, part in enumerate(parts):
                if part == 'modules':
                    modules_index = i
                    break
            
            if modules_index == -1 or modules_index + 2 >= len(parts):
                return None
            
            module_name = parts[modules_index + 1]
            version = parts[modules_index + 2]
            
            return {
                'module_name': module_name,
                'version': version
            }
            
        except Exception:
            return None


# 便捷函数
def build_steering_path(module_name: str, module_version: str, base_path: str = ".kiro/modules") -> str:
    """构建 Steering 文件路径（便捷函数）
    
    Args:
        module_name: 模块名称
        module_version: 模块版本
        base_path: 模块基础路径
        
    Returns:
        str: Steering 文件路径
    """
    loader = SteeringLoader(base_path)
    path = loader.build_steering_path(module_name, module_version)
    # 统一使用正斜杠，确保跨平台兼容性
    return path.replace('\\', '/')


def load_steering_file(module_name: str, 
                      module_version: str, 
                      module_priority: int, 
                      activation_conditions: Dict[str, Any],
                      base_path: str = ".kiro/modules") -> Tuple[bool, str, Optional[str]]:
    """加载 Steering 文件（便捷函数）
    
    Args:
        module_name: 模块名称
        module_version: 模块版本
        module_priority: 模块优先级
        activation_conditions: 激活条件
        base_path: 模块基础路径
        
    Returns:
        Tuple[bool, str, Optional[str]]: (是否成功, 内容或错误信息, 错误类型)
    """
    loader = SteeringLoader(base_path)
    return loader.load_steering(module_name, module_version, module_priority, activation_conditions)


def validate_steering_path(path: str) -> bool:
    """验证 Steering 路径格式（便捷函数）
    
    Args:
        path: 要验证的路径
        
    Returns:
        bool: 路径格式是否正确
    """
    loader = SteeringLoader()
    return loader.validate_path_format(path)