# Kiro 主入口 Prompt

## 🎯 功能说明

本文件是 Kiro Prompt 基座的主入口，负责：
1. 读取全局配置（`.kiro/config.yaml`）
2. 根据模块开关动态加载模块 Steering
3. 管理模块优先级，避免冲突

## 📋 动态加载器执行流程

当 Kiro AI 启动时，请按照以下 10 个步骤执行动态模块加载：

### 步骤 1：读取顶层配置

读取配置文件 `.kiro/config.yaml`，提取以下信息：
- `modules` 字段：所有模块的配置
- 每个模块的 `enabled` 字段：全局开关
- 每个模块的 `version` 字段：模块版本
- 每个模块的 `priority` 字段：优先级（数字越大优先级越高）

**配置示例：**
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
```

**错误处理：**
- 如果配置文件不存在，输出错误信息并使用空模块列表
- 如果 YAML 格式错误，输出错误详情并使用空模块列表

### 步骤 2：筛选启用的模块

遍历所有模块配置，只保留 `enabled: true` 的模块。

**示例：**
```
输入：workflow (enabled: true), ai-dev (enabled: true), doc-save (enabled: false)
输出：workflow, ai-dev
```

### 步骤 3：读取模块配置

对于每个启用的模块，读取其配置文件：
```
路径：.kiro/modules/{module}/{version}/config.yaml
```

提取以下信息：
- `activation_conditions`：激活条件
- `dependencies`：依赖的其他模块
- `module_specific_config`：模块特定配置

**配置示例：**
```yaml
activation_conditions:
  always: true

dependencies:
  - module-a

module_specific_config:
  custom_field: value
```

**错误处理：**
- 如果模块配置不存在，使用默认配置（`always: true`）
- 如果 YAML 格式错误，使用默认配置

### 步骤 4：合并配置

将顶层配置和模块配置合并，遵循以下规则：
- 顶层配置优先级更高
- 模块配置作为补充
- 嵌套字典进行深度合并

**合并示例：**
```
顶层配置：{enabled: true, priority: 200}
模块配置：{activation_conditions: {always: true}, custom: value}
合并结果：{enabled: true, priority: 200, activation_conditions: {always: true}, custom: value}
```

### 步骤 5：计算激活状态

对于每个模块，计算最终激活状态：
```
激活状态 = 全局开关 AND 激活条件匹配
```

**激活条件类型：**
1. `always: true` - 始终激活
2. `directory_match: [patterns]` - 当前目录匹配任一模式
3. `file_type_match: [extensions]` - 当前文件类型匹配任一扩展名
4. `and: [conditions]` - 所有子条件都满足
5. `or: [conditions]` - 任一子条件满足

**示例：**
```yaml
# 示例 1：始终激活
activation_conditions:
  always: true

# 示例 2：在 Steering 目录下激活
activation_conditions:
  directory_match:
    - ".kiro/steering/*"
    - ".kiro/modules/*/steering/*"

# 示例 3：Markdown 文件激活
activation_conditions:
  file_type_match:
    - ".md"

# 示例 4：AND 逻辑
activation_conditions:
  and:
    - directory_match: [".kiro/steering/*"]
    - file_type_match: [".md"]

# 示例 5：OR 逻辑
activation_conditions:
  or:
    - directory_match: [".kiro/steering/*"]
    - file_type_match: [".yaml"]
