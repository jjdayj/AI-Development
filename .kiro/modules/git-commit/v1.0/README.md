# Git 提交管理

## 📋 模块信息

- **模块名称**: git-commit
- **版本**: v1.0
- **分类**: git
- **作者**: yangzhuo
- **创建日期**: 2026-03-02

## 🎯 功能说明

Git 提交主题化管理模块，实现：
- 自动从需求 meta.yaml 读取提交前缀
- 生成规范的提交信息
- 提交前安全检查
- 自动推送到远程

## 📁 目录结构

```
git-commit/
├── v1.0/
│   ├── meta.yaml           # 模块元信息
│   ├── config.yaml         # 模块配置
│   ├── scripts/            # 脚本
│   │   └── security_checker.py
│   └── README.md           # 本文件
```

## ⚙️ 配置说明

### 全局开关

在 `.kiro/config.yaml` 中启用/禁用模块：

```yaml
modules:
  git-commit:
    enabled: true
    version: v1.0
    priority: 80
```

### 模块配置

在 `config.yaml` 中配置提交信息格式：

```yaml
commit_message:
  template: "{prefix}: {description}"
  auto_prefix: true
  default_prefix: "chore"

requirement_meta:
  path_template: "requirements/{module}/{version}/meta.yaml"
  required: false

pre_commit:
  check_clean: true
  check_staged: true
  run_tests: false

post_commit:
  auto_push: true
  update_meta_status: false
```

## 📖 使用方法

### 提交信息格式

```
feat(module-v1.0): 实现某功能
^    ^            ^
|    |            |
|    |            +-- 描述
|    +-- 从 meta.yaml 读取
+-- 提交类型
```

### 需求 meta.yaml 示例

```yaml
theme: Git提交主题化管理
module: git-commit
version: v1.0
git_commit_prefix: feat(git-commit-v1.0)
```

## 🔗 相关文档

- 需求文档: `requirements/git-commit/v1.0/`
- 项目文档: `doc/project/git-commit/`

## 📝 更新日志

### v1.0 (2026-03-02)
- 自动读取 meta.yaml 生成提交前缀
- 提交前安全检查
- 自动推送功能
