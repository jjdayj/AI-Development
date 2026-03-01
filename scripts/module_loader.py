#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiro 模块加载器
功能：根据 kiro.yaml 加载指定版本的模块
"""
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Optional, List

class ModuleLoader:
    """Kiro 模块加载器"""
    
    def __init__(self, base_dir: str = ".kiro"):
        """
        初始化模块加载器
        :param base_dir: .kiro 目录路径
        """
        self.base_dir = Path(base_dir)
        self.config_file = self.base_dir / "kiro.yaml"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载全局配置"""
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"配置文件不存在：{self.config_file}\n"
                f"请先创建 kiro.yaml 配置文件"
            )
        
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            
            # 验证必需字段
            if "active_modules" not in config:
                raise ValueError("配置文件缺少 active_modules 字段")
            if "module_path_template" not in config:
                raise ValueError("配置文件缺少 module_path_template 字段")
            
            return config
        
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误：{e}")
    
    def get_module_path(self, module_name: str) -> Path:
        """
        获取模块路径
        :param module_name: 模块名称（如 "ai-dev"）
        :return: 模块路径
        """
        version = self.config["active_modules"].get(module_name)
        if not version:
            raise ValueError(
                f"模块未配置：{module_name}\n"
                f"可用模块：{list(self.config['active_modules'].keys())}"
            )
        
        template = self.config["module_path_template"]
        path_str = template.format(module=module_name, version=version)
        module_path = Path(path_str)
        
        if not module_path.exists():
            raise FileNotFoundError(
                f"模块路径不存在：{module_path}\n"
                f"请检查模块是否已正确安装"
            )
        
        return module_path
    
    def load_module_meta(self, module_name: str) -> Dict:
        """
        加载模块元数据
        :param module_name: 模块名称
        :return: 元数据字典
        """
        module_path = self.get_module_path(module_name)
        meta_file = module_path / "meta.yaml"
        
        if not meta_file.exists():
            return {
                "version": self.config["active_modules"][module_name],
                "name": module_name,
                "description": "无元数据"
            }
        
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"元数据文件格式错误：{e}")
    
    def get_module_file(self, module_name: str, file_type: str, file_name: str) -> Path:
        """
        获取模块内的文件路径
        :param module_name: 模块名称
        :param file_type: 文件类型（steering/scripts/configs）
        :param file_name: 文件名
        :return: 文件路径
        """
        module_path = self.get_module_path(module_name)
        file_path = module_path / file_type / file_name
        
        if not file_path.exists():
            raise FileNotFoundError(
                f"文件不存在：{file_path}\n"
                f"模块：{module_name}，类型：{file_type}，文件名：{file_name}"
            )
        
        return file_path
    
    def list_modules(self) -> List[str]:
        """
        列出所有已配置的模块
        :return: 模块名称列表
        """
        return list(self.config["active_modules"].keys())
    
    def list_module_versions(self, module_name: str) -> List[str]:
        """
        列出模块的所有可用版本
        :param module_name: 模块名称
        :return: 版本列表
        """
        modules_dir = self.base_dir / "modules" / module_name
        
        if not modules_dir.exists():
            return []
        
        versions = [
            d.name for d in modules_dir.iterdir() 
            if d.is_dir() and d.name.startswith("v")
        ]
        
        return sorted(versions, reverse=True)
    
    def switch_version(self, module_name: str, new_version: str):
        """
        切换模块版本
        :param module_name: 模块名称
        :param new_version: 新版本号（如 "v1.1"）
        """
        # 验证模块是否存在
        if module_name not in self.config["active_modules"]:
            raise ValueError(f"模块不存在：{module_name}")
        
        # 验证新版本是否存在
        new_path = Path(
            self.config["module_path_template"].format(
                module=module_name, version=new_version
            )
        )
        
        if not new_path.exists():
            available_versions = self.list_module_versions(module_name)
            raise FileNotFoundError(
                f"版本不存在：{new_version}\n"
                f"可用版本：{available_versions}"
            )
        
        # 更新配置文件
        old_version = self.config["active_modules"][module_name]
        self.config["active_modules"][module_name] = new_version
        
        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
        
        print(f"✅ 模块 {module_name} 版本切换成功")
        print(f"   {old_version} → {new_version}")
    
    def get_setting(self, key: str, default=None):
        """
        获取全局设置
        :param key: 设置键名
        :param default: 默认值
        :return: 设置值
        """
        return self.config.get("settings", {}).get(key, default)
    
    def validate_license(self, module_name: str) -> bool:
        """
        验证模块许可证（商业化功能）
        :param module_name: 模块名称
        :return: 是否有效
        """
        commercial_config = self.config.get("commercial", {})
        licensed_modules = commercial_config.get("licensed_modules", [])
        
        # 如果不是商业模块，直接返回 True
        if module_name not in licensed_modules:
            return True
        
        # 检查许可证密钥
        license_key = commercial_config.get("license_key", "")
        if not license_key:
            license_key = os.getenv("KIRO_LICENSE_KEY", "")
        
        if not license_key:
            print(f"⚠️  模块 {module_name} 需要许可证，但未配置 license_key")
            return False
        
        # TODO: 实现许可证验证逻辑（调用授权服务器）
        # 这里简化为检查密钥是否存在
        print(f"✅ 模块 {module_name} 许可证验证通过")
        return True
    
    def check_dependencies(self, module_name: str) -> List[str]:
        """
        检查模块依赖
        :param module_name: 模块名称
        :return: 依赖的模块列表
        """
        dependencies = self.config.get("dependencies", {})
        return dependencies.get(module_name, [])
    
    def print_module_info(self, module_name: str):
        """
        打印模块信息
        :param module_name: 模块名称
        """
        try:
            meta = self.load_module_meta(module_name)
            path = self.get_module_path(module_name)
            deps = self.check_dependencies(module_name)
            
            print(f"\n📦 模块信息：{module_name}")
            print(f"   版本：{meta.get('version', '未知')}")
            print(f"   描述：{meta.get('description', '无描述')}")
            print(f"   路径：{path}")
            print(f"   更新时间：{meta.get('update_time', '未知')}")
            
            if deps:
                print(f"   依赖：{', '.join(deps)}")
            
            # 检查许可证
            if not self.validate_license(module_name):
                print(f"   ⚠️  许可证验证失败")
        
        except Exception as e:
            print(f"❌ 获取模块信息失败：{e}")


