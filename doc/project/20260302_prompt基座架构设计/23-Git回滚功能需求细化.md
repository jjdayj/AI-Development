# Git 回滚功能需求细化规格说明

## 文档说明
本文档基于需求探索和架构决策，详细定义 Git 回滚功能的需求规格、验收标准和测试用例。

---

## 需求编号规则

- **REQ-6.x**：Git 回滚功能需求
- **REQ-6.1.x**：全局开关相关
- **REQ-6.2.x**：指令解析相关
- **REQ-6.3.x**：回滚执行相关
- **REQ-6.4.x**：安全确认相关
- **REQ-6.5.x**：备份策略相关

---

## REQ-6.1：全局开关功能

### REQ-6.1.1：配置文件支持
**需求描述**：
在 `kiro.yaml` 的 `experimental` 部分添加 `git_auto_rollback` 配置项。

**详细说明**：
```yaml
experimental:
  git_auto_rollback: false  # 默认关闭
```

**验收标准**：
- [ ] `kiro.yaml` 中存在 `experimental.git_auto_rollback` 配置项
- [ ] 默认值为 `false`
- [ ] 配置项类型为布尔值（true/false）
- [ ] 配置文件格式正确，可以被 YAML 解析器读取

**测试用例**：
```yaml
# TC-6.1.1-1: 默认配置
experimental:
  git_auto_rollback: false
预期：功能关闭

# TC-6.1.1-2: 开启配置
experimental:
  git_auto_rollback: true
预期：功能开启

# TC-6.1.1-3: 缺少配置
experimental: {}
预期：使用默认值 false
```

---

### REQ-6.1.2：配置读取功能
**需求描述**：
系统能够正确读取 `git_auto_rollback` 配置项的值。

**详细说明**：
- 读取 `.kiro/kiro.yaml` 文件
- 解析 `experimental.git_auto_rollback` 配置
- 如果配置不存在，使用默认值 `false`
- 如果配置格式错误，提示错误并使用默认值

**验收标准**：
- [ ] 能够正确读取配置文件
- [ ] 能够正确解析布尔值
- [ ] 配置不存在时使用默认值
- [ ] 配置格式错误时有友好提示

**测试用例**：
```python
# TC-6.1.2-1: 正常读取
config = {'experimental': {'git_auto_rollback': True}}
assert is_rollback_enabled(config) == True

# TC-6.1.2-2: 默认值
config = {}
assert is_rollback_enabled(config) == False

# TC-6.1.2-3: 格式错误
config = {'experimental': {'git_auto_rollback': 'yes'}}
assert is_rollback_enabled(config) == False  # 使用默认值
```

---

### REQ-6.1.3：功能关闭时的提示
**需求描述**：
当功能关闭时，用户触发回滚指令应该收到清晰的提示信息。

**详细说明**：
提示信息应包含：
1. 功能已关闭的说明
2. 如何启用的步骤
3. 手动执行 Git 命令的方法
4. 相关文档链接

**验收标准**：
- [ ] 提示信息清晰易懂
- [ ] 包含启用步骤
- [ ] 包含手动命令示例
- [ ] 包含文档链接

**测试用例**：
```
# TC-6.1.3-1: 功能关闭时的提示
输入："回滚上一次提交"
配置：git_auto_rollback: false
预期输出：
⚠️ Git 自动回滚功能已关闭

如需启用，请修改 .kiro/kiro.yaml：
experimental:
  git_auto_rollback: true

或者手动执行 Git 命令：
git revert HEAD

提示：回滚是高风险操作，建议在熟悉流程后再启用。
```

---

## REQ-6.2：指令解析功能

### REQ-6.2.1：触发关键词识别
**需求描述**：
系统能够识别用户输入中的回滚触发关键词。

**详细说明**：
触发关键词包括：
- 中文：`回滚`、`撤销`、`恢复`
- 英文：`rollback`、`revert`

**验收标准**：
- [ ] 能够识别所有触发关键词
- [ ] 不区分大小写（英文）
- [ ] 支持关键词的不同位置
- [ ] 不会误识别非回滚指令

