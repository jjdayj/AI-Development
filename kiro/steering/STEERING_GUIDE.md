# Steering 配置说明

此目录包含 Kiro 的顶层 steering 文件。

## 📋 目录说明

本目录现在只包含顶层入口文件：
- `main.md` - Kiro 主入口 Prompt（负责加载模块）

## 🔄 架构更新（2026-03-03）

项目已完成模块化架构重构：

### 新的目录结构

```
.kiro/
├── config.yaml              # 顶层配置（全局开关）
├── steering/
│   ├── main.md             # 主入口 Prompt
│   └── STEERING_GUIDE.md   # 本文件
├── modules/                # 模块目录
│   ├── workflow/v1.0/
│   ├── ai-dev/v1.0/
│   ├── doc-save/v1.0/
│   ├── git-commit/v1.0/
│   └── git-rollback/v1.0/
└── templates/              # 模板目录
    ├── module/
    └── requirement/
```

### 模块 Steering 位置

所有模块的 Steering 文件已迁移到模块目录：

- **workflow**: `.kiro/modules/workflow/v1.0/steering/workflow_selector.md`
- **ai-dev**: `.kiro/modules/ai-dev/v1.0/steering/ai_dev.md`
- **doc-save**: `.kiro/modules/doc-save/v1.0/steering/doc_save_rules.md`
- **git-commit**: `.kiro/modules/git-commit/v1.0/steering/git_commit.md`
- **git-rollback**: `.kiro/modules/git-rollback/v1.0/steering/git_rollback.md`

## ⚙️ 如何管理模块

### 启用/禁用模块

编辑 `.kiro/config.yaml`：

```yaml
modules:
  {module-name}:
    enabled: true  # 改为 false 禁用
    version: v1.0
    priority: 100
```

### 查看模块文档

每个模块都有完整的文档：
- 模块信息: `.kiro/modules/{module}/{version}/README.md`
- 元信息: `.kiro/modules/{module}/{version}/meta.yaml`
- 配置: `.kiro/modules/{module}/{version}/config.yaml`
- Steering: `.kiro/modules/{module}/{version}/steering/`

## 🔗 相关文档

- 主入口文档: `main.md`
- 全局配置: `.kiro/config.yaml`
- 模块目录: `.kiro/modules/`
- 模板文件: `.kiro/templates/`
- 架构文档: `doc/project/prompt-base-architecture/`

---

**文档版本**: v2.0  
**更新日期**: 2026-03-03  
**状态**: ✅ 可用