```

### 步骤 6：校验依赖关系

检查每个激活模块的依赖：
1. 确保所有依赖的模块都在激活列表中
2. 检测循环依赖（A 依赖 B，B 依赖 A）
3. 依赖不满足的模块不应该被加载

**错误处理：**
- 缺失依赖：输出警告，跳过该模块
- 循环依赖：输出错误，跳过所有涉及的模块

### 步骤 7：按优先级排序

将通过依赖校验的模块按以下规则排序：
1. 按 `priority` 从高到低排序
2. 如果 `priority` 相同，按模块名称字母顺序排序

**示例：**
```
输入：git-commit (80), workflow (200), ai-dev (100)
输出：workflow (200), ai-dev (100), git-commit (80)
```

### 步骤 8：加载 Steering 文件

按排序后的顺序，加载每个模块的 Steering 文件：

**路径规则：**
```
标准路径：.kiro/modules/{module}/{version}/steering/{module}.md
特殊情况：workflow 模块使用 workflow_selector.md
```

**示例：**
- workflow: `.kiro/modules/workflow/v1.0/steering/workflow_selector.md`
- ai-dev: `.kiro/modules/ai-dev/v1.0/steering/ai_dev.md`
- git-commit: `.kiro/modules/git-commit/v1.0/steering/git_commit.md`

**错误处理：**
- 如果 Steering 文件不存在，输出警告并跳过该模块
- 如果文件读取失败，输出错误并继续处理下一个模块

### 步骤 9：整合 Prompt 上下文

将所有加载的 Steering 内容整合为完整的 Prompt 上下文：

1. 添加层级结构说明
2. 添加激活模块列表
3. 按优先级顺序拼接 Steering 内容
4. 添加模块标识注释

**输出格式：**
```markdown
# Kiro Prompt 层级结构

L0: 顶层入口 Prompt (.kiro/steering/main.md)
  └─ L1: 动态模块加载器
      └─ L2: 激活的模块 Steering 规则

## 当前激活的模块

- workflow (v1.0) - 优先级: 200
- ai-dev (v1.0) - 优先级: 100
- git-commit (v1.0) - 优先级: 80

## 冲突处理规则

- 优先级高的模块规则优先
- 优先级相同时，字母顺序靠前的模块规则优先

---

<!-- Module: workflow | Version: v1.0 | Priority: 200 -->
[workflow Steering 内容]

---

<!-- Module: ai-dev | Version: v1.0 | Priority: 100 -->
[ai-dev Steering 内容]

---

<!-- Module: git-commit | Version: v1.0 | Priority: 80 -->
[git-commit Steering 内容]
```

### 步骤 10：输出加载日志

输出清晰的加载日志，包含：
- 加载开始标题
- 每个模块的详细信息（名称、版本、优先级、激活状态）
- 加载完成摘要（总数、成功数、失败数）

**日志示例：**
```
[INFO] [DynamicLoader] ============================================================
[INFO] [DynamicLoader] 步骤 1: 读取顶层配置
[INFO] [DynamicLoader] ============================================================
[INFO] [DynamicLoader] 读取顶层配置文件: .kiro/config.yaml
[INFO] [DynamicLoader] ✓ 配置读取成功，共 4 个模块

[INFO] [DynamicLoader] 步骤 2: 筛选启用的模块
[INFO] [DynamicLoader] ------------------------------------------------------------
[INFO] [DynamicLoader] 筛选结果: 3 个模块启用
[INFO] [DynamicLoader]   ✓ workflow (v1.0) - 优先级: 200
[INFO] [DynamicLoader]   ✓ ai-dev (v1.0) - 优先级: 100
[INFO] [DynamicLoader]   ✓ git-commit (v1.0) - 优先级: 80

...

[INFO] [DynamicLoader] ============================================================
[INFO] [DynamicLoader] 模块加载完成: 3 个成功, 0 个失败
[INFO] [DynamicLoader] ============================================================
```

## 🔧 当前启用的模块

根据 `.kiro/config.yaml` 的配置，当前启用的模块：

1. **workflow** (v1.0) - 优先级: 200
   - 功能：双轨工作流选择器
   - Steering: `.kiro/modules/workflow/v1.0/steering/workflow_selector.md`

2. **ai-dev** (v1.0) - 优先级: 100
   - 功能：AI 开发自动化管理
   - Steering: `.kiro/modules/ai-dev/v1.0/steering/ai_dev.md`

3. **git-commit** (v1.0) - 优先级: 80
   - 功能：Git 提交主题化管理
   - Steering: `.kiro/modules/git-commit/v1.0/steering/git_commit.md`

4. **git-rollback** (v1.0) - 优先级: 70
   - 功能：Git 回滚功能
   - Steering: `.kiro/modules/git-rollback/v1.0/steering/git_rollback.md`

## 📝 使用指南

### 1. 如何启用/禁用模块

编辑 `.kiro/config.yaml`，修改模块的 `enabled` 字段：

```yaml
modules:
  workflow:
    enabled: true   # 启用模块
    version: v1.0
    priority: 200
  
  doc-save:
    enabled: false  # 禁用模块
    version: v1.0
    priority: 90
