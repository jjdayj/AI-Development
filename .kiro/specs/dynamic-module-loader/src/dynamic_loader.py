"""
动态模块加载器（Dynamic Loader）

本模块是动态模块加载器的主入口，负责整合所有组件，实现完整的模块加载流程。

加载流程（10 个步骤）：
1. 读取顶层配置（.kiro/config.yaml）
2. 筛选启用的模块（enabled: true）
3. 读取模块配置（.kiro/modules/{module}/{version}/config.yaml）
4. 合并配置（处理冲突）
5. 计算激活状态（全局开关 AND 激活条件）
6. 校验依赖关系（检测缺失依赖和循环依赖）
7. 按优先级排序（priority 从高到低）
8. 加载 Steering 文件（.kiro/modules/{module}/{version}/steering/{module}.md）
9. 整合 Prompt 上下文（拼接所有 Steering 内容）
10. 输出加载日志（记录加载过程和结果）

需求追溯：需求 1-15

作者: yangzhuo
日期: 2026-03-03
版本: v1.0
"""

from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

# 导入所有组件
from config_reader import ConfigReader
from activation_calculator import calculate_activation
from dependency_validator import validate_dependencies
from priority_sorter import sort_by_priority
from steering_loader import SteeringLoader
from prompt_integrator import PromptIntegrator
from logger import (
    log_info, log_warning, log_error, log_module_status,
    log_loading_start, log_loading_complete, log_section_separator
)
from config_merger import merge_configs
from context_manager import ContextManager