# 使用示例和命令行接口
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Kiro 模块加载器")
    parser.add_argument("action", choices=["list", "info", "switch", "versions"],
                       help="操作类型")
    parser.add_argument("--module", help="模块名称")
    parser.add_argument("--version", help="版本号（用于 switch）")
    
    args = parser.parse_args()
    
    try:
        loader = ModuleLoader()
        
        if args.action == "list":
            # 列出所有模块
            modules = loader.list_modules()
            print("\n📦 已配置的模块：")
            for module in modules:
                version = loader.config["active_modules"][module]
                print(f"   - {module} ({version})")
        
        elif args.action == "info":
            # 显示模块信息
            if not args.module:
                print("❌ 请指定模块名称：--module <name>")
                sys.exit(1)
            loader.print_module_info(args.module)
        
        elif args.action == "switch":
            # 切换版本
            if not args.module or not args.version:
                print("❌ 请指定模块名称和版本：--module <name> --version <version>")
                sys.exit(1)
            loader.switch_version(args.module, args.version)
        
        elif args.action == "versions":
            # 列出模块的所有版本
            if not args.module:
                print("❌ 请指定模块名称：--module <name>")
                sys.exit(1)
            versions = loader.list_module_versions(args.module)
            current = loader.config["active_modules"][args.module]
            print(f"\n📦 模块 {args.module} 的可用版本：")
            for version in versions:
                marker = " (当前)" if version == current else ""
                print(f"   - {version}{marker}")
    
    except Exception as e:
        print(f"❌ 错误：{e}")
        sys.exit(1)