**测试用例**：
```python
# TC-6.2.1-1: 中文关键词
assert contains_rollback_keyword("回滚上一次提交") == True
assert contains_rollback_keyword("撤销最近的修改") == True
assert contains_rollback_keyword("恢复到之前的版本") == True

# TC-6.2.1-2: 英文关键词
assert contains_rollback_keyword("rollback to previous commit") == True
assert contains_rollback_keyword("revert HEAD") == True

# TC-6.2.1-3: 非回滚指令
assert contains_rollback_keyword("提交代码") == False
assert contains_rollback_keyword("查看日志") == False
```

---

### REQ-6.2.2：时间维度解析
**需求描述**：
系统能够解析用户输入中的回滚次数。

**详细说明**：
支持的表达方式：
- "回滚上一次提交" → 1次
- "回滚最近3次提交" → 3次
- "回滚最近的提交" → 1次
- 默认：1次

**验收标准**：
- [ ] 能够正确提取数字
- [ ] 支持中文数字（一、二、三）
- [ ] 支持阿拉伯数字（1、2、3）
- [ ] 默认值为1

**测试用例**：
```python
# TC-6.2.2-1: 明确次数
assert parse_rollback_count("回滚最近3次提交") == 3
assert parse_rollback_count("回滚最近五次提交") == 5

# TC-6.2.2-2: 默认次数
assert parse_rollback_count("回滚上一次提交") == 1
assert parse_rollback_count("回滚最近的提交") == 1

# TC-6.2.2-3: 无效次数
assert parse_rollback_count("回滚所有提交") == 1  # 使用默认值
```

---

### REQ-6.2.3：ID 维度解析
**需求描述**：
系统能够解析用户输入中的 commit ID。

**详细说明**：
支持的表达方式：
- "回滚 commit abc123"
- "回滚到 abc123"
- "撤销 commit abc123def"

**验收标准**：
- [ ] 能够识别7位短ID
- [ ] 能够识别40位完整ID
- [ ] 能够验证ID格式（16进制）
- [ ] ID不存在时有错误提示

**测试用例**：
```python
# TC-6.2.3-1: 短ID
assert parse_commit_id("回滚 commit abc123") == "abc123"

# TC-6.2.3-2: 完整ID
assert parse_commit_id("回滚到 abc123def456") == "abc123def456"

# TC-6.2.3-3: 无效ID
assert parse_commit_id("回滚 commit xyz") == None  # 非16进制
```

---

## REQ-6.3：回滚执行功能

### REQ-6.3.1：回滚方式选择
**需求描述**：
系统能够根据情况自动选择合适的回滚方式（revert 或 reset）。

**详细说明**：
决策逻辑：
```
IF 已推送到远程 THEN
    使用 git revert（强制）
ELSE IF 用户明确要求 reset THEN
    警告风险 → 用户确认 → 使用 git reset
ELSE
    使用 git revert（默认）
END IF
```

**验收标准**：
- [ ] 能够检测是否已推送到远程
- [ ] 默认使用 revert
- [ ] reset 需要用户明确确认
- [ ] 提供清晰的风险提示

**测试用例**：
```python
# TC-6.3.1-1: 已推送到远程
assert select_rollback_method(pushed=True) == "revert"

# TC-6.3.1-2: 未推送，默认
assert select_rollback_method(pushed=False) == "revert"

# TC-6.3.1-3: 未推送，用户要求reset
assert select_rollback_method(pushed=False, user_request="reset") == "reset"
```

---

### REQ-6.3.2：单次提交回滚
**需求描述**：
系统能够回滚单次提交。

**详细说明**：
- 使用 `git revert HEAD`
- 自动生成提交信息
- 推送到远程仓库

**验收标准**：
- [ ] 能够成功回滚最近一次提交
- [ ] 生成的提交信息清晰
- [ ] 自动推送到远程
- [ ] 工作目录保持干净

