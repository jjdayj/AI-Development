"""
路径匹配器单元测试

测试 path_matcher.py 模块的所有功能：
- match_directory() - 目录路径匹配
- match_file_type() - 文件类型匹配
- match_pattern() - 通用模式匹配
- normalize_path() - 路径规范化

作者: yangzhuo
日期: 2026-03-03
版本: v1.0
"""

import sys
import os
import pytest

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from path_matcher import match_directory, match_file_type, match_pattern, normalize_path


class TestMatchDirectory:
    """测试 match_directory() 函数"""
    
    def test_single_pattern_match_success(self):
        """测试：单个模式匹配成功"""
        assert match_directory('.kiro/steering/main.md', '.kiro/steering/*') == True
    
    def test_single_pattern_match_failure(self):
        """测试：单个模式匹配失败"""
        assert match_directory('.kiro/steering/main.md', '.kiro/modules/*') == False
    
    def test_multiple_patterns_any_match(self):
        """测试：多个模式，任一匹配成功"""
        patterns = ['.kiro/modules/*', '.kiro/steering/*']
        assert match_directory('.kiro/steering/main.md', patterns) == True
    
    def test_multiple_patterns_no_match(self):
        """测试：多个模式，全不匹配"""
        patterns = ['.kiro/modules/*', 'doc/project/*']
        assert match_directory('.kiro/steering/main.md', patterns) == False
    
    def test_wildcard_multilevel_path(self):
        """测试：通配符匹配多层路径"""
        path = '.kiro/modules/workflow/v1.0/steering/workflow_selector.md'
        assert match_directory(path, '.kiro/modules/*') == True
    
    def test_exact_match_no_wildcard(self):
        """测试：精确匹配（无通配符）"""
        assert match_directory('.kiro/steering', '.kiro/steering') == True
    
    def test_wildcard_in_middle(self):
        """测试：通配符在中间"""
        assert match_directory('.kiro/modules/workflow/v1.0', '.kiro/*/workflow/*') == True
    
    def test_wildcard_at_beginning(self):
        """测试：通配符在开头"""
        assert match_directory('.kiro/steering/main.md', '*/main.md') == True
    
    def test_empty_path(self):
        """测试：空路径"""
        assert match_directory('', '.kiro/*') == False
    
    def test_empty_pattern_list(self):
        """测试：空模式列表"""
        assert match_directory('.kiro/steering', []) == False
    
    def test_special_characters_in_path(self):
        """测试：路径中包含特殊字符"""
        assert match_directory('.kiro/test-file_v1.0.md', '.kiro/*') == True


class TestMatchFileType:
    """测试 match_file_type() 函数"""
    
    def test_single_extension_match_success(self):
        """测试：单个扩展名匹配成功"""
        assert match_file_type('.md', '.md') == True
    
    def test_single_extension_match_failure(self):
        """测试：单个扩展名匹配失败"""
        assert match_file_type('.md', '.yaml') == False
    
    def test_multiple_extensions_any_match(self):
        """测试：多个扩展名，任一匹配成功"""
        extensions = ['.md', '.yaml', '.json']
        assert match_file_type('.md', extensions) == True
    
    def test_multiple_extensions_no_match(self):
        """测试：多个扩展名，全不匹配"""
        extensions = ['.yaml', '.json', '.txt']
        assert match_file_type('.md', extensions) == False
    
    def test_full_file_path_match(self):
        """测试：完整文件路径匹配"""
        assert match_file_type('config.yaml', '.yaml') == True
    
    def test_full_file_path_multilevel(self):
        """测试：多层文件路径匹配"""
        assert match_file_type('.kiro/steering/main.md', '.md') == True
    
    def test_full_file_path_no_match(self):
        """测试：完整文件路径不匹配"""
        assert match_file_type('.kiro/steering/main.md', '.yaml') == False
    
    def test_extension_only(self):
        """测试：仅扩展名（以 . 开头）"""
        assert match_file_type('.md', '.md') == True
    
    def test_empty_file_path(self):
        """测试：空文件路径"""
        assert match_file_type('', '.md') == False
    
    def test_empty_extension_list(self):
        """测试：空扩展名列表"""
        assert match_file_type('.md', []) == False
    
    def test_case_sensitive(self):
        """测试：大小写敏感"""
        assert match_file_type('.MD', '.md') == False
        assert match_file_type('.md', '.MD') == False


class TestMatchPattern:
    """测试 match_pattern() 函数"""
    
    def test_single_level_wildcard(self):
        """测试：单层通配符"""
        assert match_pattern('.kiro/steering', '.kiro/*') == True
    
    def test_multilevel_wildcard(self):
        """测试：多层通配符"""
        assert match_pattern('.kiro/modules/workflow/v1.0', '.kiro/modules/*') == True
    
    def test_no_match(self):
        """测试：不匹配"""
        assert match_pattern('src/main.py', '.kiro/*') == False
    
    def test_exact_match(self):
        """测试：精确匹配"""
        assert match_pattern('.kiro/config.yaml', '.kiro/config.yaml') == True
    
    def test_wildcard_in_middle(self):
        """测试：通配符在中间"""
        assert match_pattern('.kiro/modules/workflow/v1.0', '.kiro/*/workflow/*') == True
    
    def test_wildcard_at_beginning(self):
        """测试：通配符在开头"""
        assert match_pattern('.kiro/steering/main.md', '*/main.md') == True
    
    def test_wildcard_at_end(self):
        """测试：通配符在结尾"""
        assert match_pattern('.kiro/steering/main.md', '.kiro/steering/*') == True
    
    def test_multiple_wildcards(self):
        """测试：多个通配符"""
        assert match_pattern('.kiro/modules/workflow/v1.0', '.kiro/*/workflow/*') == True
    
    def test_question_mark_wildcard(self):
        """测试：问号通配符（匹配单个字符）"""
        assert match_pattern('.kiro/test1.md', '.kiro/test?.md') == True
        assert match_pattern('.kiro/test12.md', '.kiro/test?.md') == False
    
    def test_character_class(self):
        """测试：字符类 [abc]"""
        assert match_pattern('.kiro/test1.md', '.kiro/test[123].md') == True
        assert match_pattern('.kiro/test4.md', '.kiro/test[123].md') == False
    
    def test_empty_path(self):
        """测试：空路径"""
        assert match_pattern('', '.kiro/*') == False
    
    def test_empty_pattern(self):
        """测试：空模式"""
        assert match_pattern('.kiro/steering', '') == False


