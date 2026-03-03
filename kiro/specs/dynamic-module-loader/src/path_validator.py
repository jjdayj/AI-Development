"""
目录规范校验工具

功能：
1. 验证 .kiro/ 目录结构符合规范
2. 验证 requirements/ 目录结构符合规范
3. 验证模块目录结构符合规范
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple


class PathValidator:
    """路径和目录结构校验器"""
    
    def __init__(self, project_root: str = None):
        """
        初始化校验器
        
        Args:
            project_root: 项目根目录路径，默认为当前工作目录
        """
        if project_root is None:
            # 从当前文件路径计算项目根目录
            # 当前文件：.kiro/specs/dynamic-module-loader/src/path_validator.py
            # 项目根目录：向上 4 级
            current_file = Path(__file__).resolve()
            # current_file.parent = .../src
            # current_file.parent.parent = .../dynamic-module-loader
            # current_file.parent.parent.parent = .../specs
            # current_file.parent.parent.parent.parent = .../.kiro
            # current_file.parent.parent.parent.parent.parent = 项目根目录
            self.project_root = current_file.parent.parent.parent.parent.parent
        else:
            self.project_root = Path(project_root).resolve()
    
    def validate_project_structure(self) -> Tuple[bool, List[str]]:
        """
        验证项目目录结构
        
        Returns:
            (是否通过, 错误信息列表)
        """
        errors = []
        
        # 验证 .kiro/ 目录
        kiro_valid, kiro_errors = self._validate_kiro_structure()
        errors.extend(kiro_errors)
        
        # 验证 requirements/ 目录（如果存在）
        requirements_path = self.project_root / "requirements"
        if requirements_path.exists():
            req_valid, req_errors = self._validate_requirements_structure()
            errors.extend(req_errors)
        
        return len(errors) == 0, errors
    
    def _validate_kiro_structure(self) -> Tuple[bool, List[str]]:
        """
        验证 .kiro/ 目录结构
        
        预期结构：
        .kiro/
        ├── config.yaml              # 顶层配置（必需）
        ├── steering/                # Steering 目录（必需）
        │   ├── main.md             # 主入口 Prompt（必需）
        │   └── STEERING_GUIDE.md   # 说明文档（可选）
        ├── modules/                # 模块目录（必需）
        ├── specs/                  # 规格说明目录（可选）
        └── templates/              # 模板目录（可选）
        
        Returns:
            (是否通过, 错误信息列表)
        """
        errors = []
        kiro_path = self.project_root / ".kiro"
        
        # 检查 .kiro/ 目录是否存在
        if not kiro_path.exists():
            errors.append("错误：.kiro/ 目录不存在")
            return False, errors
        
        if not kiro_path.is_dir():
            errors.append("错误：.kiro/ 不是一个目录")
            return False, errors
        
        # 检查必需文件
        required_files = [
            "config.yaml"
        ]
        
        for file_name in required_files:
            file_path = kiro_path / file_name
            if not file_path.exists():
                errors.append(f"错误：缺少必需文件 .kiro/{file_name}")
            elif not file_path.is_file():
                errors.append(f"错误：.kiro/{file_name} 不是一个文件")
        
        # 检查必需目录
        required_dirs = [
            "steering",
            "modules"
        ]
        
        for dir_name in required_dirs:
            dir_path = kiro_path / dir_name
            if not dir_path.exists():
                errors.append(f"错误：缺少必需目录 .kiro/{dir_name}/")
            elif not dir_path.is_dir():
                errors.append(f"错误：.kiro/{dir_name} 不是一个目录")
        
        # 检查 steering/ 目录内容
        steering_path = kiro_path / "steering"
        if steering_path.exists() and steering_path.is_dir():
            main_md = steering_path / "main.md"
            if not main_md.exists():
                errors.append("错误：缺少必需文件 .kiro/steering/main.md")
            elif not main_md.is_file():
                errors.append("错误：.kiro/steering/main.md 不是一个文件")
        
        return len(errors) == 0, errors
    
    def _validate_requirements_structure(self) -> Tuple[bool, List[str]]:
        """
        验证 requirements/ 目录结构
        
        预期结构：
        requirements/
        └── {module}/
            └── {version}/
                ├── meta.yaml           # 元信息（必需）
                └── requirement.md      # 需求文档（必需）
        
        Returns:
            (是否通过, 错误信息列表)
        """
        errors = []
        requirements_path = self.project_root / "requirements"
        
        if not requirements_path.exists():
            # requirements/ 目录是可选的
            return True, []
        
        if not requirements_path.is_dir():
            errors.append("错误：requirements/ 不是一个目录")
            return False, errors
        
        # 遍历模块目录
        for module_dir in requirements_path.iterdir():
            if not module_dir.is_dir():
                continue
            
            module_name = module_dir.name
            
            # 遍历版本目录
            for version_dir in module_dir.iterdir():
                if not version_dir.is_dir():
                    continue
                
                version = version_dir.name
                
                # 检查必需文件
                meta_file = version_dir / "meta.yaml"
                requirement_file = version_dir / "requirement.md"
                
                if not meta_file.exists():
                    errors.append(f"警告：缺少文件 requirements/{module_name}/{version}/meta.yaml")
                
                if not requirement_file.exists():
                    errors.append(f"警告：缺少文件 requirements/{module_name}/{version}/requirement.md")
        
        return len(errors) == 0, errors
    
    def validate_module_structure(self, module_name: str, version: str) -> Tuple[bool, List[str]]:
        """
        验证模块目录结构
        
        预期结构：
        .kiro/modules/{module}/{version}/
        ├── README.md              # 模块说明（必需）
        ├── meta.yaml             # 模块元信息（必需）
        ├── config.yaml           # 模块配置（必需）
        ├── steering/             # Steering 规则目录（必需）
        │   └── {module}.md       # Steering 规则文件（必需）
        └── scripts/              # 脚本目录（可选）
        
        Args:
            module_name: 模块名称
            version: 模块版本
        
        Returns:
            (是否通过, 错误信息列表)
        """
        errors = []
        module_path = self.project_root / ".kiro" / "modules" / module_name / version
        
        if not module_path.exists():
            errors.append(f"错误：模块目录不存在 .kiro/modules/{module_name}/{version}/")
            return False, errors
        
        if not module_path.is_dir():
            errors.append(f"错误：.kiro/modules/{module_name}/{version} 不是一个目录")
            return False, errors
        
        # 检查必需文件
        required_files = [
            "README.md",
            "meta.yaml",
            "config.yaml"
        ]
        
        for file_name in required_files:
            file_path = module_path / file_name
            if not file_path.exists():
                errors.append(f"错误：缺少必需文件 .kiro/modules/{module_name}/{version}/{file_name}")
            elif not file_path.is_file():
                errors.append(f"错误：.kiro/modules/{module_name}/{version}/{file_name} 不是一个文件")
        
        # 检查 steering/ 目录
        steering_path = module_path / "steering"
        if not steering_path.exists():
            errors.append(f"错误：缺少必需目录 .kiro/modules/{module_name}/{version}/steering/")
        elif not steering_path.is_dir():
            errors.append(f"错误：.kiro/modules/{module_name}/{version}/steering 不是一个目录")
        else:
            # 检查 Steering 文件
            # workflow 模块使用特殊文件名
            if module_name == "workflow":
                steering_file = steering_path / "workflow_selector.md"
            else:
                steering_file = steering_path / f"{module_name}.md"
            
            if not steering_file.exists():
                errors.append(f"错误：缺少必需文件 {steering_file.relative_to(self.project_root)}")
            elif not steering_file.is_file():
                errors.append(f"错误：{steering_file.relative_to(self.project_root)} 不是一个文件")
        
        return len(errors) == 0, errors
    
    def get_validation_report(self) -> str:
        """
        生成完整的验证报告
        
        Returns:
            格式化的验证报告
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("目录结构验证报告")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # 验证项目结构
        report_lines.append("1. 项目结构验证")
        report_lines.append("-" * 60)
        valid, errors = self.validate_project_structure()
        
        if valid:
            report_lines.append("✓ 项目结构验证通过")
        else:
            report_lines.append("✗ 项目结构验证失败")
            for error in errors:
                report_lines.append(f"  - {error}")
        
        report_lines.append("")
        
        # 验证所有模块
        report_lines.append("2. 模块结构验证")
        report_lines.append("-" * 60)
        
        modules_path = self.project_root / ".kiro" / "modules"
        if modules_path.exists():
            module_count = 0
            valid_count = 0
            
            for module_dir in modules_path.iterdir():
                if not module_dir.is_dir():
                    continue
                
                module_name = module_dir.name
                
                for version_dir in module_dir.iterdir():
                    if not version_dir.is_dir():
                        continue
                    
                    version = version_dir.name
                    module_count += 1
                    
                    valid, errors = self.validate_module_structure(module_name, version)
                    
                    if valid:
                        report_lines.append(f"✓ {module_name}/{version}")
                        valid_count += 1
                    else:
                        report_lines.append(f"✗ {module_name}/{version}")
                        for error in errors:
                            report_lines.append(f"  - {error}")
            
            report_lines.append("")
            report_lines.append(f"模块验证统计：{valid_count}/{module_count} 通过")
        else:
            report_lines.append("警告：.kiro/modules/ 目录不存在")
        
        report_lines.append("")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)


def validate_project_structure(project_root: str = None) -> Tuple[bool, List[str]]:
    """
    验证项目目录结构（便捷函数）
    
    Args:
        project_root: 项目根目录路径
    
    Returns:
        (是否通过, 错误信息列表)
    """
    validator = PathValidator(project_root)
    return validator.validate_project_structure()


def main():
    """主函数：运行验证并输出报告"""
    validator = PathValidator()
    report = validator.get_validation_report()
    print(report)


if __name__ == "__main__":
    main()
