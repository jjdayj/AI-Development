# 数据格式规范文档

## 概述

本文档定义了 Kiro Prompt 基座项目中所有模块共享的数据格式规范，确保三个核心模块（动态模块加载器、Git 提交自动化联动、VibCoding 工作流增强）之间的数据格式完全兼容。

**文档版本**: v1.0  
**创建日期**: 2026-03-03  
**状态**: ✅ 规范冻结

---

## 1. current_context.yaml 格式规范

### 1.1 文件位置
```
.kiro/current_context.yaml
```

### 1.2 字段定义

| 字段路径 | 类型 | 必需性 | 默认值 | 说明 |
|---------|------|--------|--------|------|
| `active_requirement` | Object | 必需 | - | 当前活跃需求信息 |
| `active_requirement.theme` | String | 必需 | - | 需求主题 |
| `active_requirement.module` | String | 必需 | - | 模块名称（kebab-case） |
| `active_requirement.version` | String | 必需 | - | 版本号（SemVer 2.0.0） |
| `active_requirement.requirement_path` | String | 必需 | - | 需求目录路径 |
| `active_requirement.meta_path` | String | 必需 | - | meta.yaml 文件路径 |
| `active_requirement.started_at` | String | 必需 | - | 开始时间（YYYY-MM-DD HH:MM:SS） |
| `active_requirement.current_phase` | String | 可选 | null | 当前工作流阶段 |
| `active_requirement.paused_at` | String | 可选 | null | 暂停时间（YYYY-MM-DD HH:MM:SS） |
| `active_requirement.completed_at` | String | 可选 | null | 完成时间（YYYY-MM-DD HH:MM:SS） |
| `environment` | Object | 必需 | - | 当前工作环境 |
| `environment.current_directory` | String | 必需 | - | 当前工作目录 |
| `environment.current_file` | String | 可选 | null | 当前打开的文件 |
| `environment.current_file_type` | String | 可选 | null | 当前文件类型 |
| `updated_at` | String | 必需 | - | 最后更新时间（YYYY-MM-DD HH:MM:SS） |

### 1.3 嵌套结构说明

```yaml
# 顶层结构（3个必需字段）
active_requirement:    # 必需
  # 需求信息（6个必需字段 + 3个可选字段）
  theme: String        # 必需
  module: String       # 必需
  version: String      # 必需
  requirement_path: String  # 必需
  meta_path: String    # 必需
  started_at: String   # 必需
  current_phase: String | null  # 可选
  paused_at: String | null      # 可选
  completed_at: String | null   # 可选

environment:           # 必需
  # 环境信息（1个必需字段 + 2个可选字段）
  current_directory: String  # 必需
  current_file: String | null  # 可选
  current_file_type: String | null  # 可选

updated_at: String     # 必需
```

### 1.4 完整示例

```yaml
# .kiro/current_context.yaml

# 当前活跃需求信息
active_requirement:
  theme: "动态模块加载器"
  module: "dynamic-module-loader"
  version: "v1.0"
  requirement_path: "requirements/dynamic-module-loader/v1.0/"
  meta_path: "requirements/dynamic-module-loader/v1.0/meta.yaml"
  started_at: "2026-03-03 10:00:00"
  current_phase: "Phase 2"
  paused_at: null
  completed_at: null

# 当前工作环境
environment:
  current_directory: "/path/to/project/.kiro/steering"
  current_file: "main.md"
  current_file_type: ".md"

# 更新时间
updated_at: "2026-03-03 10:30:00"
```

### 1.5 校验规则

1. **必需字段校验**：
   - `active_requirement`, `environment`, `updated_at` 必须存在
   - `active_requirement` 下的 6 个必需字段必须存在
   - `environment.current_directory` 必须存在

2. **格式校验**：
   - `module`: 必须符合 kebab-case 格式（`^[a-z0-9]+(-[a-z0-9]+)*$`）
   - `version`: 必须符合 SemVer 2.0.0 格式（`^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[a-zA-Z0-9-]+)?(?:\+[a-zA-Z0-9-]+)?$`）
   - 所有时间字段: 必须符合 `YYYY-MM-DD HH:MM:SS` 格式

3. **路径校验**：
   - `requirement_path`: 必须符合 `requirements/{module}/{version}/` 格式
   - `meta_path`: 必须符合 `requirements/{module}/{version}/meta.yaml` 格式

4. **逻辑校验**：
   - `updated_at` >= `started_at`
   - 如果 `completed_at` 存在，则 `completed_at` >= `started_at`
   - 如果 `paused_at` 存在，则 `paused_at` >= `started_at`

---

## 2. meta.yaml 格式规范

### 2.1 文件位置
```
requirements/{module}/{version}/meta.yaml
```

### 2.2 字段定义