class DynamicLoader:
    """动态模块加载器
    
    负责整合所有组件，实现完整的模块加载流程。
    """
    
    def __init__(self, project_root: str = None):
        """初始化动态加载器
        
        Args:
            project_root: 项目根目录路径，默认为 None（自动检测）
        """
        # 初始化项目根目录
        if project_root is None:
            # 从当前文件路径计算项目根目录
            current_file = Path(__file__).resolve()
            self.project_root = current_file.parent.parent.parent.parent.parent
        else:
            self.project_root = Path(project_root).resolve()
        
        # 初始化所有组件
        self.config_reader = ConfigReader(str(self.project_root))
        self.steering_loader = SteeringLoader(str(self.project_root / ".kiro" / "modules"))
        self.prompt_integrator = PromptIntegrator()
        self.context_manager = ContextManager(str(self.project_root))
        
        # 加载结果缓存
        self.loaded_modules = []
        self.failed_modules = []
        self.integrated_prompt = ""
    
    def load(self, context: Dict[str, Any] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """执行完整的模块加载流程
        
        Args:
            context: 当前上下文（目录、文件类型等），默认为 None（使用默认上下文）
        
        Returns:
            (是否成功, 整合后的 Prompt 内容, 加载结果详情)
            
            加载结果详情包含：
            - loaded_modules: 成功加载的模块列表
            - failed_modules: 加载失败的模块列表
            - total_count: 总模块数
            - loaded_count: 成功加载数
            - failed_count: 失败数
        
        需求追溯：需求 1-15
        """
        # 如果没有提供上下文，使用默认上下文
        if context is None:
            context = self._get_default_context()
        
        # 步骤 1: 读取顶层配置
        log_info("=" * 60)
        log_info("步骤 1: 读取顶层配置")
        log_info("=" * 60)
        success, top_config, error = self._step1_read_top_config()
        if not success:
            log_error(f"读取顶层配置失败: {error}")
            return False, "", self._create_result_summary()
        
        # 步骤 2: 筛选启用的模块
        log_info("")
        log_info("步骤 2: 筛选启用的模块")
        log_info("-" * 60)
        enabled_modules = self._step2_filter_enabled_modules(top_config)
        if not enabled_modules:
            log_warning("没有启用的模块")
            return True, self._create_empty_prompt(), self._create_result_summary()
        
        # 步骤 3: 读取模块配置
        log_info("")
        log_info("步骤 3: 读取模块配置")
        log_info("-" * 60)
        modules_with_config = self._step3_read_module_configs(enabled_modules)
        
        # 步骤 4: 合并配置
        log_info("")
        log_info("步骤 4: 合并配置")
        log_info("-" * 60)
        merged_modules = self._step4_merge_configs(top_config, modules_with_config)
        
        # 步骤 5: 计算激活状态
        log_info("")
        log_info("步骤 5: 计算激活状态")
        log_info("-" * 60)
        activated_modules = self._step5_calculate_activation(merged_modules, context)
        if not activated_modules:
            log_warning("没有激活的模块")
            return True, self._create_empty_prompt(), self._create_result_summary()
        
        # 步骤 6: 校验依赖关系
        log_info("")
        log_info("步骤 6: 校验依赖关系")
        log_info("-" * 60)
        valid_modules, invalid_modules = self._step6_validate_dependencies(activated_modules)
        if not valid_modules:
            log_warning("所有模块依赖校验失败")
            self.failed_modules = invalid_modules
            return True, self._create_empty_prompt(), self._create_result_summary()
        
        # 步骤 7: 按优先级排序
        log_info("")
        log_info("步骤 7: 按优先级排序")
        log_info("-" * 60)
        sorted_modules = self._step7_sort_by_priority(valid_modules)
        
        # 步骤 8: 加载 Steering 文件
        log_info("")
        log_info("步骤 8: 加载 Steering 文件")
        log_info("-" * 60)
        steering_contents = self._step8_load_steering_files(sorted_modules)
        
        # 步骤 9: 整合 Prompt 上下文
        log_info("")
        log_info("步骤 9: 整合 Prompt 上下文")
        log_info("-" * 60)
        integrated_prompt = self._step9_integrate_prompts(steering_contents)
        
        # 步骤 10: 输出加载日志
        log_info("")
        log_info("步骤 10: 输出加载日志")
        log_info("-" * 60)
        self._step10_output_summary(sorted_modules, invalid_modules)
        
        # 保存加载结果
        self.loaded_modules = sorted_modules
        self.failed_modules = invalid_modules
        self.integrated_prompt = integrated_prompt
        
        # 输出加载完成日志
        log_info("")
        log_info("=" * 60)
        log_info(f"模块加载完成: {len(sorted_modules)} 个成功, {len(invalid_modules)} 个失败")
        log_info("=" * 60)
        
        return True, integrated_prompt, self._create_result_summary()
    
    def _step1_read_top_config(self) -> Tuple[bool, Dict[str, Any], str]:
        """步骤 1: 读取顶层配置
        
        Returns:
            (是否成功, 配置对象, 错误信息)
        """
        log_info("读取顶层配置文件: .kiro/config.yaml")
        success, config, error = self.config_reader.read_config()
        
        if success:
            log_info(f"✓ 配置读取成功，共 {len(config.get('modules', {}))} 个模块")
        else:
            log_error(f"✗ 配置读取失败: {error}")
        
        return success, config, error
    
    def _step2_filter_enabled_modules(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """步骤 2: 筛选启用的模块
        
        Args:
            config: 顶层配置对象
        
        Returns:
            启用的模块列表
        """
        enabled_modules = self.config_reader.get_enabled_modules(config)
        
        log_info(f"筛选结果: {len(enabled_modules)} 个模块启用")
        for module in enabled_modules:
            log_info(f"  ✓ {module['name']} (v{module['version']}) - 优先级: {module['priority']}")
        
        return enabled_modules
    
    def _step3_read_module_configs(self, modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """步骤 3: 读取模块配置
        
        Args:
            modules: 启用的模块列表
        
        Returns:
            包含模块配置的模块列表
        """
        modules_with_config = []
        
        for module in modules:
            module_name = module['name']
            module_version = module['version']
            
            log_info(f"读取模块配置: {module_name} (v{module_version})")
            
            success, module_config, error = self.config_reader.get_module_config(
                module_name, module_version
            )
            
            if success:
                # 将模块配置添加到模块对象中
                module_with_config = module.copy()
                module_with_config['module_config'] = module_config
                modules_with_config.append(module_with_config)
                
                # 输出激活条件
                conditions = module_config.get('activation_conditions', {})
                log_info(f"  激活条件: {conditions}")
            else:
                log_warning(f"  读取模块配置失败: {error}，使用默认配置")
                # 使用默认配置
                module_with_config = module.copy()
                module_with_config['module_config'] = {
                    'activation_conditions': {'always': True}
                }
                modules_with_config.append(module_with_config)
        
        return modules_with_config
    
    def _step4_merge_configs(
        self,
        top_config: Dict[str, Any],
        modules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """步骤 4: 合并配置
        
        Args:
            top_config: 顶层配置
            modules: 包含模块配置的模块列表
        
        Returns:
            合并后的模块列表
        """
        merged_modules = []
        
        for module in modules:
            module_name = module['name']
            
            # 获取顶层配置中的模块配置
            top_module_config = top_config.get('modules', {}).get(module_name, {})
            
            # 获取模块自己的配置
            module_config = module.get('module_config', {})
            
            # 合并配置
            merged_config = merge_configs(top_module_config, module_config, module_name)
            
            # 创建新的模块对象
            merged_module = {
                'name': module_name,
                'version': merged_config.get('version', module['version']),
                'priority': merged_config.get('priority', module['priority']),
                'enabled': merged_config.get('enabled', module['enabled']),
                'activation_conditions': merged_config.get('activation_conditions', {'always': True}),
                'dependencies': merged_config.get('dependencies', []),
                'merged_config': merged_config
            }
            
            merged_modules.append(merged_module)
            log_info(f"✓ 配置合并完成: {module_name}")
        
        return merged_modules
    
    def _step5_calculate_activation(
        self,
        modules: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """步骤 5: 计算激活状态
        
        Args:
            modules: 合并后的模块列表
            context: 当前上下文
        
        Returns:
            激活的模块列表
        """
        activated_modules = []
        
        log_info(f"当前上下文: {context}")
        
        for module in modules:
            module_name = module['name']
            global_switch = module['enabled']
            activation_conditions = module['activation_conditions']
            
            # 计算激活状态
            is_activated = calculate_activation(global_switch, activation_conditions, context)
            
            if is_activated:
                activated_modules.append(module)
                log_info(f"✓ 模块激活: {module_name}")
            else:
                log_info(f"✗ 模块未激活: {module_name}")
        
        log_info(f"激活结果: {len(activated_modules)}/{len(modules)} 个模块激活")
        
        return activated_modules
    
    def _step6_validate_dependencies(
        self,
        modules: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """步骤 6: 校验依赖关系
        
        Args:
            modules: 激活的模块列表
        
        Returns:
            (依赖校验通过的模块列表, 依赖校验失败的模块列表)
        """
        valid_modules, invalid_modules = validate_dependencies(modules)
        
        log_info(f"依赖校验结果: {len(valid_modules)} 个通过, {len(invalid_modules)} 个失败")
        
        # 输出失败的模块
        for item in invalid_modules:
            module = item['module']
            reason = item['reason']
            log_warning(f"✗ {module['name']}: {reason}")
        
        return valid_modules, invalid_modules
    
    def _step7_sort_by_priority(self, modules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """步骤 7: 按优先级排序
        
        Args:
            modules: 模块列表
        
        Returns:
            排序后的模块列表
        """
        sorted_modules = sort_by_priority(modules)
        
        log_info("模块排序完成（按优先级从高到低）:")
        for i, module in enumerate(sorted_modules, 1):
            log_info(f"  {i}. {module['name']} (v{module['version']}) - 优先级: {module['priority']}")
        
        return sorted_modules
    
    def _step8_load_steering_files(
        self,
        modules: List[Dict[str, Any]]
    ) -> List[Tuple[str, str, int, Dict[str, Any], str]]:
        """步骤 8: 加载 Steering 文件
        
        Args:
            modules: 排序后的模块列表
        
        Returns:
            Steering 内容列表，每个元素为 (module_name, version, priority, conditions, content)
        """
        steering_contents = []
        
        for module in modules:
            module_name = module['name']
            module_version = module['version']
            module_priority = module['priority']
            activation_conditions = module['activation_conditions']
            
            log_info(f"加载 Steering 文件: {module_name} (v{module_version})")
            
            # 加载 Steering 文件
            success, content, error = self.steering_loader.load_steering(
                module_name,
                module_version,
                module_priority,
                activation_conditions
            )
            
            if success:
                steering_contents.append((
                    module_name,
                    module_version,
                    module_priority,
                    activation_conditions,
                    content
                ))
                log_info(f"  ✓ Steering 文件加载成功 ({len(content)} 字符)")
            else:
                log_warning(f"  ✗ Steering 文件加载失败: {error}")
        
        log_info(f"Steering 加载结果: {len(steering_contents)}/{len(modules)} 个成功")
        
        return steering_contents
    
    def _step9_integrate_prompts(
        self,
        steering_contents: List[Tuple[str, str, int, Dict[str, Any], str]]
    ) -> str:
        """步骤 9: 整合 Prompt 上下文
        
        Args:
            steering_contents: Steering 内容列表
        
        Returns:
            整合后的 Prompt 内容
        """
        log_info("开始整合 Prompt 上下文")
        
        integrated_prompt = self.prompt_integrator.integrate_prompts(steering_contents)
        
        log_info(f"✓ Prompt 整合完成 ({len(integrated_prompt)} 字符)")
        
        return integrated_prompt
    
    def _step10_output_summary(
        self,
        loaded_modules: List[Dict[str, Any]],
        failed_modules: List[Dict[str, Any]]
    ) -> None:
        """步骤 10: 输出加载日志
        
        Args:
            loaded_modules: 成功加载的模块列表
            failed_modules: 加载失败的模块列表
        """
        log_info("=" * 60)
        log_info("加载摘要")
        log_info("=" * 60)
        log_info(f"总模块数: {len(loaded_modules) + len(failed_modules)}")
        log_info(f"成功加载: {len(loaded_modules)}")
        log_info(f"加载失败: {len(failed_modules)}")
        log_info("")
        
        if loaded_modules:
            log_info("成功加载的模块:")
            for module in loaded_modules:
                log_module_status(module, "已加载")
        
        if failed_modules:
            log_info("")
            log_info("加载失败的模块:")
            for item in failed_modules:
                module = item['module']
                reason = item['reason']
                log_warning(f"  ✗ {module['name']}: {reason}")
        
        log_info("=" * 60)
    
    def _get_default_context(self) -> Dict[str, Any]:
        """获取默认上下文
        
        Returns:
            默认上下文字典
        """
        # 尝试从 current_context.yaml 读取
        try:
            context_data = self.context_manager.read_context()
            
            if context_data and 'environment' in context_data:
                return context_data['environment']
        except Exception:
            # 如果读取失败，忽略错误，使用默认值
            pass
        
        # 如果读取失败，返回默认值
        return {
            'current_directory': str(self.project_root / ".kiro" / "steering"),
            'current_file': 'main.md',
            'current_file_type': '.md'
        }
    
    def _create_empty_prompt(self) -> str:
        """创建空 Prompt
        
        Returns:
            空 Prompt 内容
        """
        return self.prompt_integrator.integrate_prompts([])
    
    def _create_result_summary(self) -> Dict[str, Any]:
        """创建加载结果摘要
        
        Returns:
            加载结果摘要字典
        """
        return {
            'loaded_modules': self.loaded_modules,
            'failed_modules': self.failed_modules,
            'total_count': len(self.loaded_modules) + len(self.failed_modules),
            'loaded_count': len(self.loaded_modules),
            'failed_count': len(self.failed_modules)
        }
    
    def get_loaded_modules(self) -> List[Dict[str, Any]]:
        """获取成功加载的模块列表
        
        Returns:
            成功加载的模块列表
        """
        return self.loaded_modules
    
    def get_failed_modules(self) -> List[Dict[str, Any]]:
        """获取加载失败的模块列表
        
        Returns:
            加载失败的模块列表
        """
        return self.failed_modules
    
    def get_integrated_prompt(self) -> str:
        """获取整合后的 Prompt 内容
        
        Returns:
            整合后的 Prompt 内容
        """
        return self.integrated_prompt


# 便捷函数

def load_modules(context: Dict[str, Any] = None, project_root: str = None) -> Tuple[bool, str, Dict[str, Any]]:
    """加载模块（便捷函数）
    
    Args:
        context: 当前上下文
        project_root: 项目根目录
    
    Returns:
        (是否成功, 整合后的 Prompt 内容, 加载结果详情)
    """
    loader = DynamicLoader(project_root)
    return loader.load(context)


def main():
    """主函数：演示动态加载器的使用"""
    print("=" * 80)
    print("动态模块加载器 - 演示")
    print("=" * 80)
    print()
    
    # 创建加载器
    loader = DynamicLoader()
    
    # 执行加载
    success, prompt, result = loader.load()
    
    if success:
        print()
        print("=" * 80)
        print("加载成功！")
        print("=" * 80)
        print()
        print(f"成功加载 {result['loaded_count']} 个模块")
        print(f"失败 {result['failed_count']} 个模块")
        print()
        
        if result['loaded_modules']:
            print("已加载的模块:")
            for module in result['loaded_modules']:
                print(f"  - {module['name']} (v{module['version']}) - 优先级: {module['priority']}")
        
        print()
        print("=" * 80)
        print("整合后的 Prompt 内容（前 500 字符）:")
        print("=" * 80)
        print(prompt[:500])
        if len(prompt) > 500:
            print(f"\n... (还有 {len(prompt) - 500} 字符)")
    else:
        print()
        print("=" * 80)
        print("加载失败！")
        print("=" * 80)
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
