# Git 回滚功能

## 📋 模块信息

- **模块名称**: git-rollback
- **版本**: v1.0
- **分类**: git
- **作者**: yangzhuo
- **创建日期**: 2026-03-02

## 🎯 功能说明

通过自然语言指令进行 Git 回滚操作，支持：
- 回滚最近一次提交
- 回滚多次提交
- 自动创建备份分支
- 安全确认机制

## 📁 目录结构

```
git-rollback/
├── v1.0/
│   ├── meta.yaml           # 模块元信息
│   ├── config.yaml         # 模块配置
│   ├── steering/           # Steering 规则
│   │   └── git_rollback.md
│   └── README.md           # 本文件
```

## ⚙️ 配置说明

### 全局开关

在 `.kiro/config.yaml` 中启用/禁用模块：

```yaml
modules:
  git-rollback:
    enabled: true
    version: v1.0
    priority: 70
```

在 `.kiro/config.yaml` 中启用实验性功能：

```yaml
experimental:
  git_auto_rollback: true  # 启用自动回滚
```

### 模块配置

在 `config.yaml` 中配置备份和安全选项：

```yaml
backup:
  enabled: true
  push_to_remote: false
  auto_delete_after_days: 7

confirmation:
  required: true
  show_affected_files: true
  show_commit_details: true

safety:
  check_working_directory: true
  allow_force_push: false
```

## 📖 使用方法

### 触发关键词

- 中文：`回滚`、`撤销`、`恢复`
- 英文：`rollback`、`revert`

### 使用示例

```
用户："回滚上一次提交"
用户："回滚最近 3 次提交"
用户："撤销最近的修改"
```

## 🔗 相关文档

- 需求文档: `requirements/git-rollback/v1.0/`
- 项目文档: `doc/project/git-rollback/`
- Steering 规则: `steering/git_rollback.md`

## 📝 更新日志

### v1.0 (2026-03-02)
- 支持回滚单次提交
- 支持回滚多次提交
- 自动创建备份分支
- 安全确认机制
