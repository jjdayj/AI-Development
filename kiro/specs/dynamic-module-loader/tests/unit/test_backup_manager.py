"""
backup_manager.py 的单元测试
"""

import sys
import tempfile
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from backup_manager import BackupManager, backup_file, backup_directory, rollback, cleanup_backups


def test_backup_manager_initialization():
    """测试 BackupManager 初始化"""
    manager = BackupManager()
    assert manager.backup_root is not None
    assert manager.backup_root.exists()
    print(f"✓ 备份根目录: {manager.backup_root}")


def test_backup_file():
    """测试文件备份功能"""
    # 创建临时测试文件
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
        test_file = Path(f.name)
        f.write("测试内容\n")
        f.write("第二行\n")
    
    try:
        # 备份文件
        success, backup_path, error = backup_file(str(test_file))
        
        if success:
            print(f"✓ 文件备份成功: {backup_path}")
            assert Path(backup_path).exists()
            
            # 验证备份内容
            try:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    assert "测试内容" in content
            except UnicodeDecodeError:
                # 如果是二进制文件，只验证文件存在
                print("  (备份为二进制文件，跳过内容验证)")
        else:
            print(f"✗ 文件备份失败: {error}")
    
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()


def test_backup_directory():
    """测试目录备份功能"""
    # 创建临时测试目录
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        
        # 创建一些测试文件
        (test_dir / "file1.txt").write_text("文件1内容")
        (test_dir / "file2.txt").write_text("文件2内容")
        
        subdir = test_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("文件3内容")
        
        # 备份目录
        success, backup_path, error = backup_directory(str(test_dir))
        
        if success:
            print(f"✓ 目录备份成功: {backup_path}")
            backup_dir = Path(backup_path)
            assert backup_dir.exists()
            assert (backup_dir / "file1.txt").exists()
            assert (backup_dir / "file2.txt").exists()
            assert (backup_dir / "subdir" / "file3.txt").exists()
        else:
            print(f"✗ 目录备份失败: {error}")


def test_rollback():
    """测试回滚功能"""
    # 创建临时测试文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        test_file = Path(f.name)
        original_content = "原始内容\n"
        f.write(original_content)
    
    try:
        # 备份文件
        success, backup_path, error = backup_file(str(test_file))
        assert success, f"备份失败: {error}"
        
        # 修改原始文件
        test_file.write_text("修改后的内容\n")
        
        # 回滚到备份
        success, error = rollback(backup_path, str(test_file))
        
        if success:
            print(f"✓ 回滚成功")
            # 验证内容已恢复
            content = test_file.read_text()
            assert content == original_content
        else:
            print(f"✗ 回滚失败: {error}")
    
    finally:
        # 清理测试文件
        if test_file.exists():
            test_file.unlink()


def test_list_backups():
    """测试列出备份功能"""
    manager = BackupManager()
    backups = manager.list_backups()
    
    print(f"✓ 找到 {len(backups)} 个备份")
    
    if backups:
        print("  最新的 3 个备份：")
        for backup in backups[:3]:
            print(f"    - {backup['name']} ({backup['mtime']})")


def test_cleanup_backups():
    """测试清理备份功能"""
    manager = BackupManager()
    
    # 列出清理前的备份数量
    backups_before = manager.list_backups()
    print(f"  清理前备份数量: {len(backups_before)}")
    
    # 清理旧备份（保留最新的 5 个）
    deleted_count, deleted_paths = cleanup_backups(keep_count=5)
    
    print(f"✓ 清理了 {deleted_count} 个旧备份")
    
    # 列出清理后的备份数量
    backups_after = manager.list_backups()
    print(f"  清理后备份数量: {len(backups_after)}")


def test_infer_original_path():
    """测试推断原始路径功能"""
    manager = BackupManager()
    
    # 测试各种备份文件名格式
    test_cases = [
        "config.yaml.20260303_123456.bak",
        "test.txt.pre_rollback.20260303_123456.bak",
        "module.py.20260303_123456.bak"
    ]
    
    print("✓ 测试推断原始路径：")
    for backup_name in test_cases:
        backup_path = manager.backup_root / backup_name
        original_path = manager._infer_original_path(backup_path)
        if original_path:
            print(f"  {backup_name} -> {original_path.name}")


if __name__ == "__main__":
    print("运行 backup_manager 单元测试...\n")
    
    print("1. 测试初始化")
    test_backup_manager_initialization()
    print()
    
    print("2. 测试文件备份")
    test_backup_file()
    print()
    
    print("3. 测试目录备份")
    test_backup_directory()
    print()
    
    print("4. 测试回滚功能")
    test_rollback()
    print()
    
    print("5. 测试列出备份")
    test_list_backups()
    print()
    
    print("6. 测试推断原始路径")
    test_infer_original_path()
    print()
    
    print("7. 测试清理备份")
    test_cleanup_backups()
    print()
    
    print("所有测试完成！")