class TestNormalizePath:
    """测试 normalize_path() 函数"""
    
    def test_windows_path_to_unix(self):
        """测试：Windows 路径转换为 Unix 路径"""
        assert normalize_path('.kiro\\steering\\main.md') == '.kiro/steering/main.md'
    
    def test_unix_path_unchanged(self):
        """测试：Unix 路径保持不变"""
        assert normalize_path('.kiro/steering/main.md') == '.kiro/steering/main.md'
    
    def test_mixed_separators(self):
        """测试：混合路径分隔符"""
        assert normalize_path('.kiro\\modules/workflow\\v1.0') == '.kiro/modules/workflow/v1.0'
    
    def test_empty_path(self):
        """测试：空路径"""
        assert normalize_path('') == ''
    
    def test_single_backslash(self):
        """测试：单个反斜杠"""
        assert normalize_path('\\') == '/'
    
    def test_single_forward_slash(self):
        """测试：单个正斜杠"""
        assert normalize_path('/') == '/'
    
    def test_multiple_consecutive_backslashes(self):
        """测试：多个连续反斜杠"""
        assert normalize_path('.kiro\\\\steering') == '.kiro//steering'
    
    def test_absolute_windows_path(self):
        """测试：Windows 绝对路径"""
        assert normalize_path('C:\\Users\\test\\file.txt') == 'C:/Users/test/file.txt'
    
    def test_absolute_unix_path(self):
        """测试：Unix 绝对路径"""
        assert normalize_path('/home/user/file.txt') == '/home/user/file.txt'


class TestEdgeCases:
    """测试边界情况"""
    
    def test_match_directory_with_string_pattern(self):
        """测试：match_directory 接受字符串模式"""
        assert match_directory('.kiro/steering', '.kiro/*') == True
    
    def test_match_directory_with_list_pattern(self):
        """测试：match_directory 接受列表模式"""
        assert match_directory('.kiro/steering', ['.kiro/*']) == True
    
    def test_match_file_type_with_string_extension(self):
        """测试：match_file_type 接受字符串扩展名"""
        assert match_file_type('.md', '.md') == True
    
    def test_match_file_type_with_list_extension(self):
        """测试：match_file_type 接受列表扩展名"""
        assert match_file_type('.md', ['.md']) == True
    
    def test_very_long_path(self):
        """测试：非常长的路径"""
        long_path = '/'.join(['dir'] * 100) + '/file.txt'
        pattern = '/'.join(['dir'] * 100) + '/*'
        assert match_pattern(long_path, pattern) == True
    
    def test_special_regex_characters_in_path(self):
        """测试：路径中包含特殊字符（fnmatch 的字符类）"""
        # fnmatch 将 [1] 视为字符类，匹配 '1'
        assert match_pattern('.kiro/test1.md', '.kiro/test[1].md') == True
        # 如果需要匹配字面的 '[1]'，需要转义，但 fnmatch 不支持转义
        # 这是 fnmatch 的已知限制
    
    def test_unicode_characters_in_path(self):
        """测试：路径中包含 Unicode 字符"""
        assert match_pattern('.kiro/测试文件.md', '.kiro/*') == True
    
    def test_dot_files(self):
        """测试：隐藏文件（以 . 开头）"""
        assert match_pattern('.kiro/.gitignore', '.kiro/*') == True


class TestIntegration:
    """集成测试：测试实际使用场景"""
    
    def test_steering_file_detection(self):
        """测试：检测 Steering 文件"""
        path = '.kiro/modules/workflow/v1.0/steering/workflow_selector.md'
        patterns = ['.kiro/steering/*', '.kiro/modules/*/steering/*']
        assert match_directory(path, patterns) == True
    
    def test_config_file_detection(self):
        """测试：检测配置文件"""
        assert match_file_type('.kiro/config.yaml', ['.yaml', '.json']) == True
        assert match_file_type('.kiro/config.json', ['.yaml', '.json']) == True
    
    def test_documentation_file_detection(self):
        """测试：检测文档文件"""
        path = 'doc/project/architecture/design.md'
        assert match_directory(path, 'doc/**/*') == True
        assert match_file_type(path, '.md') == True
    
    def test_module_directory_detection(self):
        """测试：检测模块目录"""
        paths = [
            '.kiro/modules/workflow/v1.0',
            '.kiro/modules/ai-dev/v1.0',
            '.kiro/modules/git-commit/v1.0'
        ]
        for path in paths:
            assert match_directory(path, '.kiro/modules/*') == True


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v', '--tb=short'])
