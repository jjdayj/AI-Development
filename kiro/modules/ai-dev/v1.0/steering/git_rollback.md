---
inclusion: always
description: Git 回滚功能规则（完整版）
---

# Git 回滚功能规则

## 功能说明
本规则实现通过自然语言指令进行 Git 回滚的功能。

**当前版本**：v1.0（完整版）
**支持功能**：
- ✅ 回滚最近一次提交
- ✅ 回滚多次提交
- ✅ 自动创建备份分支

---

## 触发条件

### 关键词识别
用户输入中包含以下任一关键词时触发：
- 中文：`回滚`、`撤销`、`恢复`
- 英文：`rollback`、`revert`

### 回滚粒度识别

#### 1. 回滚单次提交（默认）
- "回滚上一次提交"
- "撤销最近的修改"
- "恢复到之前的版本"

#### 2. 回滚多次提交
- "回滚最近 3 次提交"
- "撤销最近的 5 次修改"
- "回滚上 2 次提交"

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

### 2. 解析回滚意图

#### 情况 A：回滚单次提交（默认）
```bash
# 获取最近一次提交
git log -1 --pretty=format:"%h: %s"
```

#### 情况 B：回滚多次提交
从用户输入中提取数量（如 "最近 3 次"），然后：
```bash
# 获取最近 N 次提交
git log -N --pretty=format:"%h: %s"
```

---

### 3. 获取影响的文件
```bash
# 单次提交
git diff-tree --no-commit-id --name-only -r HEAD

# 多次提交
git diff-tree --no-commit-id --name-only -r HEAD~N..HEAD
```

---

### 4. 展示回滚信息

#### 单次提交
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

#### 多次提交
```
📋 回滚信息确认

将要回滚的提交（共 N 次）：
  - <commit-id-1>: <message-1>
  - <commit-id-2>: <message-2>
  - ...

回滚方式：git revert（安全，保留历史）
回滚顺序：从新到旧依次回滚

影响的文件：
  - <file1>
  - <file2>
  - ...

⚠️ 注意：
  - 回滚后会创建 N 个新的提交
  - 回滚操作会立即推送到远程仓库
  - 如果回滚错误，可以再次 revert 恢复

确认执行回滚吗？(yes/no)
```

---

### 5. 等待用户确认
等待用户输入确认：
- 接受：`yes`、`y`、`是`、`确认`
- 拒绝：`no`、`n`、`否`、`取消`

**如果用户拒绝**：
```
❌ 回滚已取消
```

**如果用户确认**：
继续执行步骤 6

---

### 6. 创建备份分支（可选）

#### 读取备份配置
从 `.kiro/kiro.yaml` 读取备份配置：
```yaml
rollback:
  backup:
    enabled: true                    # 是否启用备份
    push_to_remote: false           # 是否推送到远程
    auto_delete_after_days: 7       # 自动删除天数（0=不删除）
```

#### 创建备份分支
如果 `rollback.backup.enabled: true`（默认启用）：
```bash
# 获取当前 HEAD 的 7 位短 ID
COMMIT_ID=$(git rev-parse --short HEAD)

# 创建备份分支
BACKUP_BRANCH="backup-before-rollback-$(date +%Y%m%d-%H%M%S)-$COMMIT_ID"
git branch $BACKUP_BRANCH

# 仅当 push_to_remote 为 true 时推送
if [ "$ROLLBACK_BACKUP_PUSH" = "true" ]; then
  git push origin $BACKUP_BRANCH
fi

# 提示用户
✅ 已创建备份分支：$BACKUP_BRANCH
```

---

### 7. 执行回滚

#### 前置检查
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
```

#### 执行回滚

**单次提交**：
```bash
git revert HEAD --no-edit
```

**多次提交**：
```bash
# 方式1：使用范围回滚（推荐）
git revert --no-edit HEAD~N..HEAD

# 方式2：循环回滚（基于原始 HEAD）
ORIG_HEAD=$(git rev-parse HEAD)
for i in $(seq 0 $((N-1))); do
  git revert --no-edit $ORIG_HEAD~$i
done
```

#### 推送到远程
```bash
# 所有回滚完成后一次性推送
git push
```

---

### 8. 报告结果

#### 成功（无备份）
```
✅ 回滚成功！

回滚详情：
  - 本地回滚：完成
  - 远程推送：完成
  - 新提交ID：<new-commit-id>

验证回滚：
git log --oneline -3
```

#### 成功（有备份）
```
✅ 回滚成功！

回滚详情：
  - 备份分支：backup-before-rollback-20260302-140000-abc1234
  - 本地回滚：完成
  - 远程推送：完成
  - 新提交ID：<new-commit-id>

