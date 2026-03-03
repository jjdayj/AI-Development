"""
动态加载器集成测试

测试 DynamicLoader 在真实场景下的完整工作流程，包括：
1. 完整的加载流程（从配置读取到 Prompt 整合）
2. 各种配置组合（多模块、依赖关系、优先级排序）
3. 错误处理（配置错误、依赖缺失、循环依赖）
4. 与其他组件的集成（上下文管理、配置合并）

需求追溯：需求 1-15

作者: yangzhuo
日期: 2026-03-03
版本: v1.0
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import yaml
import sys

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from dynamic_loader import DynamicLoader, load_modules


class TestCompleteLoadingFlow:
    """测试完整的加载流程"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # 创建基础目录结构
        (self.project_root / ".kiro").mkdir(parents=True)
        (self.project_root / ".kiro" / "modules").mkdir(parents=True)
    
    def teardown_method(self):
        """每个测试后的清理"""
        shutil.rmtree(self.temp_dir)
    
    def _create_top_config(self, modules_config):
        """创建顶层配置文件"""
        config_path = self.project_root / ".kiro" / "config.yaml"
        config = {
            'version': '2.0',
            'modules': modules_config
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
    
    def _create_module(self, name, version, priority, activation_conditions=None, dependencies=None):
        """创建完整的模块结构"""
        module_dir = self.project_root / ".kiro" / "modules" / name / version
        module_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建 config.yaml
        if activation_conditions is None:
            activation_conditions = {'always': True}
        
        config = {
            'activation_conditions': activation_conditions
        }
        
        if dependencies:
            config['dependencies'] = dependencies
        
        with open(module_dir / "config.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
        
        # 创建 steering 目录和文件
        steering_dir = module_dir / "steering"
        steering_dir.mkdir(exist_ok=True)
        
        if name == 'workflow':
            steering_file = steering_dir / "workflow_selector.md"
        else:
            steering_file = steering_dir / f"{name}.md"
        
        with open(steering_file, 'w', encoding='utf-8') as f:
            f.write(f"# {name} Steering Rules\n\n")
            f.write(f"Version: {version}\n")
            f.write(f"Priority: {priority}\n\n")
            f.write(f"This is the steering content for {name}.\n")
    
    def test_scenario_1_basic_loading(self):
        """场景 1：基本加载流程
        
        测试最简单的场景：
        - 1 个模块
        - 无依赖
        - always 激活条件
        """
        # 创建配置
        self._create_top_config({
            'test-module': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 100
            }
        })
        
        # 创建模块
        self._create_module('test-module', 'v1.0', 100)
        
        # 执行加载
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        # 验证结果
        assert success, "加载应该成功"
        assert result['loaded_count'] == 1, "应该加载 1 个模块"
        assert result['failed_count'] == 0, "不应该有失败的模块"
        assert 'test-module' in prompt, "Prompt 应该包含模块内容"
        assert 'Steering Rules' in prompt, "Prompt 应该包含 Steering 标题"
    
    def test_scenario_2_multiple_modules_with_priority(self):
        """场景 2：多模块优先级排序
        
        测试：
        - 3 个模块
        - 不同优先级
        - 验证加载顺序
        """
        # 创建配置
        self._create_top_config({
            'module-low': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 50
            },
            'module-high': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 200
            },
            'module-medium': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 100
            }
        })
        
        # 创建模块
        self._create_module('module-low', 'v1.0', 50)
        self._create_module('module-high', 'v1.0', 200)
        self._create_module('module-medium', 'v1.0', 100)
        
        # 执行加载
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        # 验证结果
        assert success
        assert result['loaded_count'] == 3
        
        # 验证加载顺序（按优先级从高到低）
        loaded = loader.get_loaded_modules()
        assert loaded[0]['name'] == 'module-high'
        assert loaded[1]['name'] == 'module-medium'
        assert loaded[2]['name'] == 'module-low'
        
        # 验证 Prompt 中的顺序
        high_pos = prompt.find('module-high')
        medium_pos = prompt.find('module-medium')
        low_pos = prompt.find('module-low')
        assert high_pos < medium_pos < low_pos, "Prompt 中的顺序应该与优先级一致"
    
    def test_scenario_3_conditional_activation(self):
        """场景 3：条件激活
        
        测试：
        - 2 个模块
        - 1 个 always 激活
        - 1 个条件激活（directory_match）
        """
        # 创建配置
        self._create_top_config({
            'module-always': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 100
            },
            'module-conditional': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 90
            }
        })
        
        # 创建模块
        self._create_module('module-always', 'v1.0', 100, {'always': True})
        self._create_module('module-conditional', 'v1.0', 90, {
            'directory_match': ['.kiro/steering*']
        })
        
        # 场景 3a：上下文匹配，两个模块都激活
        loader = DynamicLoader(str(self.project_root))
        context = {
            'current_directory': '.kiro/steering',
            'current_file_type': '.md'
        }
        success, prompt, result = loader.load(context)
        
        assert success
        assert result['loaded_count'] == 2, "两个模块都应该激活"
        
        # 场景 3b：上下文不匹配，只有 always 模块激活
        loader2 = DynamicLoader(str(self.project_root))
        context2 = {
            'current_directory': 'src',
            'current_file_type': '.py'
        }
        success2, prompt2, result2 = loader2.load(context2)
        
        assert success2
        assert result2['loaded_count'] == 1, "只有 always 模块应该激活"
        assert loader2.get_loaded_modules()[0]['name'] == 'module-always'
    
    def test_scenario_4_module_dependencies(self):
        """场景 4：模块依赖关系
        
        测试：
        - 3 个模块
        - module-c 依赖 module-b
        - module-b 依赖 module-a
        - 验证依赖链正确处理
        """
        # 创建配置
        self._create_top_config({
            'module-a': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 100
            },
            'module-b': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 90
            },
            'module-c': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 80
            }
        })
        
        # 创建模块
        self._create_module('module-a', 'v1.0', 100, dependencies=[])
        self._create_module('module-b', 'v1.0', 90, dependencies=['module-a'])
        self._create_module('module-c', 'v1.0', 80, dependencies=['module-b'])
        
        # 执行加载
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        # 验证结果
        assert success
        assert result['loaded_count'] == 3, "所有模块依赖都满足，应该全部加载"
        assert result['failed_count'] == 0
    
    def test_scenario_5_missing_dependency(self):
        """场景 5：缺失依赖
        
        测试：
        - 2 个模块
        - module-b 依赖 module-a
        - module-a 被禁用
        - module-b 应该加载失败
        """
        # 创建配置
        self._create_top_config({
            'module-a': {
                'enabled': False,  # 禁用
                'version': 'v1.0',
                'priority': 100
            },
            'module-b': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 90
            }
        })
        
        # 创建模块
        self._create_module('module-a', 'v1.0', 100)
        self._create_module('module-b', 'v1.0', 90, dependencies=['module-a'])
        
        # 执行加载
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        # 验证结果
        assert success, "加载流程应该成功（即使有模块失败）"
        assert result['loaded_count'] == 0, "module-b 依赖缺失，不应该加载"
        assert result['failed_count'] == 1, "module-b 应该加载失败"
        
        # 验证失败原因
        failed = loader.get_failed_modules()
        assert len(failed) == 1
        assert 'module-a' in failed[0]['reason'], "失败原因应该提到缺失的依赖"
    
    def test_scenario_6_circular_dependency(self):
        """场景 6：循环依赖
        
        测试：
        - 2 个模块
        - module-a 依赖 module-b
        - module-b 依赖 module-a
        - 两个模块都应该加载失败
        """
        # 创建配置
        self._create_top_config({
            'module-a': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 100
            },
            'module-b': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 90
            }
        })
        
        # 创建模块（循环依赖）
        self._create_module('module-a', 'v1.0', 100, dependencies=['module-b'])
        self._create_module('module-b', 'v1.0', 90, dependencies=['module-a'])
        
        # 执行加载
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        # 验证结果
        assert success, "加载流程应该成功（即使有模块失败）"
        assert result['loaded_count'] == 0, "循环依赖的模块都不应该加载"
        assert result['failed_count'] == 2, "两个模块都应该失败"
        
        # 验证失败原因
        failed = loader.get_failed_modules()
        assert len(failed) == 2
        for item in failed:
            assert '循环依赖' in item['reason'], "失败原因应该提到循环依赖"
    
    def test_scenario_7_config_merge(self):
        """场景 7：配置合并
        
        测试：
        - 顶层配置和模块配置的合并
        - 顶层配置优先级更高
        """
        # 创建配置（顶层指定 priority: 200）
        self._create_top_config({
            'test-module': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 200  # 顶层配置
            }
        })
        
        # 创建模块（模块配置中没有 priority）
        module_dir = self.project_root / ".kiro" / "modules" / "test-module" / "v1.0"
        module_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            'activation_conditions': {'always': True}
            # 注意：没有 priority 字段
        }
        with open(module_dir / "config.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        steering_dir = module_dir / "steering"
        steering_dir.mkdir(exist_ok=True)
        with open(steering_dir / "test-module.md", 'w', encoding='utf-8') as f:
            f.write("# Test Module")
        
        # 执行加载
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        # 验证结果
        assert success
        assert result['loaded_count'] == 1
        
        # 验证合并后的优先级
        loaded = loader.get_loaded_modules()
        assert loaded[0]['priority'] == 200, "应该使用顶层配置的 priority"
    
    def test_scenario_8_workflow_special_filename(self):
        """场景 8：Workflow 模块特殊文件名
        
        测试：
        - workflow 模块使用 workflow_selector.md
        - 其他模块使用 {module}.md
        """
        # 创建配置
        self._create_top_config({
            'workflow': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 200
            },
            'other-module': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 100
            }
        })
        
        # 创建 workflow 模块（使用特殊文件名）
        self._create_module('workflow', 'v1.0', 200)
        
        # 创建普通模块
        self._create_module('other-module', 'v1.0', 100)
        
        # 执行加载
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        # 验证结果
        assert success
        assert result['loaded_count'] == 2
        assert 'workflow' in prompt
        assert 'other-module' in prompt


