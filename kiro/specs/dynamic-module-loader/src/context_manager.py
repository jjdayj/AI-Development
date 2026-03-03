"""
当前上下文管理器（Current Context Manager）

负责管理当前活跃需求的上下文信息（current_context.yaml），
支持读取、写入、更新和格式校验功能。

需求追溯：需求 17.1, 17.2, 17.3, 17.4
"""

import os
import yaml
from datetime import datetime
from typing import Dict, Any, Optional, Union
from pathlib import Path


class ContextManager:
    """当前上下文管理器
    
    管理 current_context.yaml 文件的读写操作，
    维护当前活跃需求的上下文信息。
    """
    
    def __init__(self, context_path: str = ".kiro/current_context.yaml"):
        """初始化上下文管理器
        
        Args:
            context_path: current_context.yaml 文件路径
        """
        self.context_path = Path(context_path)
        
    def read_context(self) -> Optional[Dict[str, Any]]:
        """读取当前上下文信息
        
        Returns:
            Dict[str, Any]: 上下文信息字典，如果文件不存在返回 None
            
        Raises:
            yaml.YAMLError: YAML 格式错误
            IOError: 文件读取错误
        """
        if not self.context_path.exists():
            return None
            
        try:
            with open(self.context_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
                return content if content is not None else {}
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML 格式错误: {e}")
        except IOError as e:
            raise IOError(f"文件读取失败: {e}")
    
    def write_context(self, context: Dict[str, Any]) -> bool:
        """写入上下文信息
        
        Args:
            context: 要写入的上下文信息
            
        Returns:
            bool: 写入是否成功
            
        Raises:
            yaml.YAMLError: YAML 序列化错误
            IOError: 文件写入错误
        """
        try:
            # 确保目录存在
            self.context_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 添加更新时间戳
            context_with_timestamp = context.copy()
            context_with_timestamp['updated_at'] = datetime.now().isoformat()
            
            with open(self.context_path, 'w', encoding='utf-8') as f:
                yaml.dump(context_with_timestamp, f, 
                         default_flow_style=False, 
                         allow_unicode=True,
                         sort_keys=False)
            return True
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML 序列化错误: {e}")
        except IOError as e:
            raise IOError(f"文件写入失败: {e}")
    
    def update_context(self, updates: Dict[str, Any]) -> bool:
        """更新上下文信息
        
        读取现有上下文，合并更新内容，然后写回文件。
        
        Args:
            updates: 要更新的字段
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 读取现有上下文
            current_context = self.read_context() or {}
            
            # 深度合并更新内容
            merged_context = self._deep_merge(current_context, updates)
            
            # 写回文件
            return self.write_context(merged_context)
            
        except Exception as e:
            raise Exception(f"上下文更新失败: {e}")
    
    def validate_context_format(self, context: Dict[str, Any]) -> tuple[bool, list[str]]:
        """验证上下文格式
        
        验证 current_context.yaml 的嵌套结构和必需字段。
        
        Args:
            context: 要验证的上下文信息
            
        Returns:
            tuple[bool, list[str]]: (是否有效, 错误信息列表)
        """
        errors = []
        
        if not isinstance(context, dict):
            errors.append("上下文必须是字典类型")
            return False, errors
        
        # 验证顶层结构
        required_top_level = ['active_requirement', 'environment', 'updated_at']
        for field in required_top_level:
            if field not in context:
                errors.append(f"缺少必需字段: {field}")
        
        # 验证 active_requirement 结构
        if 'active_requirement' in context:
            active_req = context['active_requirement']
            if not isinstance(active_req, dict):
                errors.append("active_requirement 必须是字典类型")
            else:
                required_active_fields = [
                    'module_name', 'version', 'requirement_path', 
                    'requirement_title', 'created_at'
                ]
                for field in required_active_fields:
                    if field not in active_req:
                        errors.append(f"active_requirement 缺少必需字段: {field}")
                
                # 验证字段值的有效性
                if 'module_name' in active_req and not isinstance(active_req['module_name'], str):
                    errors.append("active_requirement.module_name 必须是字符串")
                if 'version' in active_req and not isinstance(active_req['version'], str):
                    errors.append("active_requirement.version 必须是字符串")
                if 'requirement_path' in active_req and not isinstance(active_req['requirement_path'], str):
                    errors.append("active_requirement.requirement_path 必须是字符串")
                if 'requirement_title' in active_req and not isinstance(active_req['requirement_title'], str):
                    errors.append("active_requirement.requirement_title 必须是字符串")
                
                # 验证 created_at 时间戳格式
                if 'created_at' in active_req:
                    try:
                        datetime.fromisoformat(active_req['created_at'].replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        errors.append("active_requirement.created_at 时间戳格式无效")
        
        # 验证 environment 结构
        if 'environment' in context:
            env = context['environment']
            if not isinstance(env, dict):
                errors.append("environment 必须是字典类型")
            else:
                required_env_fields = [
                    'current_directory', 'current_file_path', 'current_file_type'
                ]
                for field in required_env_fields:
                    if field not in env:
                        errors.append(f"environment 缺少必需字段: {field}")
                
                # 验证字段值的有效性
                if 'current_directory' in env and not isinstance(env['current_directory'], str):
                    errors.append("environment.current_directory 必须是字符串")
                if 'current_file_path' in env and not isinstance(env['current_file_path'], str):
                    errors.append("environment.current_file_path 必须是字符串")
                if 'current_file_type' in env and not isinstance(env['current_file_type'], str):
                    errors.append("environment.current_file_type 必须是字符串")
        
        # 验证时间戳格式
        if 'updated_at' in context:
            try:
                datetime.fromisoformat(context['updated_at'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                errors.append("updated_at 时间戳格式无效")
        
        return len(errors) == 0, errors
    
    def validate_and_fix_context(self, context: Dict[str, Any]) -> tuple[Dict[str, Any], list[str]]:
        """验证并尝试修复上下文格式
        
        Args:
            context: 要验证和修复的上下文信息
            
        Returns:
            tuple[Dict[str, Any], list[str]]: (修复后的上下文, 警告信息列表)
        """
        warnings = []
        fixed_context = context.copy() if isinstance(context, dict) else {}
        
        # 确保顶层结构存在
        if 'active_requirement' not in fixed_context:
            fixed_context['active_requirement'] = {}
            warnings.append("自动添加缺失的 active_requirement 字段")
        
        if 'environment' not in fixed_context:
            fixed_context['environment'] = {
                'current_directory': os.getcwd(),
                'current_file_path': '',
                'current_file_type': ''
            }
            warnings.append("自动添加缺失的 environment 字段")
        
        if 'updated_at' not in fixed_context:
            fixed_context['updated_at'] = datetime.now().isoformat()
            warnings.append("自动添加缺失的 updated_at 字段")
        
        # 修复 active_requirement 字段
        active_req = fixed_context['active_requirement']
        if not isinstance(active_req, dict):
            fixed_context['active_requirement'] = {}
            active_req = fixed_context['active_requirement']
            warnings.append("修复 active_requirement 字段类型")
        
        required_active_fields = {
            'module_name': '',
            'version': 'v1.0',
            'requirement_path': '',
            'requirement_title': '',
            'created_at': datetime.now().isoformat()
        }
        
        for field, default_value in required_active_fields.items():
            if field not in active_req:
                active_req[field] = default_value
                warnings.append(f"自动添加缺失的 active_requirement.{field} 字段")
        
        # 修复 environment 字段
        env = fixed_context['environment']
        if not isinstance(env, dict):
            fixed_context['environment'] = {
                'current_directory': os.getcwd(),
                'current_file_path': '',
                'current_file_type': ''
            }
            warnings.append("修复 environment 字段类型")
        else:
            required_env_fields = {
                'current_directory': os.getcwd(),
                'current_file_path': '',
                'current_file_type': ''
            }
            
            for field, default_value in required_env_fields.items():
                if field not in env:
                    env[field] = default_value
                    warnings.append(f"自动添加缺失的 environment.{field} 字段")
        
        return fixed_context, warnings
    
    def _deep_merge(self, base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """深度合并两个字典
        
        Args:
            base: 基础字典
            updates: 更新字典
            
        Returns:
            Dict[str, Any]: 合并后的字典
        """
        result = base.copy()
        
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def context_exists(self) -> bool:
        """检查上下文文件是否存在
        
        Returns:
            bool: 文件是否存在
        """
        return self.context_path.exists()
    
    def delete_context(self) -> bool:
        """删除上下文文件
        
        Returns:
            bool: 删除是否成功
        """
        try:
            if self.context_path.exists():
                self.context_path.unlink()
                return True
            return True  # 文件不存在也算成功
        except OSError as e:
            raise OSError(f"删除上下文文件失败: {e}")
    
    def backup_context(self, backup_suffix: Optional[str] = None) -> Optional[str]:
        """备份当前上下文文件
        
        Args:
            backup_suffix: 备份文件后缀，默认使用时间戳
            
        Returns:
            Optional[str]: 备份文件路径，如果原文件不存在返回 None
        """
        if not self.context_path.exists():
            return None
            
        if backup_suffix is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_suffix = f"backup.{timestamp}"
            
        backup_path = self.context_path.with_suffix(f".{backup_suffix}")
        
        try:
            import shutil
            shutil.copy2(self.context_path, backup_path)
            return str(backup_path)
        except OSError as e:
            raise OSError(f"备份上下文文件失败: {e}")


def create_sample_context() -> Dict[str, Any]:
    """创建示例上下文数据
    
    Returns:
        Dict[str, Any]: 示例上下文信息
    """
    return {
        'active_requirement': {
            'module_name': 'dynamic-module-loader',
            'version': 'v1.0',
            'requirement_path': 'requirements/dynamic-module-loader/v1.0',
            'requirement_title': '动态模块加载器',
            'created_at': datetime.now().isoformat(),
            'status': 'in_progress'
        },
        'environment': {
            'current_directory': os.getcwd(),
            'current_file_path': '',
            'current_file_type': ''
        },
        'updated_at': datetime.now().isoformat()
    }


# 便捷函数
def read_current_context(context_path: str = ".kiro/current_context.yaml") -> Optional[Dict[str, Any]]:
    """读取当前上下文（便捷函数）
    
    Args:
        context_path: 上下文文件路径
        
    Returns:
        Optional[Dict[str, Any]]: 上下文信息，文件不存在返回 None
    """
    manager = ContextManager(context_path)
    return manager.read_context()


def write_current_context(context: Dict[str, Any], 
                         context_path: str = ".kiro/current_context.yaml") -> bool:
    """写入当前上下文（便捷函数）
    
    Args:
        context: 上下文信息
        context_path: 上下文文件路径
        
    Returns:
        bool: 写入是否成功
    """
    manager = ContextManager(context_path)
    return manager.write_context(context)


def update_current_context(updates: Dict[str, Any], 
                          context_path: str = ".kiro/current_context.yaml") -> bool:
    """更新当前上下文（便捷函数）
    
    Args:
        updates: 要更新的字段
        context_path: 上下文文件路径
        
    Returns:
        bool: 更新是否成功
    """
    manager = ContextManager(context_path)
    return manager.update_context(updates)