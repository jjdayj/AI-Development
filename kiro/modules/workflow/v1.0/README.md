# 双轨工作流

## 📋 模块信息

- **模块名称**: workflow
- **版本**: v1.0
- **分类**: workflow
- **作者**: yangzhuo
- **创建日期**: 2026-03-02

## 🎯 功能说明

智能识别并执行 Prompt 工作流或代码工作流，包括：
- 自动识别工作流类型（按文件路径/关键词）
- 快速跳过机制（简单修改）
- 完整工作流（Phase 1-5）
- 强制总结反思（Phase 5）
- 生成三份文档（快速入门、详细说明、总结反思）

## 📁 目录结构

```
workflow/
├── v1.0/
│   ├── meta.yaml           # 模块元信息
│   ├── config.yaml         # 模块配置
│   ├── steering/           # Steering 规则
│   │   └── workflow_selector.md
│   └── README.md           # 本文件
```

## ⚙️ 配置说明

### 全局开关

在 `.kiro/config.yaml` 中启用/禁用模块：

```yaml
modules:
  workflow:
    enabled: true
    version: v1.0
    priority: 200  # 最高优先级
```

### 工作流配置

在 `.kiro/config.yaml` 中配置工作流规则：

```yaml
workflow:
  default: "prompt"
  
  quick_skip:
    enabled: true
    auto_skip_conditions:
      - type: "line_count"
        threshold: 10
      - type: "file_type"
        patterns: ["*.yaml", "*.json", "*.txt"]
  
  auto_switch:
    - pattern: ".kiro/steering/*.md"
      workflow: "prompt"
    - pattern: "**/*.py"
      workflow: "code"
```

### 模块配置

在 `config.yaml` 中配置 Phase 5 和时间预估：

```yaml
phase5:
  mandatory: true
  generate_docs: true

time_estimates:
  prompt_workflow: 2.5
  code_workflow: 8.0
  quick_fix: 0.2
```

## 📖 使用方法

### 触发工作流

工作流会自动触发，当用户输入包含以下关键词：
- 开发新功能、实现功能、添加功能
- 创建模块、新建模块、设计模块
- 功能设计、架构设计
- 重构、优化架构

### 手动指定工作流

```
用户："使用 Prompt 工作流"
用户："使用代码工作流"
```

### 快速跳过

```
用户："快速修改 config.yaml"
用户："简单修改，跳过流程"
```

## 🔗 相关文档

- 需求文档: `requirements/workflow/v1.0/`
- 项目文档: `doc/project/workflow/`
- Steering 规则: `steering/workflow_selector.md`
- 快速入门: `doc/project/workflow/快速入门指南.md`
- 详细说明: `doc/project/workflow/详细说明.md`

## 📝 更新日志

### v1.0 (2026-03-02)
- 智能识别工作流类型
- 快速跳过机制
- 强制总结反思
- 三份文档输出
