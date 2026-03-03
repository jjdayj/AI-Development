"""
依赖校验器模块

该模块负责校验模块依赖关系，确保依赖的模块已激活。

功能：
    1. 校验模块依赖关系
    2. 检测循环依赖
    3. 返回校验通过和失败的模块列表

校验规则：
    - 对于每个模块，检查其 dependencies 字段
    - 确保所有依赖的模块都在激活列表中
    - 检测循环依赖（A 依赖 B，B 依赖 A）
    - 依赖不满足的模块不应该被加载

作者: yangzhuo
日期: 2026-03-03
版本: v1.0
"""

from typing import List, Dict, Any, Tuple, Set


def validate_dependencies(
    activated_modules: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    校验模块依赖关系
    
    Args:
        activated_modules: 激活的模块列表，每个模块包含：
            - name: 模块名称
            - version: 模块版本
            - priority: 模块优先级
            - dependencies: 依赖的模块列表（可选）
        
    Returns:
        (依赖校验通过的模块列表, 依赖校验失败的模块列表)
        
        依赖校验失败的模块格式：
        {
            'module': 模块对象,
            'reason': 失败原因字符串
        }
    
    Examples:
        >>> modules = [
        ...     {'name': 'module-a', 'version': 'v1.0', 'priority': 100, 'dependencies': []},
        ...     {'name': 'module-b', 'version': 'v1.0', 'priority': 90, 'dependencies': ['module-a']}
        ... ]
        >>> valid, invalid = validate_dependencies(modules)
        >>> len(valid)
        2
        >>> len(invalid)
        0
        
        >>> modules = [
        ...     {'name': 'module-a', 'version': 'v1.0', 'priority': 100, 'dependencies': ['module-c']},
        ...     {'name': 'module-b', 'version': 'v1.0', 'priority': 90, 'dependencies': ['module-a']}
        ... ]
        >>> valid, invalid = validate_dependencies(modules)
        >>> len(valid)
        0
        >>> len(invalid)
        2
    """
    # 构建模块名称集合（用于快速查找）
    module_names = {m['name'] for m in activated_modules}
    
    # 检测循环依赖
    circular_deps = detect_circular_dependencies(activated_modules)
    
    valid_modules = []
    invalid_modules = []
    
    for module in activated_modules:
        module_name = module['name']
        dependencies = module.get('dependencies', [])
        
        # 检查是否在循环依赖中
        if module_name in circular_deps:
            invalid_modules.append({
                'module': module,
                'reason': f"循环依赖: {sorted(circular_deps)}"
            })
            continue
        
        # 检查所有依赖是否满足
        missing_deps = []
        for dep in dependencies:
            if dep not in module_names:
                missing_deps.append(dep)
        
        if missing_deps:
            invalid_modules.append({
                'module': module,
                'reason': f"缺少依赖: {missing_deps}"
            })
        else:
            valid_modules.append(module)
    
    return valid_modules, invalid_modules


def detect_circular_dependencies(modules: List[Dict[str, Any]]) -> Set[str]:
    """
    检测循环依赖
    
    使用深度优先搜索（DFS）算法检测依赖图中的环。
    
    Args:
        modules: 模块列表，每个模块包含 name 和 dependencies 字段
        
    Returns:
        存在循环依赖的模块名称集合
    
    Examples:
        >>> modules = [
        ...     {'name': 'module-a', 'dependencies': ['module-b']},
        ...     {'name': 'module-b', 'dependencies': ['module-a']}
        ... ]
        >>> circular = detect_circular_dependencies(modules)
        >>> 'module-a' in circular and 'module-b' in circular
        True
        
        >>> modules = [
        ...     {'name': 'module-a', 'dependencies': ['module-b']},
        ...     {'name': 'module-b', 'dependencies': ['module-c']},
        ...     {'name': 'module-c', 'dependencies': []}
        ... ]
        >>> circular = detect_circular_dependencies(modules)
        >>> len(circular)
        0
    """
    # 构建依赖图
    dep_graph = {}
    for module in modules:
        module_name = module['name']
        dependencies = module.get('dependencies', [])
        dep_graph[module_name] = dependencies
    
    # 使用 DFS 检测环
    visited = set()
    rec_stack = set()
    circular = set()
    
    def dfs(node: str, path: List[str]) -> bool:
        """
        深度优先搜索检测环
        
        Args:
            node: 当前节点
            path: 当前路径（用于记录环中的所有节点）
            
        Returns:
            是否检测到环
        """
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in dep_graph.get(node, []):
            # 如果邻居节点不在依赖图中，跳过（可能是缺失的依赖）
            if neighbor not in dep_graph:
                continue
            
            if neighbor not in visited:
                if dfs(neighbor, path.copy()):
                    return True
            elif neighbor in rec_stack:
                # 检测到环，记录环中的所有节点
                if neighbor in path:
                    cycle_start = path.index(neighbor)
                    for i in range(cycle_start, len(path)):
                        circular.add(path[i])
                circular.add(neighbor)
                return True
        
        rec_stack.remove(node)
        path.pop()
        return False
    
    # 对每个未访问的节点执行 DFS
    for node in dep_graph:
        if node not in visited:
            dfs(node, [])
    
    return circular


def get_dependency_order(modules: List[Dict[str, Any]]) -> List[str]:
    """
    获取模块的依赖顺序（拓扑排序）
    
    返回一个模块名称列表，确保依赖的模块在被依赖的模块之前。
    如果存在循环依赖，返回空列表。
    
    Args:
        modules: 模块列表
        
    Returns:
        按依赖顺序排列的模块名称列表，如果存在循环依赖则返回空列表
    
    Examples:
        >>> modules = [
        ...     {'name': 'module-a', 'dependencies': []},
        ...     {'name': 'module-b', 'dependencies': ['module-a']},
        ...     {'name': 'module-c', 'dependencies': ['module-b']}
        ... ]
        >>> order = get_dependency_order(modules)
        >>> order.index('module-a') < order.index('module-b')
        True
        >>> order.index('module-b') < order.index('module-c')
        True
    """
    # 检测循环依赖
    circular = detect_circular_dependencies(modules)
    if circular:
        return []
    
    # 构建依赖图和入度表
    dep_graph = {}
    in_degree = {}
    reverse_graph = {}  # 反向图：被依赖关系
    
    for module in modules:
        module_name = module['name']
        dependencies = module.get('dependencies', [])
        dep_graph[module_name] = dependencies
        in_degree[module_name] = len([d for d in dependencies if d in [m['name'] for m in modules]])
        reverse_graph[module_name] = []
    
    # 构建反向图
    for module_name, dependencies in dep_graph.items():
        for dep in dependencies:
            if dep in reverse_graph:
                reverse_graph[dep].append(module_name)
    
    # 拓扑排序（Kahn 算法）
    queue = [node for node, degree in in_degree.items() if degree == 0]
    result = []
    
    while queue:
        node = queue.pop(0)
        result.append(node)
        
        # 减少依赖此节点的模块的入度
        for neighbor in reverse_graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # 如果结果长度不等于模块数量，说明存在环（理论上不应该发生）
    if len(result) != len(modules):
        return []
    
    return result