**测试用例**：
```bash
# TC-6.3.2-1: 回滚单次提交
初始状态：3次提交（A → B → C）
执行：回滚上一次提交
预期结果：4次提交（A → B → C → Revert C）
验证：git log --oneline 显示 Revert 提交
```

---

### REQ-6.3.3：多次提交回滚
**需求描述**：
系统能够回滚多次提交。

**详细说明**：
- 使用 `git revert HEAD~n..HEAD`
- 按顺序回滚每次提交
- 每次回滚生成一个提交

**验收标准**：
- [ ] 能够回滚指定次数的提交
- [ ] 回滚顺序正确（从新到旧）
- [ ] 每次回滚都有独立提交
- [ ] 所有回滚都推送到远程

**测试用例**：
```bash
# TC-6.3.3-1: 回滚3次提交
初始状态：5次提交（A → B → C → D → E）
执行：回滚最近3次提交
预期结果：8次提交（A → B → C → D → E → Revert E → Revert D → Revert C）
验证：git log --oneline 显示3个 Revert 提交
```

---

### REQ-6.3.4：指定 commit 回滚
**需求描述**：
系统能够回滚到指定的 commit ID。

**详细说明**：
- 使用 `git revert <commit-id>`
- 验证 commit ID 是否存在
- 生成清晰的提交信息

**验收标准**：
- [ ] 能够回滚指定的 commit
- [ ] commit 不存在时有错误提示
- [ ] 提交信息包含原 commit 信息
- [ ] 自动推送到远程

**测试用例**：
```bash
# TC-6.3.4-1: 回滚指定commit
初始状态：3次提交（A[abc123] → B[def456] → C[ghi789]）
执行：回滚 commit def456
预期结果：4次提交（A → B → C → Revert B）
验证：B 的修改被撤销，A 和 C 保持不变
```

---

## REQ-6.4：安全确认功能

### REQ-6.4.1：回滚信息展示
**需求描述**：
在执行回滚前，向用户展示详细的回滚信息。

**详细说明**：
展示内容包括：
1. 将要回滚的提交列表
2. 回滚方式（revert/reset）
3. 影响的文件列表
4. 风险提示

**验收标准**：
- [ ] 信息完整清晰
- [ ] 提交列表包含 ID 和消息
- [ ] 文件列表准确
- [ ] 风险提示醒目

**测试用例**：
```
# TC-6.4.1-1: 回滚信息展示
输入："回滚最近2次提交"
预期输出：
📋 回滚信息确认

将要回滚的提交：
  - 7690050: docs: 添加Git工作流程需求补充文档
  - 03b6619: 添加Git工作流程规范和自动化规则

回滚方式：git revert（安全，保留历史）

影响的文件：
  - doc/project/.../19-Git工作流程规范.md
  - doc/project/.../20-Git工作流程需求补充.md
  - .kiro/modules/ai-dev/v1.0/steering/git_workflow.md

⚠️ 注意：
  - 回滚后会创建新的提交
  - 回滚操作会立即推送到远程仓库
  - 如果回滚错误，可以再次 revert 恢复

确认执行回滚吗？(yes/no)
```

---

### REQ-6.4.2：用户确认机制
**需求描述**：
等待用户明确确认后才执行回滚操作。

**详细说明**：
- 接受的确认输入：`yes`、`y`、`是`、`确认`
- 拒绝的确认输入：`no`、`n`、`否`、`取消`
- 其他输入：提示重新输入

**验收标准**：
- [ ] 能够正确识别确认输入
- [ ] 能够正确识别拒绝输入
- [ ] 无效输入时提示重新输入
- [ ] 拒绝后取消回滚操作

**测试用例**：
```python
# TC-6.4.2-1: 确认输入
assert parse_confirmation("yes") == True
assert parse_confirmation("y") == True
assert parse_confirmation("是") == True

# TC-6.4.2-2: 拒绝输入
assert parse_confirmation("no") == False
assert parse_confirmation("n") == False
assert parse_confirmation("否") == False

# TC-6.4.2-3: 无效输入
assert parse_confirmation("maybe") == None  # 需要重新输入
```

