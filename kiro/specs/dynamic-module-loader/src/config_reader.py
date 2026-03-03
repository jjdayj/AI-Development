"""
配置读取器

功能：
1. 读取和解析 YAML 配置文件
2. 验证版本号格式（SemVer 2.0.0）
3. 提供配置访问接口
"""

import re
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List


class ConfigReader:
    """配置文件读取器"""
    
    def __init__(self, project_root: str = None):
        """
        初始化配置读取器
        
        Args:
            project_root: 项目根目录路径
        """
        if project_root is None:
            # 从当前文件路径计算项目根目录
            current_file = Path(__file__).resolve()
            self.project_root = current_file.parent.parent.parent.parent.parent
        else:
            self.project_root = Path(project_root).resolve()
    
    def read_config(self, config_path: str = None) -> Tuple[bool, Dict[str, Any], str]:
        """
        读取配置文件
        
        Args:
            config_path: 配置文件路径，默认为 .kiro/config.yaml
        
        Returns:
            (是否成功, 配置对象, 错误信息)
        """
        if config_path is None:
            config_path = self.project_root / ".kiro" / "config.yaml"
        else:
            config_path = Path(config_path)
        
        # 检查文件是否存在
        if not config_path.exists():
            return False, {}, f"配置文件不存在: {config_path}"
        
        if not config_path.is_file():
            return False, {}, f"不是一个文件: {config_path}"
        
        try:
            # 读取 YAML 文件
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if config is None:
                return False, {}, "配置文件为空"
            
            # 验证配置结构
            if 'modules' not in config:
                return False, {}, "配置文件缺少 'modules' 字段"
            
            # 验证并过滤模块配置
            validated_config = self._validate_modules(config)
            
            return True, validated_config, ""
        
        except yaml.YAMLError as e:
            return False, {}, f"YAML 格式错误: {str(e)}"
        
        except Exception as e:
            return False, {}, f"读取配置文件失败: {str(e)}"
    
    def _validate_modules(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证并过滤模块配置
        
        Args:
            config: 原始配置对象
        
        Returns:
            验证后的配置对象
        """
        validated_config = config.copy()
        validated_modules = {}
        
        for module_name, module_config in config.get('modules', {}).items():
            # 检查必需字段
            if not isinstance(module_config, dict):
                print(f"[警告] 模块 {module_name} 配置格式错误，跳过")
                continue
            
            if 'enabled' not in module_config:
                print(f"[警告] 模块 {module_name} 缺少 'enabled' 字段，跳过")
                continue
            
            if 'version' not in module_config:
                print(f"[警告] 模块 {module_name} 缺少 'version' 字段，跳过")
                continue
            
            if 'priority' not in module_config:
                print(f"[警告] 模块 {module_name} 缺少 'priority' 字段，跳过")
                continue
            
            # 验证版本号
            version = module_config['version']
            if not self.validate_semver(version):
                print(f"[警告] 模块 {module_name} 的版本号不符合 SemVer 规范: {version}，跳过")
                continue
            
            # 验证优先级
            priority = module_config['priority']
            if not isinstance(priority, int):
                print(f"[警告] 模块 {module_name} 的优先级不是整数: {priority}，跳过")
                continue
            
            # 通过验证，添加到结果中
            validated_modules[module_name] = module_config
        
        validated_config['modules'] = validated_modules
        return validated_config
    
    def validate_semver(self, version: str) -> bool:
        """
        验证版本号是否符合语义化版本 2.0.0 规范
        
        支持的格式：
        - v1.0.0 或 1.0.0
        - v1.0.0-alpha 或 1.0.0-alpha
        - v1.0.0-simple 或 1.0.0-simple
        - v1.0.0+build 或 1.0.0+build
        
        Args:
            version: 版本号字符串
        
        Returns:
            是否符合规范
        """
        if not version:
            return False
        
        # 移除可选的 'v' 前缀
        if version.startswith('v'):
            version = version[1:]
        
        # SemVer 2.0.0 正则表达式
        # 格式：MAJOR.MINOR.PATCH[-prerelease][+build]
        semver_pattern = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
        
        # 简化版本（支持 v1.0 格式）
        simple_pattern = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
        
        return bool(re.match(semver_pattern, version)) or bool(re.match(simple_pattern, version))
    
    def get_enabled_modules(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        获取所有启用的模块
        
        Args:
            config: 配置对象
        
        Returns:
            启用的模块列表，每个元素包含 name, version, priority, enabled
        """
        enabled_modules = []
        
        for module_name, module_config in config.get('modules', {}).items():
            if module_config.get('enabled', False):
                enabled_modules.append({
                    'name': module_name,
                    'version': module_config['version'],
                    'priority': module_config['priority'],
                    'enabled': True
                })
        
        return enabled_modules
    
    def get_module_config(self, module_name: str, version: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        读取模块配置文件
        
        Args:
            module_name: 模块名称
            version: 模块版本
        
        Returns:
            (是否成功, 配置对象, 错误信息)
        """
        module_config_path = self.project_root / ".kiro" / "modules" / module_name / version / "config.yaml"
        
        if not module_config_path.exists():
            # 模块配置文件不存在，使用默认配置
            default_config = {
                'activation_conditions': {
                    'always': True
                }
            }
            return True, default_config, ""
        
        try:
            with open(module_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if config is None:
                # 空配置文件，使用默认配置
                default_config = {
                    'activation_conditions': {
                        'always': True
                    }
                }
                return True, default_config, ""
            
            # 如果没有 activation_conditions，添加默认值
            if 'activation_conditions' not in config:
                config['activation_conditions'] = {'always': True}
            
            return True, config, ""
        
        except yaml.YAMLError as e:
            return False, {}, f"YAML 格式错误: {str(e)}"
        
        except Exception as e:
            return False, {}, f"读取模块配置失败: {str(e)}"


# 便捷函数

def read_config(config_path: str = None) -> Tuple[bool, Dict[str, Any], str]:
    """
    读取配置文件（便捷函数）
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        (是否成功, 配置对象, 错误信息)
    """
    reader = ConfigReader()
    return reader.read_config(config_path)


def validate_semver(version: str) -> bool:
    """
    验证版本号（便捷函数）
    
    Args:
        version: 版本号字符串
    
    Returns:
        是否符合 SemVer 规范
    """
    reader = ConfigReader()
    return reader.validate_semver(version)


def main():
    """主函数：演示配置读取器的使用"""
    reader = ConfigReader()
    
    print("=" * 60)
    print("配置读取器")
    print("=" * 60)
    print()
    
    # 读取顶层配置
    print("1. 读取顶层配置")
    print("-" * 60)
    success, config, error = reader.read_config()
    
    if success:
        print(f"✓ 配置读取成功")
        print(f"  配置版本: {config.get('version', 'N/A')}")
        print(f"  模块数量: {len(config.get('modules', {}))}")
        print()
        
        # 列出所有模块
        print("2. 模块列表")
        print("-" * 60)
        for module_name, module_config in config.get('modules', {}).items():
            enabled = "✓" if module_config.get('enabled') else "✗"
            print(f"{enabled} {module_name}")
            print(f"  版本: {module_config.get('version')}")
            print(f"  优先级: {module_config.get('priority')}")
            print()
        
        # 列出启用的模块
        print("3. 启用的模块")
        print("-" * 60)
        enabled_modules = reader.get_enabled_modules(config)
        for module in enabled_modules:
            print(f"✓ {module['name']} (v{module['version']}) - 优先级: {module['priority']}")
    else:
        print(f"✗ 配置读取失败: {error}")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