class TestErrorHandling:
    """测试错误处理"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        (self.project_root / ".kiro").mkdir(parents=True)
        (self.project_root / ".kiro" / "modules").mkdir(parents=True)
    
    def teardown_method(self):
        """每个测试后的清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_error_1_missing_config_file(self):
        """错误 1：配置文件不存在"""
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        assert not success, "配置文件不存在，加载应该失败"
        assert result['loaded_count'] == 0
    
    def test_error_2_invalid_yaml_format(self):
        """错误 2：YAML 格式错误"""
        config_path = self.project_root / ".kiro" / "config.yaml"
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write("invalid: yaml: format: [\n")  # 无效的 YAML
        
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        assert not success, "YAML 格式错误，加载应该失败"
    
    def test_error_3_missing_steering_file(self):
        """错误 3：Steering 文件不存在"""
        # 创建配置
        config_path = self.project_root / ".kiro" / "config.yaml"
        config = {
            'version': '2.0',
            'modules': {
                'test-module': {
                    'enabled': True,
                    'version': 'v1.0',
                    'priority': 100
                }
            }
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        # 创建模块目录但不创建 Steering 文件
        module_dir = self.project_root / ".kiro" / "modules" / "test-module" / "v1.0"
        module_dir.mkdir(parents=True, exist_ok=True)
        
        config = {'activation_conditions': {'always': True}}
        with open(module_dir / "config.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        # 执行加载
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        # 验证结果（应该继续处理，但该模块加载失败）
        assert success, "Steering 文件缺失不应该导致整个流程失败"
        # 注意：由于 Steering 加载失败，模块可能不会被计入 loaded_modules
    
    def test_error_4_partial_failure(self):
        """错误 4：部分模块失败
        
        测试：
        - 3 个模块
        - 1 个成功
        - 1 个依赖缺失
        - 1 个循环依赖
        """
        # 创建配置
        config_path = self.project_root / ".kiro" / "config.yaml"
        config = {
            'version': '2.0',
            'modules': {
                'module-ok': {
                    'enabled': True,
                    'version': 'v1.0',
                    'priority': 100
                },
                'module-missing-dep': {
                    'enabled': True,
                    'version': 'v1.0',
                    'priority': 90
                },
                'module-circular-a': {
                    'enabled': True,
                    'version': 'v1.0',
                    'priority': 80
                },
                'module-circular-b': {
                    'enabled': True,
                    'version': 'v1.0',
                    'priority': 70
                }
            }
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        # 创建模块
        # module-ok: 正常模块
        module_dir = self.project_root / ".kiro" / "modules" / "module-ok" / "v1.0"
        module_dir.mkdir(parents=True, exist_ok=True)
        with open(module_dir / "config.yaml", 'w', encoding='utf-8') as f:
            yaml.dump({'activation_conditions': {'always': True}}, f)
        steering_dir = module_dir / "steering"
        steering_dir.mkdir(exist_ok=True)
        with open(steering_dir / "module-ok.md", 'w', encoding='utf-8') as f:
            f.write("# OK")
        
        # module-missing-dep: 依赖不存在的模块
        module_dir = self.project_root / ".kiro" / "modules" / "module-missing-dep" / "v1.0"
        module_dir.mkdir(parents=True, exist_ok=True)
        with open(module_dir / "config.yaml", 'w', encoding='utf-8') as f:
            yaml.dump({
                'activation_conditions': {'always': True},
                'dependencies': ['non-existent-module']
            }, f)
        steering_dir = module_dir / "steering"
        steering_dir.mkdir(exist_ok=True)
        with open(steering_dir / "module-missing-dep.md", 'w', encoding='utf-8') as f:
            f.write("# Missing Dep")
        
        # module-circular-a 和 module-circular-b: 循环依赖
        for name, dep in [('module-circular-a', 'module-circular-b'), 
                          ('module-circular-b', 'module-circular-a')]:
            module_dir = self.project_root / ".kiro" / "modules" / name / "v1.0"
            module_dir.mkdir(parents=True, exist_ok=True)
            with open(module_dir / "config.yaml", 'w', encoding='utf-8') as f:
                yaml.dump({
                    'activation_conditions': {'always': True},
                    'dependencies': [dep]
                }, f)
            steering_dir = module_dir / "steering"
            steering_dir.mkdir(exist_ok=True)
            with open(steering_dir / f"{name}.md", 'w', encoding='utf-8') as f:
                f.write(f"# {name}")
        
        # 执行加载
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        # 验证结果
        assert success, "部分失败不应该导致整个流程失败"
        assert result['loaded_count'] == 1, "只有 module-ok 应该成功"
        assert result['failed_count'] == 3, "其他 3 个模块应该失败"


class TestIntegrationWithComponents:
    """测试与其他组件的集成"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        (self.project_root / ".kiro").mkdir(parents=True)
        (self.project_root / ".kiro" / "modules").mkdir(parents=True)
    
    def teardown_method(self):
        """每个测试后的清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_integration_with_context_manager(self):
        """测试与上下文管理器的集成"""
        # 创建 current_context.yaml
        context_path = self.project_root / ".kiro" / "current_context.yaml"
        context_data = {
            'active_requirement': {
                'path': 'requirements/test/v1.0/',
                'topic': '测试需求',
                'version': 'v1.0',
                'status': '开发中'
            },
            'environment': {
                'current_directory': '.kiro/steering',
                'current_file': 'main.md',
                'current_file_type': '.md'
            },
            'updated_at': '2026-03-03 10:00:00'
        }
        with open(context_path, 'w', encoding='utf-8') as f:
            yaml.dump(context_data, f, allow_unicode=True)
        
        # 创建配置和模块
        config_path = self.project_root / ".kiro" / "config.yaml"
        config = {
            'version': '2.0',
            'modules': {
                'test-module': {
                    'enabled': True,
                    'version': 'v1.0',
                    'priority': 100
                }
            }
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        module_dir = self.project_root / ".kiro" / "modules" / "test-module" / "v1.0"
        module_dir.mkdir(parents=True, exist_ok=True)
        with open(module_dir / "config.yaml", 'w', encoding='utf-8') as f:
            yaml.dump({'activation_conditions': {'always': True}}, f)
        steering_dir = module_dir / "steering"
        steering_dir.mkdir(exist_ok=True)
        with open(steering_dir / "test-module.md", 'w', encoding='utf-8') as f:
            f.write("# Test")
        
        # 执行加载（不提供上下文，应该从 current_context.yaml 读取）
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        # 验证结果
        assert success
        assert result['loaded_count'] == 1
    
    def test_convenience_function(self):
        """测试便捷函数"""
        # 创建配置
        config_path = self.project_root / ".kiro" / "config.yaml"
        config = {
            'version': '2.0',
            'modules': {
                'test-module': {
                    'enabled': True,
                    'version': 'v1.0',
                    'priority': 100
                }
            }
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        # 创建模块
        module_dir = self.project_root / ".kiro" / "modules" / "test-module" / "v1.0"
        module_dir.mkdir(parents=True, exist_ok=True)
        with open(module_dir / "config.yaml", 'w', encoding='utf-8') as f:
            yaml.dump({'activation_conditions': {'always': True}}, f)
        steering_dir = module_dir / "steering"
        steering_dir.mkdir(exist_ok=True)
        with open(steering_dir / "test-module.md", 'w', encoding='utf-8') as f:
            f.write("# Test")
        
        # 使用便捷函数
        success, prompt, result = load_modules(project_root=str(self.project_root))
        
        # 验证结果
        assert success
        assert result['loaded_count'] == 1
        assert isinstance(prompt, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
