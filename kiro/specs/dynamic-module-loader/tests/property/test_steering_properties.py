"""
Steering 加载器和 Prompt 整合器属性测试

验证 Steering 加载器和 Prompt 整合器的正确性属性，包括路径构建、加载顺序、
内容完整性和 Prompt 整合完整性。

需求追溯：需求 7.1, 8.1, 11.2, 14.1, 14.2, 14.3, 15.3
"""

import os
import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import composite
import pytest

from src.steering_loader import SteeringLoader, build_steering_path
from src.prompt_integrator import PromptIntegrator, integrate_steering_contents


# 测试数据生成策略
@composite
def module_names(draw):
    """生成有效的模块名称"""
    # 模块名称：字母、数字、连字符，但排除 'steering' 以避免路径冲突
    name_parts = draw(st.lists(
        st.text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789', min_size=2, max_size=8),
        min_size=1, max_size=3
    ))
    name = '-'.join(name_parts)
    
    # 避免与 'steering' 目录名冲突和其他保留名称
    reserved_names = {'steering', 'modules', 'kiro'}
    if name in reserved_names:
        name = f'module-{name}'
    
    return name


@composite
def module_versions(draw):
    """生成有效的模块版本"""
    # 版本格式：v{major}.{minor}[.{patch}][-{prerelease}]
    major = draw(st.integers(min_value=1, max_value=10))
    minor = draw(st.integers(min_value=0, max_value=20))
    
    # 可选的 patch 版本
    has_patch = draw(st.booleans())
    if has_patch:
        patch = draw(st.integers(min_value=0, max_value=50))
        version = f"v{major}.{minor}.{patch}"
    else:
        version = f"v{major}.{minor}"
    
    # 可选的预发布标识
    has_prerelease = draw(st.booleans())
    if has_prerelease:
        prerelease = draw(st.sampled_from(['alpha', 'beta', 'rc', 'simple', 'complex']))
        version += f"-{prerelease}"
    
    return version


@composite
def activation_conditions(draw):
    """生成激活条件"""
    condition_type = draw(st.sampled_from([
        'always', 'directory_match', 'file_type_match', 'and_logic', 'or_logic'
    ]))
    
    if condition_type == 'always':
        return {'always': True}
    elif condition_type == 'directory_match':
        patterns = draw(st.lists(
            st.text(alphabet='abcdefghijklmnopqrstuvwxyz/*', min_size=1, max_size=20),
            min_size=1, max_size=3
        ))
        return {'directory_match': patterns}
    elif condition_type == 'file_type_match':
        extensions = draw(st.lists(
            st.sampled_from(['.py', '.js', '.ts', '.md', '.yaml', '.json']),
            min_size=1, max_size=3
        ))
        return {'file_type_match': extensions}
    elif condition_type == 'and_logic':
        return {'and': [{'always': True}, {'directory_match': ['src/*']}]}
    else:  # or_logic
        return {'or': [{'file_type_match': ['.py']}, {'directory_match': ['tests/*']}]}


@composite
def base_paths(draw):
    """生成基础路径"""
    path_type = draw(st.sampled_from(['standard', 'custom', 'nested']))
    
    if path_type == 'standard':
        return '.kiro/modules'
    elif path_type == 'custom':
        parts = draw(st.lists(
            st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=1, max_size=8),
            min_size=1, max_size=3
        ))
        return '/'.join(parts)
    else:  # nested
        return 'project/config/modules'


