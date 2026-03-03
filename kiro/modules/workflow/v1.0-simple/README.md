# 双轨工作流（简化版）

## 📋 模块信息

- **模块名称**: workflow
- **版本**: v1.0-simple
- **分类**: workflow
- **作者**: yangzhuo
- **创建日期**: 2026-03-03

## 🎯 功能说明

智能识别并执行 Prompt 工作流或代码工作流（简化版），包括：
- 自动识别工作流类型（按文件路径/关键词）
- 执行核心工作流（Phase 1-4）
- 不包含 Phase 5 总结反思
- 不生成文档

**适用场景**：
- 快速开发迭代
- 不需要详细文档的项目
- 个人项目或实验性项目
- 希望减少流程开销的场景

## 📁 目录结构

```
workflow/
├── v1.0-simple/
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
    version: v1.0-simple  # 使用简化版
    priority: 200  # 最高优先级
```

### 工作流配置

在 `.kiro/config.yaml` 中配置工作流规则：

```yaml
workflow:
  default: "prompt"
  
  auto_switch:
    - pattern: ".kiro/steering/*.md"
      workflow: "prompt"
    - pattern: "**/*.py"
      workflow: "code"
```

### 模块配置

在 `config.yaml` 中配置时间预估：

```yaml
phase5:
  mandatory: false  # 简化版不强制执行 Phase 5
  generate_docs: false  # 简化版不生成文档

time_estimates:
  prompt_workflow: 1.0  # 简化版时间更短
  code_workflow: 4.0
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

## 🔄 版本对比

### v1.0-simple（简化版）
- ✅ 智能识别工作流类型
- ✅ 执行 Phase 1-4
- ❌ 不包含 Phase 5 总结反思
- ❌ 不生成文档
- ⏱️ 时间：1-4 小时

### v1.0-complex（完整版）
- ✅ 智能识别工作流类型
- ✅ 快速跳过机制
- ✅ 执行 Phase 1-5
- ✅ 强制总结反思
- ✅ 生成三份文档
- ⏱️ 时间：2.5-8 小时

## 🔗 相关文档

- 需求文档: `requirements/workflow/v1.0/`
- 项目文档: `doc/project/workflow/`
- Steering 规则: `steering/workflow_selector.md`
- 完整版: `.kiro/modules/workflow/v1.0-complex/`

## 📝 更新日志

### v1.0-simple (2026-03-03)
- 简化版工作流
- 智能识别工作流类型
- 只执行 Phase 1-4
- 不包含 Phase 5 和文档生成
- 适合快速开发迭代

## 💡 使用建议

### 何时使用简化版？
- 快速原型开发
- 个人实验性项目
- 不需要详细文档的场景
- 希望减少流程开销

### 何时使用完整版？
- 团队协作项目
- 需要详细文档的项目
- 需要知识积累和复盘
- 重要的生产环境功能

### 如何切换版本？
在 `.kiro/config.yaml` 中修改版本号：

```yaml
modules:
  workflow:
    enabled: true
    version: v1.0-simple  # 或 v1.0-complex
    priority: 200
```
