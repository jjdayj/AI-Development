# 系统集成指南：动态模块加载器

## 📋 文档信息

**文档版本**: v1.0  
**创建日期**: 2026-03-03  
**状态**: ✅ 可用  
**需求追溯**: 需求 17, 18, 19

## 🎯 集成概述

动态模块加载器作为 Kiro Prompt 基座的核心组件，负责与多个下游模块进行数据交互和功能集成。本文档详细说明了与各个模块的集成方式、数据传递格式和兼容性要求。

### 集成模块

1. **Workflow 模块** - 双轨工作流选择器
2. **Git 提交模块** - Git 提交主题化管理
3. **VibCoding 工作流** - AI 开发自动化管理

## 🔗 与 Workflow 模块的集成

### 集成概述

Workflow 模块是动态加载器的第一个下游模块，负责根据用户需求选择合适的工作流（VibCoding 或 Git 提交）。

### 数据流向

```
动态加载器 → Workflow 模块 → VibCoding/Git 提交模块
```

### 集成方式

#### 1. 模块加载

动态加载器通过以下方式加载 Workflow 模块：

```yaml
# .kiro/config.yaml
modules:
  workflow:
    enabled: true
    version: v1.0
    priority: 200  # 最高优先级
```

#### 2. Steering 规则加载

动态加载器读取 Workflow 模块的 Steering 文件：

```
路径：.kiro/modules/workflow/v1.0/steering/workflow_selector.md
```

#### 3. 版本管理

Workflow 模块支持双版本：
- `v1.0-simple` - 简化版（基础功能）
- `v1.0-complex` - 完整版（高级功能）

切换版本：

```yaml
modules:
  workflow:
    enabled: true
    version: v1.0-simple  # 或 v1.0-complex
    priority: 200
```

### 数据传递

#### 输入数据

动态加载器不直接向 Workflow 模块传递数据，而是通过加载其 Steering 规则来激活功能。

#### 输出数据

Workflow 模块通过 Steering 规则指导 AI 选择工作流，不产生结构化输出数据。

### 兼容性要求

- ✅ 支持 Workflow v1.0 及以上版本
- ✅ 支持双版本切换（simple/complex）
- ✅ 优先级必须设置为 200（最高）
- ✅ 必须在其他功能模块之前加载

### 集成示例

```python
from src.dynamic_loader import DynamicLoader

# 创建加载器
loader = DynamicLoader()

# 执行加载
success, prompt, result = loader.load()

# 验证 Workflow 模块已加载
workflow_loaded = any(m['name'] == 'workflow' for m in result['loaded_modules'])
assert workflow_loaded == True

# 验证 Workflow 模块优先级最高
assert result['loaded_modules'][0]['name'] == 'workflow'
assert result['loaded_modules'][0]['priority'] == 200
```

## 🔗 与 Git 提交模块的集成

### 集成概述

Git 提交模块负责 Git 提交的主题化管理，需要从动态加载器获取当前活跃需求的上下文信息。

### 数据流向

```
动态加载器 → current_context.yaml → Git 提交模块
```

### 集成方式

#### 1. 模块加载

动态加载器通过以下方式加载 Git 提交模块：

```yaml
# .kiro/config.yaml
modules:
  git-commit:
    enabled: true
    version: v1.0
    priority: 80
```

#### 2. 上下文数据传递

动态加载器通过 `current_context.yaml` 文件传递上下文信息：

```yaml
# .kiro/requirements/current_context.yaml
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

#### 3. Git 提交模块读取上下文

Git 提交模块读取 `current_context.yaml` 以获取当前需求信息：

```python
import yaml

# 读取当前上下文
with open('.kiro/requirements/current_context.yaml', 'r', encoding='utf-8') as f:
    context = yaml.safe_load(f)

# 提取需求信息
requirement_id = context['active_requirement']['requirement_id']
requirement_name = context['active_requirement']['requirement_name']

# 生成 Git 提交消息
commit_message = f"feat({requirement_id}): {requirement_name} - 实现核心功能"
```

### 数据格式规范

#### current_context.yaml 格式

```yaml
# 必需字段
active_requirement:
  requirement_id: string      # 需求 ID（kebab-case）
  requirement_name: string    # 需求名称（中文）
  requirement_path: string    # 需求路径（相对路径）

# 必需字段
environment:
  current_directory: string   # 当前目录（相对路径）
  current_file: string        # 当前文件（相对路径）
  current_file_type: string   # 文件类型（如 .py, .md）