```

**说明：**
- `enabled: true` - 模块启用，会进入后续的激活条件判断
- `enabled: false` - 模块禁用，直接跳过，不会加载

**使用场景：**
- 临时禁用某个模块进行调试
- 在不同环境下使用不同的模块组合
- 快速切换功能集

### 2. 如何配置激活条件

编辑模块的配置文件 `.kiro/modules/{module}/{version}/config.yaml`：

**场景 1：始终激活**
```yaml
activation_conditions:
  always: true
```

**场景 2：在特定目录下激活**
```yaml
activation_conditions:
  directory_match:
    - ".kiro/steering/*"
    - ".kiro/modules/*/steering/*"
    - "doc/project/**/*"
```

**场景 3：处理特定文件类型时激活**
```yaml
activation_conditions:
  file_type_match:
    - ".md"
    - ".yaml"
    - ".json"
```

**场景 4：组合条件（AND 逻辑）**
```yaml
activation_conditions:
  and:
    - directory_match: [".kiro/steering/*"]
    - file_type_match: [".md"]
```

**场景 5：组合条件（OR 逻辑）**
```yaml
activation_conditions:
  or:
    - directory_match: [".kiro/steering/*"]
    - file_type_match: [".yaml", ".json"]
```

**场景 6：复杂嵌套条件**
```yaml
activation_conditions:
  or:
    - and:
        - directory_match: [".kiro/steering/*"]
        - file_type_match: [".md"]
    - directory_match: ["doc/project/*"]
```

**通配符说明：**
- `*` - 匹配单层目录或文件名
- `**` - 匹配多层目录
- 示例：`.kiro/steering/*` 匹配 `.kiro/steering/main.md`
- 示例：`doc/**/*` 匹配 `doc/project/architecture/design.md`

### 3. 如何管理模块依赖

编辑模块的配置文件，添加 `dependencies` 字段：

```yaml
activation_conditions:
  always: true

dependencies:
  - module-a
  - module-b
```

**依赖规则：**
1. 依赖的模块必须在激活列表中
2. 如果依赖缺失，当前模块不会被加载
3. 系统会自动检测循环依赖

**示例：模块依赖链**
```yaml
# module-a/config.yaml
dependencies: []  # 无依赖

# module-b/config.yaml
dependencies:
  - module-a  # 依赖 module-a

# module-c/config.yaml
dependencies:
  - module-b  # 依赖 module-b（间接依赖 module-a）
```

**错误处理：**
- 缺失依赖：系统输出警告，跳过该模块
- 循环依赖：系统输出错误，跳过所有涉及的模块

### 4. 如何调整模块优先级

编辑 `.kiro/config.yaml`，修改模块的 `priority` 字段：

```yaml
modules:
  workflow:
    enabled: true
    version: v1.0
    priority: 200  # 最高优先级
  
  ai-dev:
    enabled: true
    version: v1.0
    priority: 100  # 中等优先级
  
  git-commit:
    enabled: true
    version: v1.0
    priority: 80   # 较低优先级
```

**优先级规则：**
- 数字越大，优先级越高
- 优先级高的模块先加载
- 优先级高的模块规则优先生效
- 如果优先级相同，按模块名称字母顺序

**使用场景：**
- 确保核心模块先加载
- 控制规则冲突时的优先级
- 调整模块加载顺序

**建议的优先级范围：**
- 200-300：核心工作流模块
- 100-199：功能模块
- 50-99：辅助模块
- 1-49：可选模块

### 5. 如何切换模块版本

编辑 `.kiro/config.yaml`，修改模块的 `version` 字段：

```yaml
modules:
  workflow:
    enabled: true
    version: v1.0-simple  # 使用简化版
    priority: 200
  
  # 或者
  workflow:
    enabled: true
    version: v1.0-complex  # 使用复杂版
    priority: 200