---

### REQ-6.4.3：取消回滚操作
**需求描述**：
用户拒绝确认时，取消回滚操作并提示。

**详细说明**：
- 不执行任何 Git 操作
- 提示"回滚已取消"
- 工作目录保持不变

**验收标准**：
- [ ] 不执行 Git 命令
- [ ] 提示信息清晰
- [ ] 工作目录无变化
- [ ] 可以重新触发回滚

**测试用例**：
```
# TC-6.4.3-1: 取消回滚
输入："回滚上一次提交"
确认：no
预期输出：❌ 回滚已取消
验证：git log 无变化
```

---

## REQ-6.5：备份策略功能

### REQ-6.5.1：自动创建备份分支
**需求描述**：
在执行回滚前，自动创建备份分支。

**详细说明**：
- 备份分支命名：`backup-before-rollback-<timestamp>-<commit-id>`
- 时间戳格式：`YYYYMMdd-HHmmss`
- commit-id：当前 commit 的短 ID（7位）

**验收标准**：
- [ ] 自动创建备份分支
- [ ] 分支命名符合规范
- [ ] 备份分支指向当前 commit
- [ ] 不影响当前分支

**测试用例**：
```bash
# TC-6.5.1-1: 创建备份分支
当前commit：7690050
执行时间：2026-03-02 12:30:45
预期分支名：backup-before-rollback-20260302-123045-7690050
验证：git branch 显示备份分支
```

---

### REQ-6.5.2：备份分支配置
**需求描述**：
支持通过配置控制备份行为。

**详细说明**：
配置项：
```json
{
  "rollback": {
    "backup": {
      "enabled": true,
      "push_to_remote": false,
      "auto_delete_after_days": 7
    }
  }
}
```

**验收标准**：
- [ ] 能够读取备份配置
- [ ] `enabled: false` 时不创建备份
- [ ] `push_to_remote: true` 时推送备份分支
- [ ] 自动删除过期备份分支

**测试用例**：
```python
# TC-6.5.2-1: 禁用备份
config = {'rollback': {'backup': {'enabled': False}}}
执行回滚
验证：不创建备份分支

# TC-6.5.2-2: 推送备份
config = {'rollback': {'backup': {'push_to_remote': True}}}
执行回滚
验证：备份分支推送到远程
```

---

### REQ-6.5.3：备份分支清理
**需求描述**：
自动清理过期的备份分支。

**详细说明**：
- 根据 `auto_delete_after_days` 配置
- 0 表示不自动删除
- 大于0表示删除超过指定天数的备份

**验收标准**：
- [ ] 能够识别过期备份分支
- [ ] 自动删除过期分支
- [ ] 不删除未过期分支
- [ ] 删除前有日志记录

**测试用例**：
```python
# TC-6.5.3-1: 清理过期备份
配置：auto_delete_after_days: 7
备份分支：backup-before-rollback-20260225-120000-abc123（8天前）
执行清理
验证：分支被删除

# TC-6.5.3-2: 保留未过期备份
配置：auto_delete_after_days: 7
备份分支：backup-before-rollback-20260301-120000-def456（1天前）
执行清理
验证：分支保留
```

---

## 边界情况处理

### EDGE-6.1：回滚次数超过总提交数
**场景**：用户要求回滚5次，但只有3次提交

**处理方案**：
1. 检测总提交数
2. 提示用户实际可回滚次数
3. 询问是否回滚所有提交

**测试用例**：
```
输入："回滚最近5次提交"
当前提交数：3
预期输出：
⚠️ 当前只有3次提交，无法回滚5次

是否回滚所有3次提交？(yes/no)
```

---

### EDGE-6.2：commit ID 不存在
**场景**：用户指定的 commit ID 不存在

**处理方案**：
1. 验证 commit ID
2. 提示 ID 不存在
3. 建议使用 `git log` 查看

**测试用例**：
```
输入："回滚 commit xyz123"
预期输出：
❌ commit ID 不存在：xyz123

请使用以下命令查看提交历史：
git log --oneline -10
```

