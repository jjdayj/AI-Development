"""
动态加载器单元测试

测试 DynamicLoader 类的所有功能，包括：
1. 初始化
2. 完整加载流程
3. 各个步骤的独立测试
4. 错误处理
5. 边界情况

需求追溯：需求 1-15
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


class TestDynamicLoaderInit:
    """测试 DynamicLoader 初始化"""
    
    def test_init_with_default_root(self):
        """测试使用默认项目根目录初始化"""
        loader = DynamicLoader()
        
        assert loader.project_root is not None
        assert loader.config_reader is not None
        assert loader.steering_loader is not None
        assert loader.prompt_integrator is not None
        assert loader.context_manager is not None
        assert loader.loaded_modules == []
        assert loader.failed_modules == []
        assert loader.integrated_prompt == ""
    
    def test_init_with_custom_root(self, tmp_path):
        """测试使用自定义项目根目录初始化"""
        loader = DynamicLoader(str(tmp_path))
        
        assert loader.project_root == tmp_path
        assert loader.config_reader is not None


class TestDynamicLoaderLoad:
    """测试 DynamicLoader 完整加载流程"""
    
    def setup_method(self):
        """每个测试前的设置"""
        # 创建临时目录
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
            yaml.dump(config, f)
    
    def _create_module_structure(self, module_name, version, activation_conditions=None):
        """创建模块目录结构"""
        module_dir = self.project_root / ".kiro" / "modules" / module_name / version
        module_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建 steering 目录
        steering_dir = module_dir / "steering"
        steering_dir.mkdir(exist_ok=True)
        
        # 创建 config.yaml
        if activation_conditions is None:
            activation_conditions = {'always': True}
        
        config = {
            'activation_conditions': activation_conditions
        }
        with open(module_dir / "config.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        # 创建 steering 文件
        if module_name == 'workflow':
            steering_file = steering_dir / "workflow_selector.md"
        else:
            steering_file = steering_dir / f"{module_name}.md"
        
        with open(steering_file, 'w', encoding='utf-8') as f:
            f.write(f"# {module_name} Steering Rules\n\nThis is the steering content for {module_name}.")
    
    def test_load_with_no_config(self):
        """测试没有配置文件的情况"""
        loader = DynamicLoader(str(self.project_root))
        
        success, prompt, result = loader.load()
        
        assert not success
        assert prompt == ""
        assert result['loaded_count'] == 0
        assert result['failed_count'] == 0
    
    def test_load_with_empty_modules(self):
        """测试空模块列表"""
        self._create_top_config({})
        
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        assert success
        assert result['loaded_count'] == 0
        assert result['failed_count'] == 0
    
    def test_load_with_single_module(self):
        """测试加载单个模块"""
        # 创建配置
        self._create_top_config({
            'test-module': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 100
            }
        })
        
        # 创建模块结构
        self._create_module_structure('test-module', 'v1.0')
        
        # 加载
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        assert success
        assert result['loaded_count'] == 1
        assert result['failed_count'] == 0
        assert len(loader.get_loaded_modules()) == 1
        assert loader.get_loaded_modules()[0]['name'] == 'test-module'
    
    def test_load_with_multiple_modules(self):
        """测试加载多个模块"""
        # 创建配置
        self._create_top_config({
            'module-a': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 200
            },
            'module-b': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 100
            },
            'module-c': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 150
            }
        })
        
        # 创建模块结构
        self._create_module_structure('module-a', 'v1.0')
        self._create_module_structure('module-b', 'v1.0')
        self._create_module_structure('module-c', 'v1.0')
        
        # 加载
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        assert success
        assert result['loaded_count'] == 3
        assert result['failed_count'] == 0
        
        # 验证排序（按优先级从高到低）
        loaded = loader.get_loaded_modules()
        assert loaded[0]['name'] == 'module-a'  # priority: 200
        assert loaded[1]['name'] == 'module-c'  # priority: 150
        assert loaded[2]['name'] == 'module-b'  # priority: 100
    
    def test_load_with_disabled_module(self):
        """测试禁用的模块不被加载"""
        # 创建配置
        self._create_top_config({
            'module-enabled': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 100
            },
            'module-disabled': {
                'enabled': False,
                'version': 'v1.0',
                'priority': 200
            }
        })
        
        # 创建模块结构
        self._create_module_structure('module-enabled', 'v1.0')
        self._create_module_structure('module-disabled', 'v1.0')
        
        # 加载
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        assert success
        assert result['loaded_count'] == 1
        assert loader.get_loaded_modules()[0]['name'] == 'module-enabled'
    
    def test_load_with_activation_conditions(self):
        """测试激活条件"""
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
        
        # 创建模块结构
        self._create_module_structure('module-always', 'v1.0', {'always': True})
        self._create_module_structure('module-conditional', 'v1.0', {
            'directory_match': ['.kiro/steering*']  # 修改为匹配 .kiro/steering
        })
        
        # 加载（使用匹配的上下文）
        loader = DynamicLoader(str(self.project_root))
        context = {
            'current_directory': '.kiro/steering',
            'current_file_type': '.md'
        }
        success, prompt, result = loader.load(context)
        
        assert success
        assert result['loaded_count'] == 2
    
    def test_load_with_dependencies(self):
        """测试模块依赖"""
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
        
        # 创建模块结构（module-b 依赖 module-a）
        self._create_module_structure('module-a', 'v1.0')
        
        module_b_dir = self.project_root / ".kiro" / "modules" / "module-b" / "v1.0"
        module_b_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            'activation_conditions': {'always': True},
            'dependencies': ['module-a']
        }
        with open(module_b_dir / "config.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        steering_dir = module_b_dir / "steering"
        steering_dir.mkdir(exist_ok=True)
        with open(steering_dir / "module-b.md", 'w', encoding='utf-8') as f:
            f.write("# module-b")
        
        # 加载
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        assert success
        assert result['loaded_count'] == 2
    
    def test_load_with_missing_dependency(self):
        """测试缺失依赖"""
        # 创建配置
        self._create_top_config({
            'module-a': {
                'enabled': True,
                'version': 'v1.0',
                'priority': 100
            }
        })
        
        # 创建模块结构（module-a 依赖不存在的 module-b）
        module_a_dir = self.project_root / ".kiro" / "modules" / "module-a" / "v1.0"
        module_a_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            'activation_conditions': {'always': True},
            'dependencies': ['module-b']
        }
        with open(module_a_dir / "config.yaml", 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        steering_dir = module_a_dir / "steering"
        steering_dir.mkdir(exist_ok=True)
        with open(steering_dir / "module-a.md", 'w', encoding='utf-8') as f:
            f.write("# module-a")
        
        # 加载
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        assert success
        assert result['loaded_count'] == 0
        assert result['failed_count'] == 1
    
    def test_load_with_circular_dependency(self):
        """测试循环依赖"""
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
        
        # 创建模块结构（module-a 依赖 module-b，module-b 依赖 module-a）
        for module_name, dep in [('module-a', 'module-b'), ('module-b', 'module-a')]:
            module_dir = self.project_root / ".kiro" / "modules" / module_name / "v1.0"
            module_dir.mkdir(parents=True, exist_ok=True)
            
            config = {
                'activation_conditions': {'always': True},
                'dependencies': [dep]
            }
            with open(module_dir / "config.yaml", 'w', encoding='utf-8') as f:
                yaml.dump(config, f)
            
            steering_dir = module_dir / "steering"
            steering_dir.mkdir(exist_ok=True)
            with open(steering_dir / f"{module_name}.md", 'w', encoding='utf-8') as f:
                f.write(f"# {module_name}")
        
        # 加载
        loader = DynamicLoader(str(self.project_root))
        success, prompt, result = loader.load()
        
        assert success
        assert result['loaded_count'] == 0
        assert result['failed_count'] == 2


class TestDynamicLoaderSteps:
    """测试 DynamicLoader 各个步骤"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        (self.project_root / ".kiro").mkdir(parents=True)
    
    def teardown_method(self):
        """每个测试后的清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_step1_read_top_config_success(self):
        """测试步骤 1：成功读取顶层配置"""
        # 创建配置文件
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
        
        loader = DynamicLoader(str(self.project_root))
        success, config_data, error = loader._step1_read_top_config()
        
        assert success
        assert 'modules' in config_data
        assert 'test-module' in config_data['modules']
        assert error == ""
    
    def test_step1_read_top_config_failure(self):
        """测试步骤 1：配置文件不存在"""
        loader = DynamicLoader(str(self.project_root))
        success, config_data, error = loader._step1_read_top_config()
        
        assert not success
        assert config_data == {}
        assert "不存在" in error
    
    def test_step2_filter_enabled_modules(self):
        """测试步骤 2：筛选启用的模块"""
        config = {
            'modules': {
                'module-enabled': {
                    'enabled': True,
                    'version': 'v1.0',
                    'priority': 100
                },
                'module-disabled': {
                    'enabled': False,
                    'version': 'v1.0',
                    'priority': 90
                }
            }
        }
        
        loader = DynamicLoader(str(self.project_root))
        enabled = loader._step2_filter_enabled_modules(config)
        
        assert len(enabled) == 1
        assert enabled[0]['name'] == 'module-enabled'
    
    def test_get_default_context(self):
        """测试获取默认上下文"""
        loader = DynamicLoader(str(self.project_root))
        context = loader._get_default_context()
        
        assert 'current_directory' in context
        assert 'current_file' in context
        assert 'current_file_type' in context


class TestDynamicLoaderHelpers:
    """测试 DynamicLoader 辅助方法"""
    
    def test_create_empty_prompt(self):
        """测试创建空 Prompt"""
        loader = DynamicLoader()
        prompt = loader._create_empty_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_create_result_summary(self):
        """测试创建结果摘要"""
        loader = DynamicLoader()
        loader.loaded_modules = [{'name': 'test'}]
        loader.failed_modules = []
        
        summary = loader._create_result_summary()
        
        assert summary['loaded_count'] == 1
        assert summary['failed_count'] == 0
        assert summary['total_count'] == 1
    
    def test_get_loaded_modules(self):
        """测试获取已加载模块"""
        loader = DynamicLoader()
        loader.loaded_modules = [{'name': 'test'}]
        
        modules = loader.get_loaded_modules()
        
        assert len(modules) == 1
        assert modules[0]['name'] == 'test'
    
    def test_get_failed_modules(self):
        """测试获取失败模块"""
        loader = DynamicLoader()
        loader.failed_modules = [{'module': {'name': 'test'}, 'reason': 'error'}]
        
        modules = loader.get_failed_modules()
        
        assert len(modules) == 1
    
    def test_get_integrated_prompt(self):
        """测试获取整合后的 Prompt"""
        loader = DynamicLoader()
        loader.integrated_prompt = "test prompt"
        
        prompt = loader.get_integrated_prompt()
        
        assert prompt == "test prompt"


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def setup_method(self):
        """每个测试前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        (self.project_root / ".kiro").mkdir(parents=True)
    
    def teardown_method(self):
        """每个测试后的清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_load_modules_function(self):
        """测试 load_modules 便捷函数"""
        # 创建空配置
        config_path = self.project_root / ".kiro" / "config.yaml"
        config = {'version': '2.0', 'modules': {}}
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
        
        success, prompt, result = load_modules(project_root=str(self.project_root))
        
        assert success
        assert isinstance(prompt, str)
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