```

**版本管理规则：**
- 版本号遵循语义化版本 2.0.0 规范
- 格式：`v{major}.{minor}.{patch}[-variant]`
- 示例：`v1.0.0`, `v1.0-simple`, `v2.1.3-alpha`

**使用场景：**
- 在简化版和完整版之间切换
- 测试新版本功能
- 回退到稳定版本

**注意事项：**
- 切换版本前确保目标版本目录存在
- 不同版本可能有不同的配置选项
- 建议先在测试环境验证新版本

### 6. 如何查看加载日志

动态加载器会输出详细的加载日志，包含：

**日志级别：**
- `[INFO]` - 正常信息
- `[WARNING]` - 警告信息（模块跳过、配置缺失等）
- `[ERROR]` - 错误信息（配置错误、依赖问题等）

**日志内容：**
- 配置读取结果
- 模块筛选结果
- 激活状态计算
- 依赖校验结果
- 加载顺序
- Steering 文件加载状态
- 最终加载摘要

**如何使用日志：**
1. 检查模块是否被正确启用
2. 确认激活条件是否匹配
3. 排查依赖问题
4. 验证加载顺序
5. 定位配置错误

### 7. 常见问题排查

**问题 1：模块没有被加载**

可能原因：
1. `enabled: false` - 检查全局开关
2. 激活条件不匹配 - 检查当前上下文
3. 依赖缺失 - 检查依赖模块是否启用
4. 循环依赖 - 检查依赖关系
5. Steering 文件不存在 - 检查文件路径

**问题 2：模块加载顺序不对**

可能原因：
1. 优先级设置错误 - 检查 `priority` 值
2. 优先级相同 - 按字母顺序排序

**问题 3：配置不生效**

可能原因：
1. 配置文件路径错误
2. YAML 格式错误
3. 配置合并规则（顶层配置优先）

**问题 4：依赖校验失败**

可能原因：
1. 依赖的模块未启用
2. 依赖的模块激活条件不匹配
3. 存在循环依赖

## 🔗 相关文档

- 全局配置: `.kiro/config.yaml`
- 模块目录: `.kiro/modules/`
- 模板文件: `.kiro/templates/`
- 动态加载器实现: `.kiro/specs/dynamic-module-loader/`

## 🔧 Python 代码调用（可选）

如果需要在 Python 脚本中使用动态加载器，可以使用以下方式：

### 基本用法

```python
from dynamic_loader import DynamicLoader

# 创建加载器实例
loader = DynamicLoader()

# 执行加载
success, prompt, result = loader.load()

if success:
    print(f"成功加载 {result['loaded_count']} 个模块")
    print(f"整合后的 Prompt 长度: {len(prompt)} 字符")
else:
    print("加载失败")
```

### 使用自定义上下文

```python
from dynamic_loader import DynamicLoader

# 创建加载器
loader = DynamicLoader()

# 指定当前上下文
context = {
    'current_directory': '.kiro/steering',
    'current_file': 'main.md',
    'current_file_type': '.md'
}

# 执行加载
success, prompt, result = loader.load(context)
```

### 使用便捷函数

```python
from dynamic_loader import load_modules

# 直接加载模块
success, prompt, result = load_modules()

# 或指定项目根目录
success, prompt, result = load_modules(project_root='/path/to/project')
```

### 获取加载结果

```python
from dynamic_loader import DynamicLoader

loader = DynamicLoader()
success, prompt, result = loader.load()

# 获取成功加载的模块
loaded_modules = loader.get_loaded_modules()
for module in loaded_modules:
    print(f"- {module['name']} (v{module['version']}) - 优先级: {module['priority']}")