---

### EDGE-6.3：工作目录有未提交修改
**场景**：工作目录有未提交的修改

**处理方案**：
1. 检测工作目录状态
2. 提示用户先提交或暂存
3. 不执行回滚操作

**测试用例**：
```
输入："回滚上一次提交"
工作目录：有未提交修改
预期输出：
⚠️ 工作目录有未提交的修改

请先提交或暂存修改：
git add .
git commit -m "..."

或者暂存修改：
git stash
```

---

### EDGE-6.4：回滚导致冲突
**场景**：回滚操作导致合并冲突

**处理方案**：
1. 检测冲突
2. 提示用户解决冲突
3. 提供解决步骤

**测试用例**：
```
执行：git revert HEAD
结果：冲突
预期输出：
⚠️ 回滚操作产生冲突

请手动解决冲突：
1. 编辑冲突文件
2. git add <冲突文件>
3. git revert --continue

或者放弃回滚：
git revert --abort
```

---

### EDGE-6.5：网络问题导致推送失败
**场景**：回滚成功但推送失败

**处理方案**：
1. 本地回滚已完成
2. 提示推送失败
3. 建议手动推送

**测试用例**：
```
执行：回滚成功，推送失败
预期输出：
✅ 本地回滚成功
❌ 推送到远程失败：网络错误

请稍后手动推送：
git push
```

---

## 需求优先级

| 优先级 | 需求编号 | 需求名称 | 理由 |
|--------|---------|---------|------|
| P0 | REQ-6.1.1 | 配置文件支持 | 基础功能 |
| P0 | REQ-6.1.2 | 配置读取功能 | 基础功能 |
| P0 | REQ-6.2.1 | 触发关键词识别 | 核心功能 |
| P0 | REQ-6.3.1 | 回滚方式选择 | 核心功能 |
| P0 | REQ-6.3.2 | 单次提交回滚 | 核心功能 |
| P0 | REQ-6.4.1 | 回滚信息展示 | 安全性 |
| P0 | REQ-6.4.2 | 用户确认机制 | 安全性 |
| P1 | REQ-6.1.3 | 功能关闭提示 | 用户体验 |
| P1 | REQ-6.2.2 | 时间维度解析 | 易用性 |
| P1 | REQ-6.3.3 | 多次提交回滚 | 扩展功能 |
| P1 | REQ-6.5.1 | 自动创建备份 | 安全性 |
| P2 | REQ-6.2.3 | ID 维度解析 | 高级功能 |
| P2 | REQ-6.3.4 | 指定 commit 回滚 | 高级功能 |
| P2 | REQ-6.5.2 | 备份分支配置 | 灵活性 |
| P2 | REQ-6.5.3 | 备份分支清理 | 维护性 |

---

## 验收标准总结

### 功能完整性
- [ ] 所有 P0 需求实现
- [ ] 所有 P1 需求实现
- [ ] 至少 50% P2 需求实现

### 安全性
- [ ] 必须二次确认
- [ ] 自动创建备份
- [ ] 清晰的风险提示

### 易用性
- [ ] 自然语言指令
- [ ] 清晰的提示信息
- [ ] 友好的错误处理

### 可靠性
- [ ] 所有测试用例通过
- [ ] 边界情况正确处理
- [ ] 错误恢复机制完善

---

## 下一步

根据 VibCoding 流程，Phase 1（探索与决策）已完成：
1. ✅ 需求探索
2. ✅ 架构决策
3. ✅ 需求细化

**下一步**：进入 Phase 2（快速原型）
- MVP 实现：只实现 P0 需求
- 快速测试：验证核心功能
- 反馈收集：根据测试结果调整

**当前状态**：✅ Phase 1 完成，准备进入 Phase 2

---

**文档创建时间**：2026-03-02 13:00  
**文档作者**：Kiro (Claude Sonnet 4.5)  
**文档状态**：✅ 完整

**重要性**：🔥 最高（需求规格说明）