# 必需字段
updated_at: string            # 更新时间（ISO 8601 格式）
```

### 兼容性要求

- ✅ current_context.yaml 必须包含所有必需字段
- ✅ requirement_id 必须使用 kebab-case 格式
- ✅ 路径必须使用相对路径（相对于项目根目录）
- ✅ updated_at 必须使用 ISO 8601 格式
- ✅ 文件编码必须为 UTF-8

### 集成示例

```python
from src.context_manager import ContextManager

# 创建上下文管理器
context_mgr = ContextManager()

# 更新当前上下文
context_mgr.update_context(
    requirement_id='dynamic-module-loader',
    requirement_name='动态模块加载器',
    requirement_path='.kiro/specs/dynamic-module-loader',
    current_directory='.kiro/specs/dynamic-module-loader',
    current_file='src/dynamic_loader.py',
    current_file_type='.py'
)

# Git 提交模块读取上下文
context = context_mgr.read_context()
print(f"当前需求: {context['active_requirement']['requirement_name']}")
```

## 🔗 与 VibCoding 工作流的集成

### 集成概述

VibCoding 工作流是 AI 开发自动化管理模块，需要从动态加载器获取当前活跃需求的上下文信息。

### 数据流向

```
动态加载器 → current_context.yaml → VibCoding 工作流
```

### 集成方式

#### 1. 模块加载

动态加载器通过以下方式加载 AI-Dev 模块：

```yaml
# .kiro/config.yaml
modules:
  ai-dev:
    enabled: true
    version: v1.0
    priority: 100
```

#### 2. 上下文数据传递

VibCoding 工作流使用与 Git 提交模块相同的 `current_context.yaml` 格式。

#### 3. VibCoding 工作流读取上下文

```python
import yaml

# 读取当前上下文
with open('.kiro/requirements/current_context.yaml', 'r', encoding='utf-8') as f:
    context = yaml.safe_load(f)

# 提取需求信息
requirement_path = context['active_requirement']['requirement_path']

# 读取需求文档
requirements_file = f"{requirement_path}/requirements.md"
with open(requirements_file, 'r', encoding='utf-8') as f:
    requirements = f.read()
```

### 数据格式规范

VibCoding 工作流使用与 Git 提交模块相同的 `current_context.yaml` 格式（见上文）。

### 兼容性要求

- ✅ current_context.yaml 必须包含所有必需字段
- ✅ requirement_path 必须指向有效的需求目录
- ✅ 需求目录必须包含 requirements.md 文件
- ✅ 文件编码必须为 UTF-8

### 集成示例

```python
from src.context_manager import ContextManager

# 创建上下文管理器
context_mgr = ContextManager()

# 更新当前上下文
context_mgr.update_context(
    requirement_id='dynamic-module-loader',
    requirement_name='动态模块加载器',
    requirement_path='.kiro/specs/dynamic-module-loader',
    current_directory='.kiro/specs/dynamic-module-loader',
    current_file='requirements.md',
    current_file_type='.md'
)

# VibCoding 工作流读取上下文
context = context_mgr.read_context()
requirement_path = context['active_requirement']['requirement_path']
print(f"需求路径: {requirement_path}")
```

## 📊 数据格式兼容性矩阵

| 字段 | Git 提交模块 | VibCoding 工作流 | 格式要求 |
|------|-------------|-----------------|---------|
| requirement_id | ✅ 必需 | ✅ 必需 | kebab-case |
| requirement_name | ✅ 必需 | ✅ 必需 | 中文字符串 |
| requirement_path | ✅ 必需 | ✅ 必需 | 相对路径 |
| current_directory | ✅ 必需 | ✅ 必需 | 相对路径 |
| current_file | ✅ 必需 | ✅ 必需 | 相对路径 |
| current_file_type | ✅ 必需 | ✅ 必需 | 文件扩展名 |
| updated_at | ✅ 必需 | ✅ 必需 | ISO 8601 |

## 🔧 集成测试

### 测试场景 1：Workflow 模块集成测试

```python
def test_workflow_integration():
    """测试 Workflow 模块集成"""
    loader = DynamicLoader()
    success, prompt, result = loader.load()
    
    # 验证 Workflow 模块已加载
    assert success == True
    workflow_module = next((m for m in result['loaded_modules'] if m['name'] == 'workflow'), None)
    assert workflow_module is not None
    
    # 验证优先级
    assert workflow_module['priority'] == 200
    
    # 验证 Steering 内容已加载
    assert 'workflow' in prompt.lower()
