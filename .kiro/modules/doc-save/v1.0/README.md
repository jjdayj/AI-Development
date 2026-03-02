# 会话文档自动保存

## 📋 模块信息

- **模块名称**: doc-save
- **版本**: v1.0
- **分类**: doc
- **作者**: yangzhuo
- **创建日期**: 2026-03-02

## 🎯 功能说明

自动保存每次对话的操作文档和对话记录，包括：
- 对话记录
- 操作文档
- 会话总览

## 📁 目录结构

```
doc-save/
├── v1.0/
│   ├── meta.yaml           # 模块元信息
│   ├── config.yaml         # 模块配置
│   ├── steering/           # Steering 规则
│   │   └── doc_save_rules.md
│   └── README.md           # 本文件
```

## ⚙️ 配置说明

### 全局开关

在 `.kiro/config.yaml` 中启用/禁用模块：

```yaml
modules:
  doc-save:
    enabled: false  # 默认禁用
    version: v1.0
    priority: 90
```

### 模块配置

在 `config.yaml` 中配置保存路径和内容：

```yaml
save_path:
  root: "doc"
  subdirectory_template: "测试docsave功能-{date}"
  date_format: "%Y%m%d_%H%M%S"

content:
  save_conversation: true
  save_operations: true
  save_summary: true

auto_save:
  enabled: false
  triggers:
    - "对话结束"
    - "用户请求"
```

## 📖 使用方法

### 启用模块

1. 编辑 `.kiro/config.yaml`，设置 `enabled: true`
2. 编辑 `steering/doc_save_rules.md`，设置 `inclusion: always`

### 手动触发保存

在对话中说："保存本次对话"

## 🔗 相关文档

- 需求文档: `requirements/doc-save/v1.0/`
- 项目文档: `doc/project/doc-save/`
- Steering 规则: `steering/doc_save_rules.md`

## 📝 更新日志

### v1.0 (2026-03-02)
- 自动保存对话记录
- 自动保存操作文档
- 生成会话总览
