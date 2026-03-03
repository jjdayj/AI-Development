---
inclusion: always
description: Kiro 主入口 - 加载 VibeCoding 工作流模块
priority: highest
enabled: true
---

# Kiro 主入口

## 🎯 功能说明

本文件是 Kiro 的主入口，负责加载 VibeCoding 工作流模块。

## 📋 模块加载

### 当前启用的模块

根据 `kiro/config.yaml` 配置，当前启用的模块：

- **workflow (v2.0)** - VibeCoding 工作流
  - 优先级: 200（最高）
  - Steering: `kiro/modules/workflow/v2.0/steering/workflow_main.md`
  - 功能：轻量化工作流，支持原生开发和二次开发

### 模块说明

**VibeCoding 工作流 (v2.0)**
- **触发方式**：用户输入包含触发关键词（如"开发新功能"、"实现功能"等）
- **工作流类型**：
  - A. 原生功能开发流程（4 阶段）
  - B. 二次开发流程（5 阶段）
  - C. 不进入工作流，正常作答
- **核心特点**：
  - 需求复杂度分析
  - 改一点测一点
  - 测试和文档可选
  - 支持需求拆分

## 🔧 配置管理

### 启用/禁用模块

编辑 `kiro/config.yaml`：

```yaml
modules:
  workflow:
    enabled: true   # 改为 false 可禁用工作流
    version: v2.0
    priority: 200
```

### 查看模块详情

- 工作流说明：`kiro/modules/workflow/v2.0/README.md`
- 工作流配置：`kiro/modules/workflow/v2.0/config.yaml`
- 更新日志：`kiro/modules/workflow/v2.0/CHANGELOG.md`

## 📚 使用指南

### 快速开始

1. 在 Kiro 中输入触发关键词（如"开发新功能"）
2. 选择工作流类型（A/B/C）
3. 如果选择 A 或 B，系统会分析需求复杂度
4. 按照引导完成各个阶段

### 常见问题

**Q: 如何禁用工作流？**
A: 在 `kiro/config.yaml` 中将 `workflow.enabled` 改为 `false`

**Q: 如何查看工作流详细说明？**
A: 查看 `kiro/modules/workflow/v2.0/README.md`

**Q: 如何修改工作流配置？**
A: 编辑 `kiro/modules/workflow/v2.0/config.yaml`

---

**版本**: v2.0  
**最后更新**: 2026-03-04  
**维护者**: yangzhuo