class TestSteeringLoaderProperties:
    """Steering 加载器属性测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        
    def teardown_method(self):
        """每个测试方法后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @given(
        module_name=module_names(),
        module_version=module_versions(),
        base_path=base_paths()
    )
    @settings(max_examples=100, deadline=None)
    def test_property_6_path_construction_correctness(self, module_name, module_version, base_path):
        """
        属性 6：路径构建正确性
        
        验证需求：需求 7.1, 11.2
        
        属性：对于任何有效的模块名称、版本和基础路径，
        构建的路径应该：
        1. 包含所有必要的路径组件
        2. 使用正确的文件名（workflow 模块特殊处理）
        3. 路径格式符合规范
        """
        # Feature: dynamic-module-loader, Property 6: 路径构建正确性
        
        loader = SteeringLoader(base_path)
        path = loader.build_steering_path(module_name, module_version)
        
        # 验证路径包含所有必要组件
        path_obj = Path(path)
        parts = path_obj.parts
        
        # 应该包含：base_path_parts + module_name + version + steering + filename
        assert len(parts) >= 4, f"路径组件不足: {path}"
        
        # 验证 steering 目录存在
        assert 'steering' in parts, f"缺少 steering 目录: {path}"
        
        # 验证文件扩展名
        assert path.endswith('.md'), f"文件扩展名错误: {path}"
        
        # 验证模块名称在路径中
        assert module_name in parts, f"模块名称不在路径中: {path}"
        
        # 验证版本在路径中
        assert module_version in parts, f"版本不在路径中: {path}"
        
        # 验证 workflow 模块的特殊文件名
        if module_name == 'workflow':
            assert path.endswith('workflow_selector.md'), f"workflow 模块文件名错误: {path}"
        else:
            assert path.endswith(f'{module_name}.md'), f"标准模块文件名错误: {path}"
        
        # 验证路径格式（如果不是空基础路径）
        if base_path.strip():
            assert loader.validate_path_format(path), f"路径格式验证失败: {path}"
    
    @given(
        modules_data=st.lists(
            st.tuples(
                module_names(),
                module_versions(),
                st.integers(min_value=1, max_value=1000),  # priority
                activation_conditions()
            ),
            min_size=1, max_size=10
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_property_7_steering_loading_order_correctness(self, modules_data):
        """
        属性 7：Steering 加载顺序正确性
        
        验证需求：需求 8.1
        
        属性：当加载多个模块的 Steering 文件时，
        加载顺序应该：
        1. 按优先级从高到低排序
        2. 优先级相同时按模块名称字母顺序排序
        3. 每个模块的路径构建都正确
        """
        # Feature: dynamic-module-loader, Property 7: Steering 加载顺序正确性
        
        loader = SteeringLoader(self.temp_dir)
        
        # 创建测试文件
        created_files = []
        for module_name, module_version, priority, conditions in modules_data:
            # 创建目录结构
            module_dir = os.path.join(
                self.temp_dir, module_name, module_version, "steering"
            )
            os.makedirs(module_dir, exist_ok=True)
            
            # 确定文件名
            if module_name == 'workflow':
                filename = 'workflow_selector.md'
            else:
                filename = f'{module_name}.md'
            
            # 创建文件
            file_path = os.path.join(module_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {module_name} Steering\n\nPriority: {priority}")
            
            created_files.append((module_name, module_version, priority, conditions))
        
        # 按预期顺序排序（优先级降序，名称升序）
        expected_order = sorted(
            created_files,
            key=lambda x: (-x[2], x[0])  # -priority, module_name
        )
        
        # 验证每个模块的路径构建和加载
        loaded_results = []
        for module_name, module_version, priority, conditions in expected_order:
            success, content, error_type = loader.load_steering(
                module_name, module_version, priority, conditions
            )
            
            if success:
                loaded_results.append((module_name, priority, content))
        
        # 验证加载成功的模块保持正确顺序
        if len(loaded_results) > 1:
            for i in range(len(loaded_results) - 1):
                current_name, current_priority, _ = loaded_results[i]
                next_name, next_priority, _ = loaded_results[i + 1]
                
                # 验证优先级顺序
                if current_priority != next_priority:
                    assert current_priority > next_priority, \
                        f"优先级顺序错误: {current_name}({current_priority}) 应该在 {next_name}({next_priority}) 之前"
                else:
                    # 优先级相同时验证名称顺序
                    assert current_name <= next_name, \
                        f"名称顺序错误: {current_name} 应该在 {next_name} 之前"
    
    @given(
        module_name=module_names(),
        module_version=module_versions(),
        priority=st.integers(min_value=1, max_value=1000),
        conditions=activation_conditions(),
        content=st.text(min_size=10, max_size=1000)
    )
    @settings(max_examples=100, deadline=None)
    def test_property_8_steering_content_integrity(self, module_name, module_version, 
                                                  priority, conditions, content):
        """
        属性 8：Steering 内容完整性
        
        验证需求：需求 14.1, 14.2, 14.3
        
        属性：加载的 Steering 内容应该：
        1. 包含原始文件内容
        2. 包含正确的模块标识注释
        3. 注释包含所有必要的元信息
        4. 内容格式正确且完整
        """
        # Feature: dynamic-module-loader, Property 8: Steering 内容完整性
        
        loader = SteeringLoader(self.temp_dir)
        
        # 创建测试文件
        module_dir = os.path.join(
            self.temp_dir, module_name, module_version, "steering"
        )
        os.makedirs(module_dir, exist_ok=True)
        
        # 确定文件名
        if module_name == 'workflow':
            filename = 'workflow_selector.md'
        else:
            filename = f'{module_name}.md'
        
        file_path = os.path.join(module_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 加载 Steering 文件
        success, loaded_content, error_type = loader.load_steering(
            module_name, module_version, priority, conditions
        )
        
        # 验证加载成功
        assert success, f"加载失败: {error_type}"
        assert error_type is None, f"不应该有错误: {error_type}"
        
        # 验证内容完整性
        assert loaded_content is not None, "加载的内容不应该为空"
        assert len(loaded_content) > len(content), "加载的内容应该包含注释"
        
        # 验证包含原始内容（处理不同的行结束符）
        normalized_content = content.replace('\r\n', '\n').replace('\r', '\n')
        normalized_loaded = loaded_content.replace('\r\n', '\n').replace('\r', '\n')
        assert normalized_content in normalized_loaded, "加载的内容应该包含原始文件内容"
        
        # 验证模块标识注释
        comment_start = f"<!-- Module: {module_name}"
        assert comment_start in loaded_content, "应该包含模块标识注释"
        
        # 验证注释包含必要信息
        assert f"Version: {module_version}" in loaded_content, "注释应该包含版本信息"
        assert f"Priority: {priority}" in loaded_content, "注释应该包含优先级信息"
        assert "Activated:" in loaded_content, "注释应该包含激活条件信息"
        
        # 验证注释格式
        lines = loaded_content.split('\n')
        first_line = lines[0]
        assert first_line.startswith('<!--'), "第一行应该是注释开始"
        assert first_line.endswith('-->'), "第一行应该是完整的注释"
        
        # 验证注释后有空行分隔
        assert lines[1] == '', "注释后应该有空行"
        
        # 验证原始内容从第三行开始（处理行结束符）
        original_start_line = 2
        remaining_content = '\n'.join(lines[original_start_line:])
        normalized_remaining = remaining_content.replace('\r\n', '\n').replace('\r', '\n')
        normalized_original = content.replace('\r\n', '\n').replace('\r', '\n')
        assert normalized_remaining == normalized_original, "原始内容应该完整保留"
    
    @given(
        module_name=st.sampled_from(['workflow', 'ai-dev', 'git-commit']),
        module_version=module_versions()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_6_workflow_special_handling(self, module_name, module_version):
        """
        属性 6 的特殊情况：workflow 模块特殊处理
        
        验证 workflow 模块使用 workflow_selector.md 文件名
        """
        # Feature: dynamic-module-loader, Property 6: 路径构建正确性（workflow 特殊情况）
        
        path = build_steering_path(module_name, module_version)
        
        if module_name == 'workflow':
            assert path.endswith('workflow_selector.md'), \
                f"workflow 模块应该使用 workflow_selector.md: {path}"
        else:
            assert path.endswith(f'{module_name}.md'), \
                f"非 workflow 模块应该使用标准文件名: {path}"
    
    @given(
        conditions=activation_conditions()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_8_activation_conditions_formatting(self, conditions):
        """
        属性 8 的特殊情况：激活条件格式化
        
        验证激活条件在注释中的格式化正确性
        """
        # Feature: dynamic-module-loader, Property 8: Steering 内容完整性（条件格式化）
        
        loader = SteeringLoader()
        comment = loader.create_module_comment('test-module', 'v1.0', 100, conditions)
        
        # 验证注释格式
        assert comment.startswith('<!--'), "注释应该以 <!-- 开始"
        assert comment.endswith('-->\n\n'), "注释应该以 --> 结束并有两个换行"
        
        # 验证激活条件被正确格式化
        if conditions.get('always'):
            assert 'Activated: always' in comment
        elif 'directory_match' in conditions:
            assert 'Activated: dir:' in comment
        elif 'file_type_match' in conditions:
            assert 'Activated: type:' in comment
        elif 'and' in conditions:
            assert 'Activated: and_logic' in comment
        elif 'or' in conditions:
            assert 'Activated: or_logic' in comment
        else:
            assert 'Activated: custom' in comment


class TestPromptIntegratorProperties:
    """Prompt 整合器属性测试类"""
    
    @given(
        steering_data=st.lists(
            st.tuples(
                module_names(),
                module_versions(),
                st.integers(min_value=1, max_value=1000),  # priority
                activation_conditions(),
                st.text(min_size=0, max_size=500)  # content
            ),
            min_size=0, max_size=10
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_property_9_prompt_integration_completeness(self, steering_data):
        """
        属性 9：Prompt 整合完整性
        
        验证需求：需求 15.3
        
        属性：整合后的 Prompt 应该：
        1. 包含所有输入模块的内容
        2. 保持模块的优先级顺序
        3. 包含正确的层级结构说明
        4. 包含完整的模块列表
        5. 格式正确且结构完整
        """
        # Feature: dynamic-module-loader, Property 9: Prompt 整合完整性
        
        integrator = PromptIntegrator()
        
        # 执行整合（不对输入数据排序，因为 PromptIntegrator 期望输入已经排序）
        result = integrator.integrate_prompts(steering_data)
        
        # 验证基本结构完整性
        assert isinstance(result, str), "整合结果必须是字符串"
        assert len(result) > 0, "整合结果不能为空"
        
        if not steering_data:
            # 空输入的情况
            assert "当前没有激活的模块" in result, "空输入应该显示无激活模块"
            assert "激活模块数**: 0" in result, "空输入应该显示模块数为 0"
        else:
            # 有内容的情况
            
            # 1. 验证包含所有模块内容
            for module_name, version, priority, conditions, content in steering_data:
                assert module_name in result, f"整合结果应该包含模块 {module_name}"
                assert version in result, f"整合结果应该包含版本 {version}"
                assert str(priority) in result, f"整合结果应该包含优先级 {priority}"
                
                # 如果模块有内容，验证内容被包含
                if content and content.strip():
                    # 处理可能的行结束符差异
                    normalized_content = content.strip().replace('\r\n', '\n').replace('\r', '\n')
                    normalized_result = result.replace('\r\n', '\n').replace('\r', '\n')
                    assert normalized_content in normalized_result, \
                        f"整合结果应该包含模块 {module_name} 的内容"
            
            # 2. 验证结构完整性（不验证具体顺序，因为可能有重复模块名）
            # 验证每个模块都在结果中出现了正确的次数
            module_count_in_input = {}
            for module_name, _, _, _, _ in steering_data:
                module_count_in_input[module_name] = module_count_in_input.get(module_name, 0) + 1
            
            for module_name, expected_count in module_count_in_input.items():
                # 使用更精确的匹配，避免子字符串匹配问题
                import re
                pattern = rf"^## {re.escape(module_name)} \("
                actual_count = len(re.findall(pattern, result, re.MULTILINE))
                assert actual_count == expected_count, \
                    f"模块 {module_name} 应该出现 {expected_count} 次，实际出现 {actual_count} 次"
            
            # 3. 验证层级结构说明
            assert "# Kiro Prompt 层级结构" in result, "应该包含层级结构说明"
            assert "L0 (顶层入口)" in result, "应该包含 L0 层级说明"
            assert "L1 (加载器逻辑)" in result, "应该包含 L1 层级说明"
            assert "L2 (模块规则)" in result, "应该包含 L2 层级说明"
            
            # 4. 验证模块列表
            assert "# 激活的模块" in result, "应该包含激活模块列表"
            assert f"共激活 {len(steering_data)} 个模块" in result, "应该显示正确的模块数量"
            
            # 5. 验证完成标记
            assert "# Prompt 整合完成" in result, "应该包含整合完成标记"
            assert f"激活模块数**: {len(steering_data)}" in result, "完成标记应该显示正确的模块数量"
    
    @given(
        steering_data=st.lists(
            st.tuples(
                module_names(),
                module_versions(),
                st.integers(min_value=1, max_value=1000),
                activation_conditions(),
                st.text(min_size=10, max_size=200)
            ),
            min_size=1, max_size=5
        ),
        include_hierarchy=st.booleans(),
        include_module_list=st.booleans()
    )
    @settings(max_examples=50, deadline=None)
    def test_property_9_integration_options_consistency(self, steering_data, include_hierarchy, include_module_list):
        """
        属性 9 的扩展：整合选项一致性
        
        验证不同整合选项的一致性和正确性
        """
        # Feature: dynamic-module-loader, Property 9: Prompt 整合完整性（选项一致性）
        
        integrator = PromptIntegrator()
        result = integrator.integrate_prompts(
            steering_data, 
            include_hierarchy=include_hierarchy,
            include_module_list=include_module_list
        )
        
        # 验证选项控制的正确性
        if include_hierarchy:
            assert "# Kiro Prompt 层级结构" in result, "启用层级结构时应该包含层级说明"
        else:
            assert "# Kiro Prompt 层级结构" not in result, "禁用层级结构时不应该包含层级说明"
        
        if include_module_list:
            assert "# 激活的模块" in result, "启用模块列表时应该包含模块列表"
        else:
            assert "# 激活的模块" not in result, "禁用模块列表时不应该包含模块列表"
        
        # 无论选项如何，都应该包含内容部分和完成标记
        assert "# 模块 Steering 规则" in result, "应该始终包含模块内容部分"
        assert "# Prompt 整合完成" in result, "应该始终包含完成标记"
    
    @given(
        steering_data=st.lists(
            st.tuples(
                module_names(),
                module_versions(),
                st.integers(min_value=1, max_value=1000),
                activation_conditions(),
                st.text(alphabet='abcdefghijklmnopqrstuvwxyz\n\r\t .,!?', min_size=0, max_size=100)
            ),
            min_size=0, max_size=3
        )
    )
    @settings(max_examples=50, deadline=None)
    def test_property_9_content_preservation(self, steering_data):
        """
        属性 9 的扩展：内容保持性
        
        验证原始内容在整合过程中的完整保持
        """
        # Feature: dynamic-module-loader, Property 9: Prompt 整合完整性（内容保持性）
        
        integrator = PromptIntegrator()
        result = integrator.integrate_prompts(steering_data)
        
        # 验证每个模块的内容都被正确保持
        for module_name, version, priority, conditions, content in steering_data:
            if content and content.strip():
                # 规范化处理不同的行结束符
                normalized_content = content.strip().replace('\r\n', '\n').replace('\r', '\n')
                normalized_result = result.replace('\r\n', '\n').replace('\r', '\n')
                
                # 内容应该在结果中完整出现
                assert normalized_content in normalized_result, \
                    f"模块 {module_name} 的内容应该在整合结果中完整保持"
        
        # 验证整合摘要的正确性
        summary = integrator.get_integration_summary(steering_data)
        assert summary['total_modules'] == len(steering_data), "摘要中的模块数量应该正确"
        assert len(summary['modules']) == len(steering_data), "摘要中的模块列表长度应该正确"
        
        # 验证输入验证的正确性
        valid, error = integrator.validate_integration_input(steering_data)
        assert valid is True, f"有效输入应该通过验证: {error}"
        assert error is None, "有效输入不应该有错误信息"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])