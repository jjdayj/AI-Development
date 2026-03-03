# 数据格式规范：动态模块加载器

## 📋 文档信息

**文档版本**: v1.0  
**创建日期**: 2026-03-03  
**状态**: ✅ 可用  
**需求追溯**: 需求 17, 18, 19

## 🎯 规范目的

本文档定义了动态模块加载器使用的所有数据格式规范，确保系统内部和与下游模块之间的数据交换标准化、一致性和兼容性。

## 📊 数据格式概览

动态模块加载器涉及以下数据格式：

1. **顶层配置格式** - `.kiro/config.yaml`
2. **模块配置格式** - `.kiro/modules/{module}/{version}/config.yaml`
3. **当前上下文格式** - `.kiro/requirements/current_context.yaml`
4. **Steering 加载结果格式** - Python 字典格式

## 1. 顶层配置格式

### 文件路径

```
.kiro/config.yaml
```

### 格式规范

```yaml
# 配置文件版本（必需）
version: string  # 格式："{major}.{minor}"，如 "2.0"

# 模块配置（必需）
modules:
  {module_name}:
    enabled: boolean      # 全局开关（必需）
    version: string       # 模块版本（必需，符合 SemVer 2.0.0）
    priority: integer     # 优先级（必需，数字越大优先级越高）
```

### 完整示例

```yaml
version: "2.0"

modules:
  workflow:
    enabled: true
    version: v1.0
    priority: 200
  
  ai-dev:
    enabled: true
    version: v1.0
    priority: 100
  
  git-commit:
    enabled: true
    version: v1.0
    priority: 80
  
  doc-save:
    enabled: false
    version: v1.0
    priority: 90
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| version | string | ✅ | 配置文件版本 | "2.0" |
| modules | object | ✅ | 模块配置对象 | - |
| modules.{name}.enabled | boolean | ✅ | 全局开关 | true/false |
| modules.{name}.version | string | ✅ | 模块版本（SemVer） | "v1.0", "v1.0-simple" |
| modules.{name}.priority | integer | ✅ | 优先级（0-999） | 200 |

### 验证规则

1. **version 字段**：
   - 必须存在
   - 格式：`"{major}.{minor}"`
   - 示例：`"2.0"`, `"1.0"`

2. **modules 字段**：
   - 必须存在
   - 至少包含一个模块配置

3. **enabled 字段**：
   - 必须存在
   - 类型：boolean
   - 值：`true` 或 `false`

4. **version 字段**（模块版本）：
   - 必须存在
   - 符合 SemVer 2.0.0 规范
   - 格式：`v{major}.{minor}.{patch}[-variant]`
   - 示例：`v1.0.0`, `v1.0-simple`, `v2.1.3-alpha.1`

5. **priority 字段**：
   - 必须存在
   - 类型：integer
   - 范围：0-999
   - 建议：200-300（核心模块），100-199（功能模块），50-99（辅助模块）

## 2. 模块配置格式

### 文件路径

```
.kiro/modules/{module}/{version}/config.yaml
```

### 格式规范

```yaml
# 激活条件（可选，默认 always: true）
activation_conditions:
  # 方式 1：始终激活
  always: boolean
  
  # 方式 2：目录匹配
  directory_match:
    - string  # 支持通配符 * 和 **
  
  # 方式 3：文件类型匹配
  file_type_match:
    - string  # 文件扩展名，如 ".md", ".py"
  
  # 方式 4：AND 逻辑组合
  and:
    - condition_object
  
  # 方式 5：OR 逻辑组合
  or:
    - condition_object

# 模块依赖（可选）
dependencies:
  - string  # 依赖的模块名称

# 模块特定配置（可选）
module_specific_config:
  {key}: {value}
```

### 完整示例

```yaml
# 示例 1：始终激活
activation_conditions:
  always: true

# 示例 2：目录匹配
activation_conditions:
  directory_match:
    - ".kiro/steering/*"
    - "doc/project/**/*"