| 字段名 | 类型 | 必需性 | 默认值 | 说明 |
|--------|------|--------|--------|------|
| `theme` | String | 必需 | - | 需求主题 |
| `module` | String | 必需 | - | 模块名称（kebab-case） |
| `version` | String | 必需 | - | 版本号（SemVer 2.0.0） |
| `author` | String | 必需 | "yangzhuo" | 作者 |
| `date` | String | 必需 | - | 创建日期（YYYY-MM-DD） |
| `status` | String | 必需 | "开发中" | 状态 |
| `description` | String | 必需 | - | 描述 |
| `git_commit_prefix` | String | 必需 | - | Git 提交前缀 |
| `updated_at` | String | 可选 | - | 更新时间（YYYY-MM-DD HH:MM:SS） |

### 2.3 完整示例

```yaml
# requirements/dynamic-module-loader/v1.0/meta.yaml

theme: "动态模块加载器"
module: "dynamic-module-loader"
version: "v1.0"
author: "yangzhuo"
date: "2026-03-03"
status: "开发中"
description: "实现 Kiro Prompt 基座的动态模块加载功能"
git_commit_prefix: "feat(dynamic-module-loader-v1.0)"
updated_at: "2026-03-03 15:30:00"
```

### 2.4 校验规则

1. **必需字段校验**：
   - 所有 8 个必需字段必须存在

2. **格式校验**：
   - `module`: 必须符合 kebab-case 格式
   - `version`: 必须符合 SemVer 2.0.0 格式
   - `date`: 必须符合 `YYYY-MM-DD` 格式
   - `updated_at`: 必须符合 `YYYY-MM-DD HH:MM:SS` 格式
   - `git_commit_prefix`: 必须符合 `feat({module}-{version})` 格式

3. **枚举值校验**：
   - `status`: 必须是以下值之一：`开发中`, `已完成`, `已暂停`, `已取消`

4. **逻辑校验**：
   - 如果 `updated_at` 存在，则 `updated_at` >= `date`

---

## 3. 模块配置格式规范（config.yaml）

### 3.1 文件位置
```
.kiro/modules/{module}/{version}/config.yaml
```

### 3.2 字段定义

| 字段路径 | 类型 | 必需性 | 默认值 | 说明 |
|---------|------|--------|--------|------|
| `activation_conditions` | Object | 可选 | `{always: true}` | 激活条件 |
| `module_specific_config` | Object | 可选 | `{}` | 模块特定配置 |

### 3.3 激活条件格式

#### 3.3.1 条件类型

| 条件类型 | 格式 | 说明 |
|---------|------|------|
| `always` | `always: true` | 始终激活 |
| `directory_match` | `directory_match: [pattern1, pattern2]` | 按目录匹配 |
| `file_type_match` | `file_type_match: [.ext1, .ext2]` | 按文件类型匹配 |
| `and` | `and: [condition1, condition2]` | 逻辑与 |
| `or` | `or: [condition1, condition2]` | 逻辑或 |

#### 3.3.2 完整示例

```yaml
# .kiro/modules/workflow/v1.0/config.yaml

# 激活条件
activation_conditions:
  or:
    - directory_match:
        - ".kiro/steering/*"
        - "doc/project/*"
    - file_type_match:
        - ".md"
        - ".yaml"

# 模块特定配置
module_specific_config:
  workflow_type: "simple"
  auto_save: true
```

### 3.4 校验规则

1. **条件类型校验**：
   - 条件类型必须是以下之一：`always`, `directory_match`, `file_type_match`, `and`, `or`

2. **条件值校验**：
   - `always`: 值必须是 `true`
   - `directory_match`: 值必须是字符串数组
   - `file_type_match`: 值必须是字符串数组（以 `.` 开头）
   - `and`: 值必须是条件对象数组
   - `or`: 值必须是条件对象数组

3. **嵌套深度校验**：
   - 条件嵌套深度不超过 3 层

---

## 4. 顶层配置格式规范（.kiro/config.yaml）

### 4.1 文件位置
```
.kiro/config.yaml
```

### 4.2 字段定义

| 字段路径 | 类型 | 必需性 | 默认值 | 说明 |
|---------|------|--------|--------|------|
| `version` | String | 必需 | - | 配置文件版本 |
| `modules` | Object | 必需 | `{}` | 模块配置 |
| `modules.{module_name}` | Object | 必需 | - | 单个模块配置 |
| `modules.{module_name}.enabled` | Boolean | 必需 | - | 全局开关 |
| `modules.{module_name}.version` | String | 必需 | - | 模块版本 |
| `modules.{module_name}.priority` | Integer | 必需 | - | 优先级 |

### 4.3 完整示例

```yaml
# .kiro/config.yaml

version: "2.0"

modules:
  workflow:
    enabled: true
    version: "v1.0-simple"
    priority: 200
  
  ai-dev:
    enabled: true
    version: "v1.0"
    priority: 100
  
  git-commit:
    enabled: true
    version: "v1.0"
    priority: 80
```

