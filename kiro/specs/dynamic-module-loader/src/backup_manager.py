"""
文件备份与回滚管理器

功能：
1. 备份单个文件
2. 备份整个目录
3. 回滚到备份
4. 清理旧备份
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple


class BackupManager:
    """文件备份与回滚管理器"""
    
    def __init__(self, backup_root: str = None):
        """
        初始化备份管理器
        
        Args:
            backup_root: 备份根目录，默认为项目根目录下的 .backups/
        """
        if backup_root is None:
            # 默认备份目录在项目根目录下
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent.parent
            self.backup_root = project_root / ".backups"
        else:
            self.backup_root = Path(backup_root).resolve()
        
        # 确保备份目录存在
        self.backup_root.mkdir(parents=True, exist_ok=True)
    
    def backup_file(self, file_path: str, backup_name: str = None) -> Tuple[bool, str, str]:
        """
        备份单个文件
        
        Args:
            file_path: 要备份的文件路径
            backup_name: 备份名称（可选），默认使用时间戳
        
        Returns:
            (是否成功, 备份路径, 错误信息)
        """
        source_path = Path(file_path).resolve()
        
        # 检查文件是否存在
        if not source_path.exists():
            return False, "", f"文件不存在: {file_path}"
        
        if not source_path.is_file():
            return False, "", f"不是一个文件: {file_path}"
        
        # 生成备份名称
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_path.name}.{timestamp}.bak"
        
        # 创建备份目录结构（保持原始目录层级）
        relative_path = self._get_relative_path(source_path)
        backup_dir = self.backup_root / relative_path.parent
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 备份文件路径
        backup_path = backup_dir / backup_name
        
        try:
            # 复制文件
            shutil.copy2(source_path, backup_path)
            return True, str(backup_path), ""
        except Exception as e:
            return False, "", f"备份失败: {str(e)}"
    
    def backup_directory(self, dir_path: str, backup_name: str = None) -> Tuple[bool, str, str]:
        """
        备份整个目录
        
        Args:
            dir_path: 要备份的目录路径
            backup_name: 备份名称（可选），默认使用时间戳
        
        Returns:
            (是否成功, 备份路径, 错误信息)
        """
        source_path = Path(dir_path).resolve()
        
        # 检查目录是否存在
        if not source_path.exists():
            return False, "", f"目录不存在: {dir_path}"
        
        if not source_path.is_dir():
            return False, "", f"不是一个目录: {dir_path}"
        
        # 生成备份名称
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{source_path.name}.{timestamp}.bak"
        
        # 创建备份目录
        relative_path = self._get_relative_path(source_path)
        backup_dir = self.backup_root / relative_path.parent
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 备份目录路径
        backup_path = backup_dir / backup_name
        
        try:
            # 复制整个目录树
            shutil.copytree(source_path, backup_path)
            return True, str(backup_path), ""
        except Exception as e:
            return False, "", f"备份失败: {str(e)}"
    
    def rollback(self, backup_path: str, target_path: str = None) -> Tuple[bool, str]:
        """
        从备份恢复文件或目录
        
        Args:
            backup_path: 备份文件/目录的路径
            target_path: 恢复目标路径（可选），默认恢复到原始位置
        
        Returns:
            (是否成功, 错误信息)
        """
        backup_source = Path(backup_path).resolve()
        
        # 检查备份是否存在
        if not backup_source.exists():
            return False, f"备份不存在: {backup_path}"
        
        # 确定目标路径
        if target_path is None:
            # 从备份路径推断原始路径
            target_path = self._infer_original_path(backup_source)
            if target_path is None:
                return False, "无法推断原始路径，请指定 target_path"
        
        target = Path(target_path).resolve()
        
        try:
            # 如果目标已存在，先备份当前版本
            if target.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pre_rollback_backup = f"{target.name}.pre_rollback.{timestamp}.bak"
                
                if target.is_file():
                    self.backup_file(str(target), pre_rollback_backup)
                else:
                    self.backup_directory(str(target), pre_rollback_backup)
                
                # 删除当前版本
                if target.is_file():
                    target.unlink()
                else:
                    shutil.rmtree(target)
            
            # 恢复备份
            if backup_source.is_file():
                # 确保目标目录存在
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_source, target)
            else:
                shutil.copytree(backup_source, target)
            
            return True, ""
        except Exception as e:
            return False, f"回滚失败: {str(e)}"
    
    def cleanup_backups(self, keep_count: int = 5, older_than_days: int = None) -> Tuple[int, List[str]]:
        """
        清理旧备份
        
        Args:
            keep_count: 保留最新的 N 个备份（默认 5 个）
            older_than_days: 删除超过 N 天的备份（可选）
        
        Returns:
            (删除的备份数量, 删除的备份路径列表)
        """
        deleted_count = 0
        deleted_paths = []
        
        if not self.backup_root.exists():
            return 0, []
        
        # 收集所有备份文件
        backups = []
        for backup_file in self.backup_root.rglob("*.bak"):
            if backup_file.is_file():
                backups.append(backup_file)
            elif backup_file.is_dir():
                backups.append(backup_file)
        
        # 按修改时间排序（最新的在前）
        backups.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        
        # 按时间删除
        if older_than_days is not None:
            cutoff_time = datetime.now().timestamp() - (older_than_days * 24 * 60 * 60)
            
            for backup in backups:
                if backup.stat().st_mtime < cutoff_time:
                    try:
                        if backup.is_file():
                            backup.unlink()
                        else:
                            shutil.rmtree(backup)
                        deleted_count += 1
                        deleted_paths.append(str(backup))
                    except Exception as e:
                        print(f"删除备份失败: {backup}, 错误: {e}")
        
        # 按数量删除（保留最新的 keep_count 个）
        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                if backup.exists():  # 可能已经被时间规则删除
                    try:
                        if backup.is_file():
                            backup.unlink()
                        else:
                            shutil.rmtree(backup)
                        deleted_count += 1
                        if str(backup) not in deleted_paths:
                            deleted_paths.append(str(backup))
                    except Exception as e:
                        print(f"删除备份失败: {backup}, 错误: {e}")
        
        return deleted_count, deleted_paths
    
    def list_backups(self, pattern: str = None) -> List[dict]:
        """
        列出所有备份
        
        Args:
            pattern: 文件名模式（可选），用于过滤备份
        
        Returns:
            备份信息列表，每个元素包含：
            - path: 备份路径
            - name: 备份名称
            - size: 文件大小（字节）
            - mtime: 修改时间
            - is_dir: 是否为目录
        """
        backups = []
        
        if not self.backup_root.exists():
            return []
        
        for backup_path in self.backup_root.rglob("*.bak"):
            # 应用模式过滤
            if pattern and pattern not in backup_path.name:
                continue
            
            stat = backup_path.stat()
            
            backups.append({
                "path": str(backup_path),
                "name": backup_path.name,
                "size": stat.st_size if backup_path.is_file() else self._get_dir_size(backup_path),
                "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "is_dir": backup_path.is_dir()
            })
        
        # 按修改时间排序（最新的在前）
        backups.sort(key=lambda b: b["mtime"], reverse=True)
        
        return backups
    
    def _get_relative_path(self, path: Path) -> Path:
        """
        获取相对于项目根目录的路径
        
        Args:
            path: 绝对路径
        
        Returns:
            相对路径
        """
        project_root = self.backup_root.parent
        try:
            return path.relative_to(project_root)
        except ValueError:
            # 如果路径不在项目根目录下，使用绝对路径的最后几级
            return Path(*path.parts[-3:])
    
    def _infer_original_path(self, backup_path: Path) -> Optional[Path]:
        """
        从备份路径推断原始文件路径
        
        Args:
            backup_path: 备份文件路径
        
        Returns:
            原始文件路径，如果无法推断则返回 None
        """
        # 移除 .bak 扩展名和时间戳
        name = backup_path.name
        
        # 移除 .bak 后缀
        if name.endswith(".bak"):
            name = name[:-4]
        
        # 移除时间戳（格式：.YYYYMMDD_HHMMSS）
        parts = name.split(".")
        if len(parts) >= 2:
            # 检查倒数第二个部分是否为时间戳
            timestamp_part = parts[-1]
            if len(timestamp_part) == 15 and "_" in timestamp_part:
                name = ".".join(parts[:-1])
        
        # 移除 .pre_rollback 标记
        if ".pre_rollback." in name:
            name = name.split(".pre_rollback.")[0]
        
        # 构建原始路径
        project_root = self.backup_root.parent
        relative_path = backup_path.relative_to(self.backup_root)
        original_path = project_root / relative_path.parent / name
        
        return original_path
    
    def _get_dir_size(self, path: Path) -> int:
        """
        计算目录大小
        
        Args:
            path: 目录路径
        
        Returns:
            目录大小（字节）
        """
        total_size = 0
        for item in path.rglob("*"):
            if item.is_file():
                total_size += item.stat().st_size
        return total_size


# 便捷函数

def backup_file(file_path: str, backup_name: str = None) -> Tuple[bool, str, str]:
    """
    备份单个文件（便捷函数）
    
    Args:
        file_path: 要备份的文件路径
        backup_name: 备份名称（可选）
    
    Returns:
        (是否成功, 备份路径, 错误信息)
    """
    manager = BackupManager()
    return manager.backup_file(file_path, backup_name)


def backup_directory(dir_path: str, backup_name: str = None) -> Tuple[bool, str, str]:
    """
    备份整个目录（便捷函数）
    
    Args:
        dir_path: 要备份的目录路径
        backup_name: 备份名称（可选）
    
    Returns:
        (是否成功, 备份路径, 错误信息)
    """
    manager = BackupManager()
    return manager.backup_directory(dir_path, backup_name)


def rollback(backup_path: str, target_path: str = None) -> Tuple[bool, str]:
    """
    从备份恢复（便捷函数）
    
    Args:
        backup_path: 备份路径
        target_path: 恢复目标路径（可选）
    
    Returns:
        (是否成功, 错误信息)
    """
    manager = BackupManager()
    return manager.rollback(backup_path, target_path)


def cleanup_backups(keep_count: int = 5, older_than_days: int = None) -> Tuple[int, List[str]]:
    """
    清理旧备份（便捷函数）
    
    Args:
        keep_count: 保留最新的 N 个备份
        older_than_days: 删除超过 N 天的备份
    
    Returns:
        (删除的备份数量, 删除的备份路径列表)
    """
    manager = BackupManager()
    return manager.cleanup_backups(keep_count, older_than_days)


def main():
    """主函数：演示备份管理器的使用"""
    manager = BackupManager()
    
    print("=" * 60)
    print("备份管理器")
    print("=" * 60)
    print()
    
    # 列出所有备份
    print("当前备份列表：")
    print("-" * 60)
    backups = manager.list_backups()
    
    if not backups:
        print("没有找到备份文件")
    else:
        for backup in backups:
            size_mb = backup["size"] / (1024 * 1024)
            type_str = "目录" if backup["is_dir"] else "文件"
            print(f"[{type_str}] {backup['name']}")
            print(f"  路径: {backup['path']}")
            print(f"  大小: {size_mb:.2f} MB")
            print(f"  时间: {backup['mtime']}")
            print()
    
    print("=" * 60)


if __name__ == "__main__":
    main()