# 示例 3：文件类型匹配
activation_conditions:
  file_type_match:
    - ".md"
    - ".yaml"

# 示例 4：AND 逻辑组合
activation_conditions:
  and:
    - directory_match:
        - ".kiro/steering/*"
    - file_type_match:
        - ".md"

# 示例 5：OR 逻辑组合
activation_conditions:
  or:
    - directory_match:
        - ".kiro/steering/*"
    - file_type_match:
        - ".yaml"

# 示例 6：带依赖的配置
activation_conditions:
  always: true

dependencies:
  - module-a
  - module-b

module_specific_config:
  custom_field: value
  nested:
    field: value
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| activation_conditions | object | ❌ | 激活条件（默认 always: true） | - |
| activation_conditions.always | boolean | ❌ | 始终激活 | true |
| activation_conditions.directory_match | array | ❌ | 目录匹配模式 | [".kiro/*"] |
| activation_conditions.file_type_match | array | ❌ | 文件类型匹配 | [".md"] |
| activation_conditions.and | array | ❌ | AND 逻辑组合 | - |
| activation_conditions.or | array | ❌ | OR 逻辑组合 | - |
| dependencies | array | ❌ | 依赖的模块列表 | ["module-a"] |
| module_specific_config | object | ❌ | 模块特定配置 | - |

### 验证规则

1. **activation_conditions 字段**：
   - 可选，默认为 `always: true`
   - 只能包含一个顶层条件类型（always, directory_match, file_type_match, and, or）

2. **directory_match 模式**：
   - 支持通配符：`*`（单层）和 `**`（多层）
   - 示例：`.kiro/steering/*`, `doc/**/*`

3. **file_type_match 模式**：
   - 必须以 `.` 开头
   - 示例：`.md`, `.py`, `.yaml`

4. **and/or 逻辑**：
   - 必须包含至少 2 个子条件
   - 支持嵌套

5. **dependencies 字段**：
   - 可选
   - 依赖的模块必须存在且已启用
   - 不允许循环依赖

## 3. 当前上下文格式

### 文件路径

```
.kiro/requirements/current_context.yaml
```

### 格式规范

```yaml
# 活跃需求信息（必需）
active_requirement:
  requirement_id: string      # 需求 ID（kebab-case）
  requirement_name: string    # 需求名称（中文）
  requirement_path: string    # 需求路径（相对路径）

# 环境信息（必需）
environment:
  current_directory: string   # 当前目录（相对路径）
  current_file: string        # 当前文件（相对路径）
  current_file_type: string   # 文件类型（扩展名）

# 更新时间（必需）
updated_at: string            # ISO 8601 格式
```

### 完整示例