### 4.4 校验规则

1. **必需字段校验**：
   - `version`, `modules` 必须存在
   - 每个模块的 `enabled`, `version`, `priority` 必须存在

2. **格式校验**：
   - `version`: 必须符合 `X.Y` 格式
   - `modules.{module_name}.version`: 必须符合 SemVer 2.0.0 格式
   - `modules.{module_name}.priority`: 必须是正整数

3. **逻辑校验**：
   - 模块名称必须符合 kebab-case 格式
   - 优先级值不能重复（建议）

---

## 5. 格式校验工具

### 5.1 工具位置
```
.kiro/specs/scripts/validate_format.py
```

### 5.2 使用方法

```bash
# 校验单个文件
python .kiro/specs/scripts/validate_format.py --file .kiro/current_context.yaml

# 校验所有文件
python .kiro/specs/scripts/validate_format.py --all

# 生成兼容性报告
python .kiro/specs/scripts/validate_format.py --report
```

### 5.3 校验输出

```
[✓] .kiro/current_context.yaml - 格式正确
[✓] requirements/dynamic-module-loader/v1.0/meta.yaml - 格式正确
[✗] .kiro/modules/workflow/v1.0/config.yaml - 错误：缺少必需字段 'enabled'

兼容性报告：
- 总文件数: 15
- 通过: 14
- 失败: 1
- 兼容性: 93.3%
```

---

## 6. 模块间数据传递协议

### 6.1 动态模块加载器 → Git 提交模块

**传递方式**: 通过 `current_context.yaml` 文件

**传递内容**:
- `active_requirement.module`: 模块名称
- `active_requirement.version`: 版本号
- `active_requirement.meta_path`: meta.yaml 路径

**Git 提交模块读取流程**:
1. 读取 `current_context.yaml`
2. 提取 `meta_path`
3. 读取 `meta_path` 指向的 `meta.yaml`
4. 提取 `git_commit_prefix`
5. 生成提交信息

### 6.2 动态模块加载器 → VibCoding 工作流

**传递方式**: 通过 `current_context.yaml` 文件

**传递内容**:
- `active_requirement.*`: 所有需求信息
- `environment.*`: 所有环境信息

**VibCoding 工作流读取流程**:
1. 工作流启动时读取 `current_context.yaml`
2. 如果文件存在，恢复上次的工作状态
3. 如果文件不存在，创建新的需求上下文

### 6.3 VibCoding 工作流 → Git 提交模块

**传递方式**: 通过 `current_context.yaml` 文件

**传递内容**:
- 完整的 `current_context.yaml` 内容

**集成流程**:
1. VibCoding 工作流完成后，确保 `current_context.yaml` 完整
2. 用户触发 Git 提交
3. Git 提交模块读取 `current_context.yaml`
4. 自动生成规范的提交信息

---

## 7. 版本兼容性

### 7.1 向后兼容性

本规范遵循以下向后兼容性原则：

1. **新增字段**: 可以新增可选字段，不影响现有模块
2. **字段重命名**: 不允许重命名字段，必须保持字段名称不变
3. **字段删除**: 不允许删除必需字段
4. **格式变更**: 不允许变更已有字段的格式

### 7.2 版本升级策略

当需要进行不兼容的格式变更时：

1. 创建新版本的规范文档（如 v2.0）
2. 提供格式迁移工具
3. 在过渡期内同时支持旧版本和新版本
4. 在所有模块都升级后，废弃旧版本

---

## 8. 常见问题

### Q1: 为什么 current_context.yaml 使用嵌套结构？

**A**: 嵌套结构（active_requirement + environment）提供了更好的逻辑分组，便于：
- 区分需求信息和环境信息
- 支持未来扩展（如添加 history、settings 等顶层字段）
- 提高可读性和可维护性

### Q2: 为什么 version 字段必须符合 SemVer 2.0.0？

**A**: 语义化版本提供了标准的版本管理方式，便于：
- 自动推荐下一个版本号
- 判断版本兼容性
- 支持版本范围查询

### Q3: 为什么 git_commit_prefix 格式固定为 `feat({module}-{version})`？

**A**: 固定格式确保：
- 提交信息的一致性
- 便于自动生成和解析
- 符合 Conventional Commits 规范

### Q4: 如何处理格式校验失败？

**A**: 
1. 运行格式校验工具，查看详细错误信息
2. 根据错误信息修复格式问题
3. 重新运行校验工具，确保通过
4. 如果是上游模块的格式问题，阻止下游模块实施

---

## 9. 更新日志

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0 | 2026-03-03 | 初始版本，定义所有核心数据格式 |

---

**文档维护者**: Kiro AI 开发团队  
**最后更新**: 2026-03-03  
**状态**: ✅ 规范冻结