恢复备份：
git checkout backup-before-rollback-20260302-140000-abc1234

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

### 错误 2：回滚次数超过总提交数
```
⚠️ 当前只有M次提交，无法回滚N次

是否回滚所有M次提交？(yes/no)
```

### 错误 3：回滚产生冲突
```
⚠️ 回滚操作产生冲突

冲突文件：
  - <file1>
  - <file2>

请手动解决冲突：
1. 编辑冲突文件
2. git add <冲突文件>
3. git revert --continue

或者放弃回滚：
git revert --abort
```

### 错误 4：推送失败
```
✅ 本地回滚成功
❌ 推送到远程失败：<错误信息>

请稍后手动推送：
git push

提示：本地回滚已完成，代码已安全保存
```

---

## 配置说明

### kiro.yaml 配置
```yaml
# 实验性功能开关
experimental:
  git_auto_rollback: false  # 默认关闭（安全优先）

# Git 回滚配置
rollback:
  backup:
    enabled: true                    # 是否启用备份
    push_to_remote: false           # 是否推送到远程
    auto_delete_after_days: 7       # 自动删除天数（0=不删除）
```

### 配置建议
- **生产环境**：建议 `git_auto_rollback: false`，手动执行更安全
- **开发环境**：可以 `git_auto_rollback: true`，提高效率
- **备份分支**：建议始终保持 `enabled: true`

---

## 使用示例

### 示例 1：回滚单次提交
```
用户："回滚上一次提交"

Kiro：
📋 回滚信息确认

将要回滚的提交：
  - f1b38a6: docs: 修正Git回滚功能Phase3完善实现文档

回滚方式：git revert（安全，保留历史）

影响的文件：
  - doc/project/20260302_prompt基座架构设计/29-Git回滚功能Phase3完善实现.md

⚠️ 注意：
  - 回滚后会创建新的提交
  - 回滚操作会立即推送到远程仓库
  - 如果回滚错误，可以再次 revert 恢复

确认执行回滚吗？(yes/no)

用户："yes"

Kiro：
✅ 已创建备份分支：backup-before-rollback-20260302-153500-f1b38a6

[执行 git revert HEAD --no-edit]
[执行 git push]

✅ 回滚成功！

回滚详情：
  - 备份分支：backup-before-rollback-20260302-153500-f1b38a6
  - 本地回滚：完成
  - 远程推送：完成
  - 新提交ID：abc1234

恢复备份：
git checkout backup-before-rollback-20260302-153500-f1b38a6

验证回滚：
git log --oneline -3
```

### 示例 2：回滚多次提交
```
用户："回滚最近 3 次提交"

Kiro：
📋 回滚信息确认

将要回滚的提交（共 3 次）：
  - f1b38a6: docs: 修正Git回滚功能Phase3完善实现文档
  - 0ef4cc6: test: 完成Git回滚功能Phase3基线测试（步骤8）
  - 0a32e38: test: 清理基线测试文件

回滚方式：git revert（安全，保留历史）
回滚顺序：从新到旧依次回滚

影响的文件：
  - doc/project/20260302_prompt基座架构设计/29-Git回滚功能Phase3完善实现.md
  - doc/project/20260302_prompt基座架构设计/28-Git回滚功能Phase3基线测试.md
  - test-baseline.txt

⚠️ 注意：
  - 回滚后会创建 3 个新的提交
  - 回滚操作会立即推送到远程仓库
  - 如果回滚错误，可以再次 revert 恢复

确认执行回滚吗？(yes/no)

用户："yes"

Kiro：
✅ 已创建备份分支：backup-before-rollback-20260302-153600-f1b38a6

[执行 git revert --no-edit HEAD~2..HEAD]
[执行 git push]

✅ 回滚成功！

回滚详情：
  - 备份分支：backup-before-rollback-20260302-153600-f1b38a6
  - 本地回滚：完成（3 次提交）
  - 远程推送：完成
  - 新提交ID：def5678

恢复备份：
git checkout backup-before-rollback-20260302-153600-f1b38a6

验证回滚：
git log --oneline -5
```

### 示例 3：功能关闭
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

### 示例 4：用户取消
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
- `doc/project/20260302_prompt基座架构设计/27-Git回滚功能Phase3测试计划.md`

---

**文档创建时间**：2026-03-02 13:35  
**文档更新时间**：2026-03-02 15:40  
**版本**：v1.0（完整版）  
**状态**：✅ 可用

**更新说明**：
- Phase 2 MVP：只支持回滚单次提交
- Phase 3 完整版：新增回滚多次提交、自动备份分支