# 获取加载失败的模块
failed_modules = loader.get_failed_modules()
for item in failed_modules:
    module = item['module']
    reason = item['reason']
    print(f"✗ {module['name']}: {reason}")

# 获取整合后的 Prompt
integrated_prompt = loader.get_integrated_prompt()
```

## 📊 完整示例

### 示例 1：基本配置

**配置文件（.kiro/config.yaml）：**
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
```

**预期结果：**
- 3 个模块被加载
- 加载顺序：workflow → ai-dev → git-commit
- 所有模块使用默认激活条件（always: true）

### 示例 2：条件激活

**模块配置（.kiro/modules/doc-save/v1.0/config.yaml）：**
```yaml
activation_conditions:
  or:
    - directory_match:
        - "doc/**/*"
        - ".kiro/steering/*"
    - file_type_match:
        - ".md"
```

**场景 A：在 doc 目录下**
```
当前目录: doc/project/architecture/
当前文件: design.md
结果: doc-save 模块激活 ✓
```

**场景 B：在 src 目录下编辑 Python 文件**
```
当前目录: src/
当前文件: main.py
结果: doc-save 模块不激活 ✗
```

### 示例 3：模块依赖

**配置：**
```yaml
# .kiro/config.yaml
modules:
  module-a:
    enabled: true
    version: v1.0
    priority: 100
  
  module-b:
    enabled: true
    version: v1.0
    priority: 90
  
  module-c:
    enabled: true
    version: v1.0
    priority: 80

# .kiro/modules/module-b/v1.0/config.yaml
dependencies:
  - module-a

# .kiro/modules/module-c/v1.0/config.yaml
dependencies:
  - module-b
```

**预期结果：**
- 所有模块依赖满足
- 加载顺序：module-a → module-b → module-c
- 3 个模块全部成功加载

### 示例 4：错误处理

**场景：缺失依赖**
```yaml
# module-b 依赖 module-a，但 module-a 被禁用
modules:
  module-a:
    enabled: false  # 禁用
    version: v1.0
    priority: 100
  
  module-b:
    enabled: true
    version: v1.0
    priority: 90
```

**预期结果：**
```
[WARNING] [DynamicLoader] 模块 module-b 缺少依赖 [module-a]，跳过加载
成功加载: 0 个
加载失败: 1 个
```

### 示例 5：循环依赖

**场景：循环依赖**
```yaml
# module-a 依赖 module-b
# module-b 依赖 module-a
```

**预期结果：**
```
[ERROR] [DynamicLoader] 检测到循环依赖: {module-a, module-b}
[WARNING] [DynamicLoader] 模块 module-a 存在循环依赖，跳过加载
[WARNING] [DynamicLoader] 模块 module-b 存在循环依赖，跳过加载
成功加载: 0 个
加载失败: 2 个
```

## 🎯 最佳实践

### 1. 模块组织

- 核心模块（workflow）：优先级 200+
- 功能模块（ai-dev, git-commit）：优先级 100-199
- 辅助模块（doc-save）：优先级 50-99
- 可选模块：优先级 1-49

### 2. 激活条件设计

- 使用 `always: true` 用于核心模块
- 使用 `directory_match` 用于特定目录的功能
- 使用 `file_type_match` 用于特定文件类型的功能
- 使用 `and/or` 组合实现复杂条件

### 3. 依赖管理

- 保持依赖关系简单清晰
- 避免循环依赖
- 核心模块不应该依赖其他模块
- 功能模块可以依赖核心模块

### 4. 版本管理

- 使用语义化版本号
- 为不同复杂度创建不同版本（如 v1.0-simple, v1.0-complex）
- 在 meta.yaml 中记录版本变更历史

### 5. 配置管理

- 顶层配置用于全局控制
- 模块配置用于模块特定设置
- 使用配置合并实现灵活的配置组合

### 6. 错误处理

- 定期检查加载日志
- 及时修复配置错误
- 处理依赖问题
- 验证 Steering 文件存在

---

**文档版本**: v2.0  
**创建日期**: 2026-03-03  
**状态**: ✅ 可用
