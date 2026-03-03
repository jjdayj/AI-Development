"""
环境初始化综合测试

测试内容：
1. 目录结构创建
2. 备份机制的正确性
3. 回滚机制的正确性
"""

import sys
import tempfile
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from path_validator import PathValidator
from backup_manager import BackupManager


class TestEnvironmentInit:
    """环境初始化测试类"""
    
    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0
    
    def test_project_directory_structure(self):
        """测试项目目录结构"""
        print("=" * 60)
        print("测试 1: 项目目录结构验证")
        print("=" * 60)
        
        validator = PathValidator()
        
        # 检查 .kiro/ 目录
        kiro_path = validator.project_root / ".kiro"
        if kiro_path.exists():
            print(f"✓ .kiro/ 目录存在: {kiro_path}")
            self.passed += 1
        else:
            print(f"✗ .kiro/ 目录不存在: {kiro_path}")
            self.failed += 1
            return False
        
        # 检查必需的子目录
        required_dirs = ["steering", "modules", "specs"]
        for dir_name in required_dirs:
            dir_path = kiro_path / dir_name
            if dir_path.exists():
                print(f"✓ {dir_name}/ 目录存在")
                self.passed += 1
            else:
                print(f"✗ {dir_name}/ 目录不存在")
                self.failed += 1
        
        # 检查必需的文件
        config_file = kiro_path / "config.yaml"
        if config_file.exists():
            print(f"✓ config.yaml 文件存在")
            self.passed += 1
        else:
            print(f"✗ config.yaml 文件不存在")
            self.failed += 1
        
        main_md = kiro_path / "steering" / "main.md"
        if main_md.exists():
            print(f"✓ steering/main.md 文件存在")
            self.passed += 1
        else:
            print(f"✗ steering/main.md 文件不存在")
            self.failed += 1
        
        print()
        return True
    
    def test_backup_mechanism(self):
        """测试备份机制"""
        print("=" * 60)
        print("测试 2: 备份机制验证")
        print("=" * 60)
        
        manager = BackupManager()
        
        # 测试 1: 备份单个文件
        print("\n2.1 测试文件备份")
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
            test_file = Path(f.name)
            original_content = "原始内容\n测试数据\n"
            f.write(original_content)
        
        try:
            success, backup_path, error = manager.backup_file(str(test_file))
            
            if success:
                print(f"✓ 文件备份成功")
                print(f"  原始文件: {test_file.name}")
                print(f"  备份路径: {Path(backup_path).name}")
                self.passed += 1
                
                # 验证备份文件存在
                if Path(backup_path).exists():
                    print(f"✓ 备份文件存在")
                    self.passed += 1
                else:
                    print(f"✗ 备份文件不存在")
                    self.failed += 1
            else:
                print(f"✗ 文件备份失败: {error}")
                self.failed += 1
        finally:
            if test_file.exists():
                test_file.unlink()
        
        # 测试 2: 备份目录
        print("\n2.2 测试目录备份")
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir)
            
            # 创建测试文件
            (test_dir / "file1.txt").write_text("文件1")
            (test_dir / "file2.txt").write_text("文件2")
            
            subdir = test_dir / "subdir"
            subdir.mkdir()
            (subdir / "file3.txt").write_text("文件3")
            
            success, backup_path, error = manager.backup_directory(str(test_dir))
            
            if success:
                print(f"✓ 目录备份成功")
                print(f"  原始目录: {test_dir.name}")
                print(f"  备份路径: {Path(backup_path).name}")
                self.passed += 1
                
                # 验证备份目录结构
                backup_dir = Path(backup_path)
                if (backup_dir / "file1.txt").exists():
                    print(f"✓ 备份包含 file1.txt")
                    self.passed += 1
                else:
                    print(f"✗ 备份缺少 file1.txt")
                    self.failed += 1
                
                if (backup_dir / "subdir" / "file3.txt").exists():
                    print(f"✓ 备份包含子目录文件")
                    self.passed += 1
                else:
                    print(f"✗ 备份缺少子目录文件")
                    self.failed += 1
            else:
                print(f"✗ 目录备份失败: {error}")
                self.failed += 1
        
        print()
        return True
    
    def test_rollback_mechanism(self):
        """测试回滚机制"""
        print("=" * 60)
        print("测试 3: 回滚机制验证")
        print("=" * 60)
        
        manager = BackupManager()
        
        # 创建测试文件
        print("\n3.1 准备测试环境")
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
            test_file = Path(f.name)
            original_content = "原始版本\n"
            f.write(original_content)
        
        print(f"✓ 创建测试文件: {test_file.name}")
        
        try:
            # 备份原始文件
            print("\n3.2 备份原始文件")
            success, backup_path, error = manager.backup_file(str(test_file))
            
            if not success:
                print(f"✗ 备份失败: {error}")
                self.failed += 1
                return False
            
            print(f"✓ 备份成功: {Path(backup_path).name}")
            self.passed += 1
            
            # 修改文件
            print("\n3.3 修改文件内容")
            modified_content = "修改后的版本\n"
            test_file.write_text(modified_content, encoding='utf-8')
            
            current_content = test_file.read_text(encoding='utf-8')
            if current_content == modified_content:
                print(f"✓ 文件已修改")
                self.passed += 1
            else:
                print(f"✗ 文件修改失败")
                self.failed += 1
                return False
            
            # 回滚到备份
            print("\n3.4 回滚到备份版本")
            success, error = manager.rollback(backup_path, str(test_file))
            
            if not success:
                print(f"✗ 回滚失败: {error}")
                self.failed += 1
                return False
            
            print(f"✓ 回滚成功")
            self.passed += 1
            
            # 验证内容已恢复
            print("\n3.5 验证内容已恢复")
            restored_content = test_file.read_text(encoding='utf-8')
            
            if restored_content == original_content:
                print(f"✓ 内容已恢复到原始版本")
                print(f"  原始: {original_content.strip()}")
                print(f"  恢复: {restored_content.strip()}")
                self.passed += 1
            else:
                print(f"✗ 内容恢复失败")
                print(f"  期望: {original_content.strip()}")
                print(f"  实际: {restored_content.strip()}")
                self.failed += 1
        
        finally:
            if test_file.exists():
                test_file.unlink()
        
        print()
        return True
    
    def test_backup_cleanup(self):
        """测试备份清理功能"""
        print("=" * 60)
        print("测试 4: 备份清理机制验证")
        print("=" * 60)
        
        manager = BackupManager()
        
        # 列出当前备份
        print("\n4.1 列出当前备份")
        backups_before = manager.list_backups()
        print(f"✓ 当前备份数量: {len(backups_before)}")
        self.passed += 1
        
        # 创建一些测试备份
        print("\n4.2 创建测试备份")
        test_backups = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
                test_file = Path(f.name)
                f.write(f"测试备份 {i}\n")
            
            success, backup_path, error = manager.backup_file(str(test_file))
            if success:
                test_backups.append(backup_path)
                print(f"✓ 创建测试备份 {i+1}")
                self.passed += 1
            
            test_file.unlink()
        
        # 列出新的备份数量
        print("\n4.3 验证备份数量增加")
        backups_after = manager.list_backups()
        print(f"✓ 新的备份数量: {len(backups_after)}")
        
        if len(backups_after) >= len(backups_before) + 3:
            print(f"✓ 备份数量正确增加")
            self.passed += 1
        else:
            print(f"✗ 备份数量不正确")
            self.failed += 1
        
        print()
        return True
    
    def test_integration(self):
        """集成测试：完整的备份-修改-回滚流程"""
        print("=" * 60)
        print("测试 5: 集成测试（完整流程）")
        print("=" * 60)
        
        manager = BackupManager()
        
        print("\n5.1 创建测试文件")
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.txt') as f:
            test_file = Path(f.name)
            version1 = "版本 1\n"
            f.write(version1)
        
        print(f"✓ 创建文件: {test_file.name}")
        self.passed += 1
        
        try:
            # 第一次备份
            print("\n5.2 第一次备份")
            success1, backup1, error1 = manager.backup_file(str(test_file), "version1.bak")
            if success1:
                print(f"✓ 第一次备份成功")
                self.passed += 1
            else:
                print(f"✗ 第一次备份失败: {error1}")
                self.failed += 1
                return False
            
            # 修改文件
            print("\n5.3 修改为版本 2")
            version2 = "版本 2\n"
            test_file.write_text(version2, encoding='utf-8')
            print(f"✓ 文件已修改")
            self.passed += 1
            
            # 第二次备份
            print("\n5.4 第二次备份")
            success2, backup2, error2 = manager.backup_file(str(test_file), "version2.bak")
            if success2:
                print(f"✓ 第二次备份成功")
                self.passed += 1
            else:
                print(f"✗ 第二次备份失败: {error2}")
                self.failed += 1
                return False
            
            # 再次修改文件
            print("\n5.5 修改为版本 3")
            version3 = "版本 3\n"
            test_file.write_text(version3, encoding='utf-8')
            print(f"✓ 文件已修改")
            self.passed += 1
            
            # 回滚到版本 1
            print("\n5.6 回滚到版本 1")
            success, error = manager.rollback(backup1, str(test_file))
            if success:
                content = test_file.read_text(encoding='utf-8')
                if content == version1:
                    print(f"✓ 成功回滚到版本 1")
                    self.passed += 1
                else:
                    print(f"✗ 回滚内容不正确")
                    self.failed += 1
            else:
                print(f"✗ 回滚失败: {error}")
                self.failed += 1
        
        finally:
            if test_file.exists():
                test_file.unlink()
        
        print()
        return True
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 60)
        print("环境初始化综合测试")
        print("=" * 60)
        print()
        
        # 运行所有测试
        self.test_project_directory_structure()
        self.test_backup_mechanism()
        self.test_rollback_mechanism()
        self.test_backup_cleanup()
        self.test_integration()
        
        # 输出测试结果
        print("=" * 60)
        print("测试结果汇总")
        print("=" * 60)
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        print(f"总计: {self.passed + self.failed}")
        print(f"通过率: {self.passed / (self.passed + self.failed) * 100:.1f}%")
        print("=" * 60)
        
        return self.failed == 0


def main():
    """主函数"""
    tester = TestEnvironmentInit()
    success = tester.run_all_tests()
    
    if success:
        print("\n✓ 所有环境初始化测试通过！")
        return 0
    else:
        print(f"\n✗ 有 {tester.failed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit(main())