```yaml
active_requirement:
  requirement_id: "dynamic-module-loader"
  requirement_name: "动态模块加载器"
  requirement_path: ".kiro/specs/dynamic-module-loader"

environment:
  current_directory: ".kiro/specs/dynamic-module-loader"
  current_file: "src/dynamic_loader.py"
  current_file_type: ".py"

updated_at: "2026-03-03T10:30:00Z"
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 | 示例 |
|------|------|------|------|------|
| active_requirement | object | ✅ | 活跃需求信息 | - |
| active_requirement.requirement_id | string | ✅ | 需求 ID（kebab-case） | "dynamic-module-loader" |
| active_requirement.requirement_name | string | ✅ | 需求名称（中文） | "动态模块加载器" |
| active_requirement.requirement_path | string | ✅ | 需求路径（相对路径） | ".kiro/specs/..." |
| environment | object | ✅ | 环境信息 | - |
| environment.current_directory | string | ✅ | 当前目录（相对路径） | ".kiro/specs/..." |
| environment.current_file | string | ✅ | 当前文件（相对路径） | "src/file.py" |
| environment.current_file_type | string | ✅ | 文件类型（扩展名） | ".py" |
| updated_at | string | ✅ | 更新时间（ISO 8601） | "2026-03-03T10:30:00Z" |

### 验证规则

1. **requirement_id 字段**：
   - 必须存在
   - 格式：kebab-case（小写字母、数字、连字符）
   - 示例：`dynamic-module-loader`, `git-commit-automation`

2. **requirement_name 字段**：
   - 必须存在
   - 类型：string（支持中文）
   - 示例：`动态模块加载器`, `Git 提交自动化`

3. **requirement_path 字段**：
   - 必须存在
   - 格式：相对路径（相对于项目根目录）
   - 示例：`.kiro/specs/dynamic-module-loader`

4. **current_directory 字段**：
   - 必须存在
   - 格式：相对路径
   - 示例：`.kiro/specs/dynamic-module-loader`

5. **current_file 字段**：
   - 必须存在
   - 格式：相对路径
   - 示例：`src/dynamic_loader.py`

6. **current_file_type 字段**：
   - 必须存在
   - 格式：文件扩展名（以 `.` 开头）
   - 示例：`.py`, `.md`, `.yaml`

7. **updated_at 字段**：
   - 必须存在
   - 格式：ISO 8601（`YYYY-MM-DDTHH:MM:SSZ`）
   - 示例：`2026-03-03T10:30:00Z`

## 4. Steering 加载结果格式

### 格式规范

```python
{
    'success': boolean,           # 加载是否成功
    'prompt': string,             # 整合后的 Prompt 内容
    'result': {
        'loaded_count': integer,  # 成功加载的模块数量
        'failed_count': integer,  # 加载失败的模块数量
        'loaded_modules': [       # 成功加载的模块列表
            {
                'name': string,           # 模块名称
                'version': string,        # 模块版本
                'priority': integer,      # 模块优先级
                'steering_path': string,  # Steering 文件路径
                'steering_content': string # Steering 文件内容
            }
        ],
        'failed_modules': [       # 加载失败的模块列表
            {
                'module': {
                    'name': string,       # 模块名称
                    'version': string,    # 模块版本
                    'priority': integer   # 模块优先级
                },
                'reason': string          # 失败原因
            }
        ]
    }
}
```

### 完整示例

```python
{
    'success': True,
    'prompt': '# Kiro Prompt 层级结构\n\nL0: 顶层入口 Prompt...',
    'result': {
        'loaded_count': 3,
        'failed_count': 0,
        'loaded_modules': [
            {
                'name': 'workflow',
                'version': 'v1.0',
                'priority': 200,
                'steering_path': '.kiro/modules/workflow/v1.0/steering/workflow_selector.md',
                'steering_content': '# Workflow 选择器\n\n...'
            },
            {
                'name': 'ai-dev',
                'version': 'v1.0',
                'priority': 100,
                'steering_path': '.kiro/modules/ai-dev/v1.0/steering/ai_dev.md',
                'steering_content': '# AI 开发自动化\n\n...'
            },
            {
                'name': 'git-commit',
                'version': 'v1.0',
                'priority': 80,
                'steering_path': '.kiro/modules/git-commit/v1.0/steering/git_commit.md',
                'steering_content': '# Git 提交管理\n\n...'
            }
        ],
        'failed_modules': []
    }
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 加载是否成功 |
| prompt | string | 整合后的 Prompt 内容 |
| result.loaded_count | integer | 成功加载的模块数量 |
| result.failed_count | integer | 加载失败的模块数量 |
| result.loaded_modules | array | 成功加载的模块列表 |
| result.failed_modules | array | 加载失败的模块列表 |

## 🔧 格式校验工具

### Python 校验函数

#### 1. 校验顶层配置格式

```python
def validate_top_level_config(config: dict) -> tuple[bool, str]:
    """
    校验顶层配置格式
    
    Args:
        config: 配置字典
        
    Returns:
        (是否有效, 错误信息)
    """
    # 检查 version 字段
    if 'version' not in config:
        return False, "缺少 version 字段"
    
    # 检查 modules 字段
    if 'modules' not in config:
        return False, "缺少 modules 字段"
    
    # 检查每个模块配置
    for module_name, module_config in config['modules'].items():
        # 检查必需字段
        required_fields = ['enabled', 'version', 'priority']
        for field in required_fields:
            if field not in module_config:
                return False, f"模块 {module_name} 缺少 {field} 字段"
        
        # 检查字段类型
        if not isinstance(module_config['enabled'], bool):
            return False, f"模块 {module_name} 的 enabled 字段必须是 boolean"
        
        if not isinstance(module_config['priority'], int):
            return False, f"模块 {module_name} 的 priority 字段必须是 integer"
    
    return True, ""
```

#### 2. 校验当前上下文格式

```python
def validate_current_context(context: dict) -> tuple[bool, str]:
    """
    校验当前上下文格式
    
    Args:
        context: 上下文字典
        
    Returns:
        (是否有效, 错误信息)
    """
    # 检查顶层字段
    required_top_fields = ['active_requirement', 'environment', 'updated_at']
    for field in required_top_fields:
        if field not in context:
            return False, f"缺少 {field} 字段"
    
    # 检查 active_requirement 字段
    required_req_fields = ['requirement_id', 'requirement_name', 'requirement_path']
    for field in required_req_fields:
        if field not in context['active_requirement']:
            return False, f"active_requirement 缺少 {field} 字段"
    
    # 检查 environment 字段
    required_env_fields = ['current_directory', 'current_file', 'current_file_type']
    for field in required_env_fields:
        if field not in context['environment']:
            return False, f"environment 缺少 {field} 字段"
    
    # 检查 requirement_id 格式（kebab-case）
    import re
    requirement_id = context['active_requirement']['requirement_id']
    if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', requirement_id):
        return False, f"requirement_id 必须使用 kebab-case 格式"
    
    # 检查 updated_at 格式（ISO 8601）
    updated_at = context['updated_at']
    if not re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$', updated_at):
        return False, f"updated_at 必须使用 ISO 8601 格式"
    
    return True, ""
```

### 使用示例

```python
import yaml

# 读取配置文件
with open('.kiro/config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 校验格式
valid, error = validate_top_level_config(config)
if not valid:
    print(f"配置格式错误: {error}")
else:
    print("配置格式正确")
```

## 📊 格式兼容性检查清单

### 顶层配置检查清单

- [ ] version 字段存在且格式正确
- [ ] modules 字段存在且至少包含一个模块
- [ ] 每个模块包含 enabled, version, priority 字段
- [ ] enabled 字段为 boolean 类型
- [ ] version 字段符合 SemVer 2.0.0 规范
- [ ] priority 字段为 integer 类型且在 0-999 范围内

### 模块配置检查清单

- [ ] activation_conditions 字段格式正确（如果存在）
- [ ] directory_match 模式使用正确的通配符
- [ ] file_type_match 模式以 `.` 开头
- [ ] and/or 逻辑包含至少 2 个子条件
- [ ] dependencies 字段为数组类型（如果存在）
- [ ] 无循环依赖

### 当前上下文检查清单

- [ ] active_requirement 字段存在且包含所有必需字段
- [ ] environment 字段存在且包含所有必需字段
- [ ] updated_at 字段存在且格式正确
- [ ] requirement_id 使用 kebab-case 格式
- [ ] 所有路径使用相对路径
- [ ] current_file_type 以 `.` 开头
- [ ] 文件编码为 UTF-8

## 🔗 相关文档

- **系统集成指南**: `integration-guide.md`
- **README**: `README.md`
- **测试计划**: `test-plan.md`
- **需求文档**: `requirements.md`
- **设计文档**: `design.md`

---

**文档版本**: v1.0  
**创建日期**: 2026-03-03  
**最后更新**: 2026-03-03  
**状态**: ✅ 可用
