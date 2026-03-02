---
inclusion: always
description: Git 回滚功能规则（MVP版本）
---

# Git 回滚功能规则

## 功能说明
本规则实现通过自然语言指令进行 Git 回滚的功能。

**当前版本**：MVP（最小可行产品）
**支持功能**：回滚最近一次提交

---

## 触发条件

### 关键词识别
用户输入中包含以下任一关键词时触发：
- 中文：`回滚`、`撤销`、`恢复`
- 英文：`rollback`、`revert`

### 示例
- "回滚上一次提交"
- "撤销最近的修改"
- "恢复到之前的版本"
- "rollback last commit"

---

## 执行流程

### 1. 检查全局开关
首先检查 `.kiro/kiro.yaml` 中的配置：
```yaml
experimental:
  git_auto_rollback: false  # 或 true
```

**如果 git_auto_rollback: false**：
```
⚠️ Git 自动回滚功能已关闭

如需启用，请修改 .kiro/kiro.yaml：
experimental:
  git_auto_rollback: true

或者手动执行 Git 命令：
git revert HEAD

提示：回滚是高风险操作，建议在熟悉流程后再启用。
```

**如果 git_auto_rollback: true**：
继续执行后续步骤

---

### 2. 获取回滚信息
执行以下命令获取最近一次提交的信息：
```bash
# 获取最近一次提交
git log -1 --pretty=format:"%h: %s"

# 获取影响的文件
git diff-tree --no-commit-id --name-only -r HEAD
```

---

### 3. 展示回滚信息
向用户展示详细的回滚信息：

```
📋 回滚信息确认

将要回滚的提交：
  - <commit-id>: <commit-message>

回滚方式：git revert（安全，保留历史）

影响的文件：
  - <file1>
  - <file2>
  - ...

⚠️ 注意：
  - 回滚后会创建新的提交
  - 回滚操作会立即推送到远程仓库
  - 如果回滚错误，可以再次 revert 恢复

确认执行回滚吗？(yes/no)
```

---

### 4. 等待用户确认
等待用户输入确认：
- 接受：`yes`、`y`、`是`、`确认`
- 拒绝：`no`、`n`、`否`、`取消`

**如果用户拒绝**：
```
❌ 回滚已取消
```

**如果用户确认**：
继续执行步骤 5

---

### 5. 执行回滚
执行以下命令：
```bash
# 1. 检查工作目录状态
git status --porcelain

# 2. 如果有未提交修改，提示错误
如果输出不为空：
⚠️ 工作目录有未提交的修改

请先提交或暂存修改：
git add .
git commit -m "..."

或者暂存修改：
git stash

# 3. 执行回滚
git revert HEAD --no-edit

# 4. 推送到远程
git push

# 5. 报告结果
✅ 回滚成功！

回滚详情：
  - 本地回滚：完成
  - 远程推送：完成
  - 新提交ID：<new-commit-id>

验证回滚：
git log --oneline -3
```

---

## 错误处理

### 错误 1：工作目录有未提交修改
```
⚠️ 工作目录有未提交的修改

请先提交或暂存修改：
git add .
git commit -m "..."

或者暂存修改：
git stash
```

### 错误 2：回滚产生冲突
```
⚠️ 回滚操作产生冲突

请手动解决冲突：
1. 编辑冲突文件
2. git add <冲突文件>
3. git revert --continue

或者放弃回滚：
git revert --abort
```

### 错误 3：推送失败
```
✅ 本地回滚成功
❌ 推送到远程失败：<错误信息>

请稍后手动推送：
git push

提示：本地回滚已完成，代码已安全保存
```

---

## MVP 限制

### 当前版本只支持：
- ✅ 回滚最近一次提交（`git revert HEAD`）
- ✅ 使用 git revert 方式（安全）
- ✅ 自动推送到远程
- ✅ 基本错误处理

### 当前版本不支持：
- ❌ 回滚多次提交
- ❌ 指定 commit ID 回滚
- ❌ 自动创建备份分支
- ❌ 使用 git reset 方式

这些功能将在 Phase 3 中添加。

---

## 使用示例

### 示例 1：成功回滚
```
用户："回滚上一次提交"

Kiro：
📋 回滚信息确认

将要回滚的提交：
  - 34c30ef: fix: 优化Git回滚功能需求细化文档

回滚方式：git revert（安全，保留历史）

影响的文件：
  - doc/project/20260302_prompt基座架构设计/23-Git回滚功能需求细化.md

⚠️ 注意：
  - 回滚后会创建新的提交
  - 回滚操作会立即推送到远程仓库
  - 如果回滚错误，可以再次 revert 恢复

确认执行回滚吗？(yes/no)

用户："yes"

Kiro：
[执行 git revert HEAD --no-edit]
[执行 git push]

✅ 回滚成功！

回滚详情：
  - 本地回滚：完成
  - 远程推送：完成
  - 新提交ID：abc1234

验证回滚：
git log --oneline -3
```

### 示例 2：功能关闭
```
用户："回滚上一次提交"

Kiro：
⚠️ Git 自动回滚功能已关闭

如需启用，请修改 .kiro/kiro.yaml：
experimental:
  git_auto_rollback: true

或者手动执行 Git 命令：
git revert HEAD

提示：回滚是高风险操作，建议在熟悉流程后再启用。
```

### 示例 3：用户取消
```
用户："回滚上一次提交"

Kiro：
📋 回滚信息确认
[... 展示回滚信息 ...]
确认执行回滚吗？(yes/no)

用户："no"

Kiro：
❌ 回滚已取消
```

---

## 相关文档
- `doc/project/20260302_prompt基座架构设计/19-Git工作流程规范.md`
- `doc/project/20260302_prompt基座架构设计/22-Git回滚功能架构决策.md`
- `doc/project/20260302_prompt基座架构设计/23-Git回滚功能需求细化.md`

---

**文档创建时间**：2026-03-02 13:35  
**版本**：MVP v1.0  
**状态**：✅ 可用