```

### 测试场景 2：Git 提交模块集成测试

```python
def test_git_commit_integration():
    """测试 Git 提交模块集成"""
    from src.context_manager import ContextManager
    
    # 更新上下文
    context_mgr = ContextManager()
    context_mgr.update_context(
        requirement_id='test-requirement',
        requirement_name='测试需求',
        requirement_path='.kiro/specs/test',
        current_directory='.kiro/specs/test',
        current_file='test.py',
        current_file_type='.py'
    )
    
    # 读取上下文
    context = context_mgr.read_context()
    
    # 验证格式
    assert 'active_requirement' in context
    assert 'environment' in context
    assert 'updated_at' in context
    
    # 验证必需字段
    assert context['active_requirement']['requirement_id'] == 'test-requirement'
    assert context['active_requirement']['requirement_name'] == '测试需求'
```

### 测试场景 3：VibCoding 工作流集成测试

```python
def test_vibcoding_integration():
    """测试 VibCoding 工作流集成"""
    from src.context_manager import ContextManager
    
    # 更新上下文
    context_mgr = ContextManager()
    context_mgr.update_context(
        requirement_id='dynamic-module-loader',
        requirement_name='动态模块加载器',
        requirement_path='.kiro/specs/dynamic-module-loader',
        current_directory='.kiro/specs/dynamic-module-loader',
        current_file='requirements.md',
        current_file_type='.md'
    )
    
    # 读取上下文
    context = context_mgr.read_context()
    
    # 验证需求路径
    requirement_path = context['active_requirement']['requirement_path']
    assert requirement_path == '.kiro/specs/dynamic-module-loader'
    
    # 验证需求文件存在
    import os
    requirements_file = f"{requirement_path}/requirements.md"
    assert os.path.exists(requirements_file)
```

## 🚨 常见集成问题

### 问题 1：current_context.yaml 格式错误

**症状**：Git 提交模块或 VibCoding 工作流无法读取上下文

**原因**：
- 缺少必需字段
- 字段格式不正确
- 文件编码错误

**解决方案**：
```python
from src.context_manager import ContextManager

# 使用 ContextManager 确保格式正确
context_mgr = ContextManager()
context_mgr.update_context(
    requirement_id='your-requirement-id',
    requirement_name='你的需求名称',
    requirement_path='.kiro/specs/your-requirement',
    current_directory='.kiro/specs/your-requirement',
    current_file='your-file.py',
    current_file_type='.py'
)
```

### 问题 2：Workflow 模块未加载

**症状**：Workflow 模块的 Steering 规则未生效

**原因**：
- enabled: false
- 优先级设置错误
- Steering 文件不存在

**解决方案**：
```yaml
# 检查配置
modules:
  workflow:
    enabled: true      # 确保为 true
    version: v1.0      # 确保版本正确
    priority: 200      # 确保优先级最高
```

### 问题 3：模块加载顺序错误

**症状**：模块功能冲突或规则不生效

**原因**：
- 优先级设置不当
- 模块依赖关系错误

**解决方案**：
```yaml
# 建议的优先级设置
modules:
  workflow:
    priority: 200  # 最高优先级
  ai-dev:
    priority: 100  # 中等优先级
  git-commit:
    priority: 80   # 较低优先级
```

## 📝 集成检查清单

### Workflow 模块集成检查清单

- [ ] Workflow 模块已在 config.yaml 中启用
- [ ] 优先级设置为 200（最高）
- [ ] Steering 文件存在且可读
- [ ] 版本号符合 SemVer 规范
- [ ] 模块成功加载并排在第一位

### Git 提交模块集成检查清单

- [ ] Git 提交模块已在 config.yaml 中启用
- [ ] current_context.yaml 文件存在
- [ ] current_context.yaml 包含所有必需字段
- [ ] requirement_id 使用 kebab-case 格式
- [ ] 路径使用相对路径
- [ ] 文件编码为 UTF-8

### VibCoding 工作流集成检查清单

- [ ] AI-Dev 模块已在 config.yaml 中启用
- [ ] current_context.yaml 文件存在
- [ ] requirement_path 指向有效目录
- [ ] requirements.md 文件存在
- [ ] 文件编码为 UTF-8

## 🔗 相关文档

- **数据格式规范**: `data-format-spec.md`
- **README**: `README.md`
- **测试计划**: `test-plan.md`
- **需求文档**: `requirements.md`
- **设计文档**: `design.md`

---

**文档版本**: v1.0  
**创建日期**: 2026-03-03  
**最后更新**: 2026-03-03  
**状态**: ✅ 可用
