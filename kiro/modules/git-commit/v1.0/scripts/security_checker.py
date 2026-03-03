 """
安全检查模块

负责检测敏感文件、大文件和保护分支，确保提交安全。
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from fnmatch import fnmatch


class SecurityChecker:
    """安全检查器"""
    
    # 默认敏感文件模式
    DEFAULT_SENSITIVE_PATTERNS = [
        "*.env",
        ".env.*",
        "*.pem",
        "*.key",
        "*.p12",
        "*.pfx",
        "*.crt",
        "*.cer",
        "**/config/secrets*",
        "**/config/credentials*",
        "**/token*",
        "**/*secret*",
        "**/*password*",
        "**/*apikey*",
        "*.db",
        "*.sqlite",
        "**/.aws/credentials",
        "**/.ssh/id_*",
    ]
    
    def __init__(self, workspace_root: Optional[str] = None, config: Optional[Dict] = None):
        """
        初始化安全检查器
        
        Args:
            workspace_root: 工作区根目录，默认为当前目录
            config: 配置字典（可选）
        """
        self.workspace_root = Path(workspace_root or os.getcwd())
        self.config = config or {}
        
        # 加载敏感文件模式
        custom_patterns = self.config.get("sensitive_patterns", [])
        self.sensitive_patterns = self.DEFAULT_SENSITIVE_PATTERNS + custom_patterns
        
        # 加载大文件阈值
        self.warn_size_mb = self.config.get("warn_size_mb", 10)
        self.block_size_mb = self.config.get("block_size_mb", 100)
        
        # 加载保护分支列表
        self.protected_branches = self.config.get("protected_branches", ["main", "master", "production"])
    
    def check_sensitive_files(self, files: List[str]) -> Dict[str, List[Dict]]:
        """
        检测敏感文件
        
        Args:
            files: 文件路径列表
            
        Returns:
            检测结果字典，格式：
            {
                "sensitive_files": [
                    {
                        "file": "path/to/file",
                        "matched_pattern": "*.env",
                        "risk_level": "high"
                    },
                    ...
                ]
            }
        """
        sensitive_files = []
        
        for file_path in files:
            matched_pattern = self._match_sensitive_pattern(file_path)
            if matched_pattern:
                sensitive_files.append({
                    "file": file_path,
                    "matched_pattern": matched_pattern,
                    "risk_level": "high"
                })
        
        return {"sensitive_files": sensitive_files}
    
    def _match_sensitive_pattern(self, file_path: str) -> Optional[str]:
        """
        检查文件是否匹配敏感文件模式
        
        Args:
            file_path: 文件路径
            
        Returns:
            匹配的模式，如果不匹配则返回 None
        """
        # 规范化路径（使用正斜杠）
        normalized_path = file_path.replace("\\", "/")
        file_name = os.path.basename(normalized_path)
        
        for pattern in self.sensitive_patterns:
            # 处理 ** 通配符（匹配任意层级目录）
            if pattern.startswith("**/"):
                # **/ 开头的模式，匹配任意路径下的文件
                sub_pattern = pattern[3:]  # 去掉 **/
                
                # 检查文件名是否匹配
                if fnmatch(file_name.lower(), sub_pattern.lower()):
                    return pattern
                
                # 检查路径中任意部分是否匹配
                path_parts = normalized_path.split("/")
                for i in range(len(path_parts)):
                    sub_path = "/".join(path_parts[i:])
                    if fnmatch(sub_path.lower(), sub_pattern.lower()):
                        return pattern
            else:
                # 普通模式，直接匹配完整路径
                if fnmatch(normalized_path.lower(), pattern.lower()):
                    return pattern
                
                # 检查文件名匹配（对于不包含路径的模式）
                if "/" not in pattern and fnmatch(file_name.lower(), pattern.lower()):
                    return pattern
        
        return None

    
    def check_large_files(self, files: List[str]) -> Dict[str, List[Dict]]:
        """
        检测大文件
        
        Args:
            files: 文件路径列表
            
        Returns:
            检测结果字典，格式：
            {
                "large_files": [
                    {
                        "file": "path/to/file",
                        "size_mb": 15.5,
                        "level": "warning"  # "warning" 或 "block"
                    },
                    ...
                ]
            }
        """
        large_files = []
        
        for file_path in files:
            size_mb = self._get_file_size_mb(file_path)
            
            if size_mb is None:
                # 文件不存在或无法读取，跳过
                continue
            
            level = None
            if size_mb >= self.block_size_mb:
                level = "block"
            elif size_mb >= self.warn_size_mb:
                level = "warning"
            
            if level:
                large_files.append({
                    "file": file_path,
                    "size_mb": round(size_mb, 2),
                    "level": level
                })
        
        return {"large_files": large_files}
    
    def _get_file_size_mb(self, file_path: str) -> Optional[float]:
        """
        获取文件大小（MB）
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件大小（MB），如果文件不存在则返回 None
        """
        full_path = self.workspace_root / file_path
        
        if not full_path.exists():
            return None
        
        try:
            size_bytes = full_path.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            return size_mb
        except Exception:
            return None
    
    def check_protected_branch(self) -> Dict[str, any]:
        """
        检测当前分支是否为保护分支
        
        Returns:
            检测结果字典，格式：
            {
                "is_protected": True/False,
                "current_branch": "main",
                "protected_branches": ["main", "master", "production"]
            }
        """
        current_branch = self._get_current_branch()
        is_protected = current_branch in self.protected_branches if current_branch else False
        
        return {
            "is_protected": is_protected,
            "current_branch": current_branch,
            "protected_branches": self.protected_branches
        }
    
    def _get_current_branch(self) -> Optional[str]:
        """
        获取当前 Git 分支名称
        
        Returns:
            分支名称，如果获取失败则返回 None
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                check=True
            )
            branch_name = result.stdout.strip()
            return branch_name if branch_name else None
        except Exception:
            return None
    
    def check_all(self, files: List[str]) -> Dict[str, any]:
        """
        执行所有安全检查
        
        Args:
            files: 文件路径列表
            
        Returns:
            所有检查结果的汇总字典
        """
        results = {}
        
        # 敏感文件检测
        sensitive_result = self.check_sensitive_files(files)
        results.update(sensitive_result)
        
        # 大文件检测
        large_file_result = self.check_large_files(files)
        results.update(large_file_result)
        
        # 保护分支检测
        branch_result = self.check_protected_branch()
        results.update(branch_result)
        
        return results
    
    def has_blocking_issues(self, check_results: Dict[str, any]) -> Tuple[bool, List[str]]:
        """
        检查是否有阻止性问题
        
        Args:
            check_results: 检查结果字典（来自 check_all）
            
        Returns:
            (是否有阻止性问题, 问题描述列表)
        """
        blocking_issues = []
        
        # 检查是否有阻止级别的大文件
        large_files = check_results.get("large_files", [])
        for file_info in large_files:
            if file_info["level"] == "block":
                blocking_issues.append(
                    f"文件 {file_info['file']} 过大 ({file_info['size_mb']} MB)，"
                    f"超过阻止阈值 {self.block_size_mb} MB"
                )
        
        return len(blocking_issues) > 0, blocking_issues
    
    def has_warnings(self, check_results: Dict[str, any]) -> Tuple[bool, List[str]]:
        """
        检查是否有警告
        
        Args:
            check_results: 检查结果字典（来自 check_all）
            
        Returns:
            (是否有警告, 警告描述列表)
        """
        warnings = []
        
        # 检查敏感文件
        sensitive_files = check_results.get("sensitive_files", [])
        if sensitive_files:
            warnings.append(f"检测到 {len(sensitive_files)} 个敏感文件")
        
        # 检查警告级别的大文件
        large_files = check_results.get("large_files", [])
        warning_files = [f for f in large_files if f["level"] == "warning"]
        if warning_files:
            warnings.append(f"检测到 {len(warning_files)} 个大文件")
        
        # 检查保护分支
        if check_results.get("is_protected", False):
            branch = check_results.get("current_branch", "unknown")
            warnings.append(f"当前分支 '{branch}' 是保护分支")
        
        return len(warnings) > 0, warnings
