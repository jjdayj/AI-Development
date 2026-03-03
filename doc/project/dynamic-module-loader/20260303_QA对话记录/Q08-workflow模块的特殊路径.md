# Q08: workflow 模块的 Steering 文件路径是什么？为什么特殊？

**提问时间**: 2026-03-03

## 问题

workflow 模块的 Steering 文件路径是什么？为什么特殊？

## 回答

根据 `main.md` 文档，workflow 模块的 Steering 文件路径确实是特殊的。

## workflow 模块的 Steering 文件路径

### 步骤 8：加载 Steering 文件

```
路径规则：
标准路径：.kiro/modules/{module}/{version}/steering/{module}.md
特殊情况：workflow 模块使用 workflow_selector.md

示例：
- workflow: .kiro/modules/workflow/v1.0/steering/workflow_selector.md
- ai-dev: .kiro/modules/ai-dev/v1.0/steering/ai_dev.md
- git-commit: .kiro/modules/git-commit/v1.0/steering/git_commit.md
```

---

## 为什么 workflow 模块特殊？

### 特殊路径

```
workflow 模块：.kiro/modules/workflow/v1.0/steering/workflow_selector.md
                                                      ^^^^^^^^^^^^^^^^^^
                                                      不是 workflow.md
```

### 标准路径对比

**其他模块（标准命名）**：
```
ai-dev:       .kiro/modules/ai-dev/v1.0/steering/ai_dev.md
git-commit:   .kiro/modules/git-commit/v1.0/steering/git_commit.md
git-rollback: .kiro/modules/git-rollback/v1.0/steering/git_rollback.md
doc-save:     .kiro/modules/doc-save/v1.0/steering/doc_save.md
```

**标准规则**：
```
.kiro/modules/{module}/{version}/steering/{module}.md
```

---

### 原因 1：功能定位不同

workflow 模块不是一个普通的功能模块，而是一个**选择器（Selector）**。

**功能对比**：

| 模块类型 | 功能 | 文件名 |
|---------|------|--------|
| **普通功能模块** | 提供具体功能 | `{module}.md` |
| ai-dev | AI 开发自动化 | `ai_dev.md` |
| git-commit | Git 提交管理 | `git_commit.md` |
| **选择器模块** | 选择和调度其他工作流 | `{module}_selector.md` |
| workflow | 工作流选择器 | `workflow_selector.md` |

---

### 原因 2：职责是"选择"而非"执行"

**workflow 模块的核心职责**：
1. 判断是否可以快速跳过
2. 识别工作流类型（Prompt 工作流 / 代码工作流）
3. 调度对应的工作流执行
4. 强制执行 Phase 5（总结反思）

**命名逻辑**：
```
workflow_selector.md = workflow（工作流）+ selector（选择器）
```

这个名字更准确地反映了模块的功能：它是一个**工作流选择器**，而不是工作流本身。

---

### 原因 3：历史演进

从文档内容可以看出，workflow 模块经历了多次迭代：

**版本演进**：
```
v1.0-simple  → 简化版选择器
v1.0-complex → 复杂版选择器
v1.0         → 完整版选择器（当前版本）
```

在演进过程中，"selector"这个名字被保留下来，因为它准确描述了模块的核心功能。

---

### 原因 4：与其他工作流文件区分

项目中可能存在多个工作流相关的文件：

```
.kiro/modules/workflow/v1.0/steering/
├── workflow_selector.md    # 选择器（当前使用）
├── prompt_workflow.md      # Prompt 工作流（可能存在）
└── code_workflow.md        # 代码工作流（可能存在）
```

使用 `workflow_selector.md` 可以清晰地与其他工作流文件区分开。

---

## 动态加载器如何处理这个特殊情况？

### 步骤 8：加载 Steering 文件

```python
def get_steering_path(module_name, version):
    """获取 Steering 文件路径"""
    
    # 特殊情况：workflow 模块
    if module_name == 'workflow':
        return f'.kiro/modules/workflow/{version}/steering/workflow_selector.md'
    
    # 标准情况：其他模块
    return f'.kiro/modules/{module_name}/{version}/steering/{module_name}.md'
```

**处理逻辑**：
```
1. 检查模块名称
2. 如果是 'workflow' → 使用 'workflow_selector.md'
3. 如果是其他模块 → 使用 '{module}.md'
```

---

## 实际示例

### 示例 1：加载 workflow 模块

```
[INFO] [DynamicLoader] 步骤 8: 加载 Steering 文件
[INFO] [DynamicLoader] ------------------------------------------------------------
[INFO] [DynamicLoader] 加载 Steering: workflow (v1.0)
[INFO] [DynamicLoader] 路径: .kiro/modules/workflow/v1.0/steering/workflow_selector.md
[INFO] [DynamicLoader] ✓ Steering 加载成功
```

### 示例 2：加载其他模块

```
[INFO] [DynamicLoader] 加载 Steering: ai-dev (v1.0)
[INFO] [DynamicLoader] 路径: .kiro/modules/ai-dev/v1.0/steering/ai_dev.md
[INFO] [DynamicLoader] ✓ Steering 加载成功

[INFO] [DynamicLoader] 加载 Steering: git-commit (v1.0)
[INFO] [DynamicLoader] 路径: .kiro/modules/git-commit/v1.0/steering/git_commit.md
[INFO] [DynamicLoader] ✓ Steering 加载成功
```

---

## workflow 模块的功能说明

根据实际的 Steering 文件内容，workflow 模块提供以下功能：

### 核心功能

1. **快速跳过判断**
   - 手动跳过关键词识别
   - 自动跳过条件检查
   - 用户确认机制

2. **工作流类型识别**
   - 按文件路径自动识别
   - 按关键词自动识别
   - 支持手动覆盖

3. **工作流执行**
   - Prompt 工作流（Phase 1-5）
   - 代码工作流（Phase 1-5）

4. **强制总结反思**
   - Phase 5 必须执行
   - 5 个强制项不可跳过
   - 生成三份文档

5. **用户友好文档**
   - 快速入门指南
   - 详细说明文档
   - 总结与反思文档

---

## 总结

**workflow 模块的 Steering 文件路径特殊的原因**：

1. **功能定位**：它是一个选择器（Selector），不是普通功能模块
2. **职责不同**：负责选择和调度，而非直接执行
3. **命名准确**：`workflow_selector.md` 更准确地描述了功能
4. **文件区分**：与其他工作流文件（如 prompt_workflow.md）区分开
5. **历史演进**：在多次迭代中保留了这个命名

**关键点**：
- 这是唯一一个使用特殊命名的模块
- 动态加载器需要特殊处理这个情况
- 其他所有模块都遵循标准命名规则：`{module}.md`

---

**相关文档**: `.kiro/steering/main.md`, `.kiro/modules/workflow/v1.0/steering/workflow_selector.md`
