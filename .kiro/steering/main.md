# Kiro 主入口 Prompt

## 🎯 功能说明

本文件是 Kiro Prompt 基座的主入口，负责：
1. 读取全局配置（`.kiro/config.yaml`）
2. 根据模块开关动态加载模块 Steering
3. 管理模块优先级，避免冲突

## 📋 执行流程

### 1. 读取全局配置

从 `.kiro/config.yaml` 读取：
- 模块开关状态（`modules.{module}.enabled`）
- 模块版本（`modules.{module}.version`）
- 模块优先级（`modules.{module}.priority`）

### 2. 加载启用的模块

按优先级从高到低加载模块的 Steering 文件：

```
优先级排序：
1. workflow (priority: 200) - 工作流选择器
2. ai-dev (priority: 100) - AI 开发自动化
3. doc-save (priority: 90) - 文档自动保存
4. git-commit (priority: 80) - Git 提交管理
5. git-rollback (priority: 70) - Git 回滚功能
```

### 3. 模块 Steering 路径

每个模块的 Steering 文件路径：
```
.kiro/modules/{module}/{version}/steering/{module}.md
```

示例：
- `.kiro/modules/workflow/v1.0/steering/workflow_selector.md`
- `.kiro/modules/ai-dev/v1.0/steering/ai_dev.md`
- `.kiro/modules/git-commit/v1.0/steering/git_commit.md`
- `.kiro/modules/git-rollback/v1.0/steering/git_rollback.md`

### 4. 冲突处理

如果多个模块的 Steering 规则冲突：
- 优先级高的模块规则优先
- 如果优先级相同，按模块名称字母顺序

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

## 📝 使用说明

### 启用/禁用模块

编辑 `.kiro/config.yaml`：

```yaml
modules:
  {module-name}:
    enabled: true  # 改为 false 禁用
    version: v1.0
    priority: 100
```

### 调整模块优先级

修改 `priority` 值（数字越大优先级越高）：

```yaml
modules:
  my-module:
    enabled: true
    version: v1.0
    priority: 150  # 调整优先级
```

### 切换模块版本

修改 `version` 值：

```yaml
modules:
  my-module:
    enabled: true
    version: v2.0  # 切换到 v2.0
    priority: 100
```

## 🔗 相关文档

- 全局配置: `.kiro/config.yaml`
- 模块目录: `.kiro/modules/`
- 模板文件: `.kiro/templates/`

---

**文档版本**: v2.0  
**创建日期**: 2026-03-03  
**状态**: ✅ 可用
