# Git 回滚功能架构决策（ADR）

## 文档说明
本文档记录 Git 回滚功能的架构决策，基于用户反馈和需求探索结果。

---

## ADR-005：回滚粒度设计

### 决策
支持指定单次/多次提交回滚，默认单次。

### 理由
1. **灵活性**：不同场景需要不同粒度
   - 单次回滚：修复最近一次错误
   - 多次回滚：整个对话都有问题
2. **安全性**：默认单次，降低误操作风险
3. **可扩展性**：未来可以支持更复杂的回滚场景

### 实现方案
```python
# 默认回滚 1 次提交
rollback_count = 1

# 支持指定回滚次数
rollback_count = parse_count_from_prompt(user_input)  # 例如："回滚最近3次提交"
```

### 影响
- 需要解析用户输入中的数量信息
- 需要验证回滚次数的合理性（不能超过总提交数）

---

## ADR-006：回滚方式选择

### 决策
优先使用 `git revert`，可选 `git reset` 并明确风险。

### 理由

#### 为什么优先 `git revert`？
1. **安全性**：不改写历史，保留所有提交记录
2. **可追溯**：回滚操作本身也会产生提交，方便审计
3. **协作友好**：不会影响其他人的工作
4. **可恢复**：如果回滚错误，可以再次 revert

#### 什么时候用 `git reset`？
1. **本地开发**：还未推送到远程
2. **个人分支**：确定不会影响他人
3. **用户明确要求**：理解风险并接受后果

### 实现方案

#### 方案 A：git revert（默认）
```bash
# 回滚单次提交
git revert HEAD --no-edit

# 回滚多次提交
git revert HEAD~2..HEAD --no-edit

# 推送到远程
git push
```

**优点**：
- ✅ 安全，不改写历史
- ✅ 保留完整记录
- ✅ 可以随时恢复

**缺点**：
- ⚠️ 会产生新的提交
- ⚠️ 提交历史会变长

#### 方案 B：git reset（可选）
```bash
# 回滚单次提交（保留修改）
git reset --soft HEAD~1

# 回滚单次提交（丢弃修改）
git reset --hard HEAD~1

# 强制推送到远程
git push --force
```

**优点**：
- ✅ 提交历史干净
- ✅ 可以重新修改后提交

**缺点**：
- ❌ 改写历史，危险
- ❌ 需要强制推送
- ❌ 可能影响他人

### 决策逻辑
```
IF 已推送到远程 THEN
    使用 git revert（强制）
ELSE IF 用户明确要求 reset THEN
    警告风险 → 用户确认 → 使用 git reset
ELSE
    使用 git revert（默认）
END IF
```

---

## ADR-007：触发方式设计

### 决策
自然语言指令 + 标准化关键词结合。

### 理由
1. **易用性**：用户不需要记复杂命令
2. **准确性**：标准化关键词避免歧义
3. **灵活性**：支持多种表达方式

### 触发关键词（必填）
用户指令中必须包含以下之一：
- `回滚`
- `撤销`
- `恢复`
- `rollback`
- `revert`

### 定位维度（可选）

#### 1. 时间维度（默认）
```
回滚上一次提交          → 回滚 1 次
回滚最近 3 次提交       → 回滚 3 次
回滚最近的提交          → 回滚 1 次
```

#### 2. ID 维度
```
回滚 commit abc123      → 回滚到指定 commit
回滚到 abc123           → 回滚到指定 commit
```

#### 3. 基准维度
```
回滚到 v1.0 版本        → 回滚到指定 tag
回滚到昨天的状态        → 回滚到指定时间
```

### 解析逻辑
```python
def parse_rollback_command(user_input):
    # 1. 检查是否包含触发关键词
    if not contains_keyword(user_input, ['回滚', '撤销', '恢复']):
        return None
    
    # 2. 解析定位维度
    if 'commit' in user_input or re.match(r'[0-9a-f]{7,}', user_input):
        # ID 维度
        commit_id = extract_commit_id(user_input)
        return {'type': 'commit', 'target': commit_id}
    
    elif '次' in user_input:
        # 时间维度（次数）
        count = extract_number(user_input)
        return {'type': 'count', 'target': count}
    
    elif '版本' in user_input or 'v' in user_input:
        # 基准维度（版本）
        version = extract_version(user_input)
        return {'type': 'version', 'target': version}
    
    else:
        # 默认：回滚 1 次
        return {'type': 'count', 'target': 1}
```

### 示例

| 用户输入 | 解析结果 | 执行操作 |
|---------|---------|---------|
| "回滚上一次提交" | `{'type': 'count', 'target': 1}` | `git revert HEAD` |
| "回滚最近3次提交" | `{'type': 'count', 'target': 3}` | `git revert HEAD~2..HEAD` |
| "回滚 commit abc123" | `{'type': 'commit', 'target': 'abc123'}` | `git revert abc123` |
| "撤销最近的修改" | `{'type': 'count', 'target': 1}` | `git revert HEAD` |

---

## ADR-008：安全确认机制

### 决策
必须二次确认，回滚前向用户展示详细信息并等待确认。

### 理由
1. **不可逆性**：回滚操作会产生新提交或改写历史
2. **误操作风险**：用户可能输入错误的指令
3. **透明性**：让用户清楚知道将要发生什么

### 确认流程
```
1. 用户输入回滚指令
   ↓
2. Kiro 解析指令
   ↓
3. Kiro 展示回滚信息：
   - 将要回滚的提交列表
   - 回滚方式（revert/reset）
   - 影响范围（文件列表）
   - 风险提示
   ↓
4. Kiro 询问："确认执行回滚吗？(yes/no)"
   ↓
5. 用户确认
   ↓
6. Kiro 执行回滚
   ↓
7. Kiro 报告结果
```

### 确认信息模板
```
📋 回滚信息确认

将要回滚的提交：
  - 7690050: docs: 添加Git工作流程需求补充文档
  - 03b6619: 添加Git工作流程规范和自动化规则

回滚方式：git revert（安全，保留历史）

影响的文件：
  - doc/project/20260302_prompt基座架构设计/19-Git工作流程规范.md
  - doc/project/20260302_prompt基座架构设计/20-Git工作流程需求补充.md
  - .kiro/modules/ai-dev/v1.0/steering/git_workflow.md

⚠️ 注意：
  - 回滚后会创建新的提交
  - 回滚操作会立即推送到远程仓库
  - 如果回滚错误，可以再次 revert 恢复

确认执行回滚吗？(yes/no)
```

### 实现方案
```python
def confirm_rollback(rollback_info):
    # 1. 展示回滚信息
    print_rollback_info(rollback_info)
    
    # 2. 等待用户确认
    user_input = input("确认执行回滚吗？(yes/no): ")
    
    # 3. 验证输入
    if user_input.lower() in ['yes', 'y', '是', '确认']:
        return True
    else:
        print("❌ 回滚已取消")
        return False
```

---

## ADR-009：备份策略设计

### 决策
默认自动创建备份分支，可选关闭。

### 理由
1. **安全性**：备份分支是最后的保险
2. **可恢复性**：如果回滚错误，可以从备份恢复
3. **灵活性**：允许用户关闭（如果确定不需要）

### 备份分支命名规则
```
backup-before-rollback-<timestamp>-<commit-id>

示例：
backup-before-rollback-20260302-123045-7690050
```

**命名规则说明**：
- `backup-before-rollback`：固定前缀
- `<timestamp>`：时间戳（YYYYMMdd-HHmmss）
- `<commit-id>`：当前 commit 的短 ID（7位）

### 实现方案
```bash
# 1. 创建备份分支
git branch backup-before-rollback-20260302-123045-7690050

# 2. 执行回滚操作
git revert HEAD

# 3. 推送备份分支到远程（可选）
git push origin backup-before-rollback-20260302-123045-7690050
```

### 备份分支管理
```python
# 配置项
backup_config = {
    'enabled': True,  # 是否启用备份
    'push_to_remote': False,  # 是否推送到远程
    'auto_delete_after_days': 7,  # 自动删除天数（0=不删除）
}

# 清理逻辑
def cleanup_old_backups():
    """清理超过指定天数的备份分支"""
    if backup_config['auto_delete_after_days'] > 0:
        # 查找所有备份分支
        backup_branches = find_backup_branches()
        
        # 删除过期分支
        for branch in backup_branches:
            if is_expired(branch, backup_config['auto_delete_after_days']):
                delete_branch(branch)
```

### 用户控制
用户可以通过配置文件控制备份行为：
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

---

## 架构决策总结

| ADR | 决策内容 | 关键点 |
|-----|---------|--------|
| ADR-005 | 回滚粒度 | 支持单次/多次，默认单次 |
| ADR-006 | 回滚方式 | 优先 revert，可选 reset |
| ADR-007 | 触发方式 | 自然语言 + 标准关键词 |
| ADR-008 | 安全确认 | 必须二次确认 |
| ADR-009 | 备份策略 | 默认自动备份 |

---

## 下一步

根据 VibCoding 流程，下一步是：
**步骤 3：需求细化（Requirement Specification）**

需要编写详细的需求规格说明，包括：
1. 功能需求（REQ-6.x）
2. 验收标准
3. 测试用例
4. 边界情况处理

**当前状态**：✅ 架构决策完成，等待进入需求细化

---

**文档创建时间**：2026-03-02 12:40  
**文档作者**：Kiro (Claude Sonnet 4.5)  
**文档状态**：✅ 完整

**重要性**：🔥 最高（核心架构决策）


---

## ADR-010：Git 回滚功能全局开关

### 决策
在 `kiro.yaml` 的 `experimental` 部分添加 `git_auto_rollback` 开关，控制是否允许通过 prompt 进行 Git 回滚。

### 理由

#### 为什么需要全局开关？
1. **安全性**：防止误操作导致的意外回滚
2. **权限控制**：团队协作时，可能只允许特定人员回滚
3. **环境隔离**：开发环境可以开启，生产环境必须关闭
4. **学习保护**：新用户可以先关闭，熟悉后再开启

#### 为什么放在 `experimental` 部分？
1. **功能定位**：Git 回滚是高级功能，属于实验性特性
2. **一致性**：与现有的 `auto_rfc_recording`、`prompt_effect_evaluation` 保持一致
3. **可扩展性**：未来可能添加更多回滚相关的实验性功能

### 配置设计

#### kiro.yaml 配置
```yaml
# 实验性功能开关（可选）
experimental:
  # 是否启用自动 RFC 记录
  auto_rfc_recording: false
  
  # 是否启用提示词效果评估
  prompt_effect_evaluation: true
  
  # 是否启用 Git 自动回滚功能
  git_auto_rollback: false  # 默认关闭（安全优先）
```

#### 默认值
- **默认值**：`false`（关闭）
- **理由**：安全优先，避免新用户误操作

### 行为定义

#### 开关开启时（`git_auto_rollback: true`）
```
用户输入："回滚上一次提交"
   ↓
Kiro 检查开关：✅ 已开启
   ↓
Kiro 解析指令 → 展示回滚信息 → 等待确认 → 执行回滚
```

#### 开关关闭时（`git_auto_rollback: false`）
```
用户输入："回滚上一次提交"
   ↓
Kiro 检查开关：❌ 已关闭
   ↓
Kiro 提示：
⚠️ Git 自动回滚功能已关闭

如需启用，请修改 .kiro/kiro.yaml：
experimental:
  git_auto_rollback: true

或者手动执行 Git 命令：
git revert HEAD

提示：回滚是高风险操作，建议在熟悉流程后再启用。
```

### 实现方案

#### 配置读取
```python
def is_rollback_enabled():
    """检查 Git 回滚功能是否启用"""
    config = load_kiro_config()
    return config.get('experimental', {}).get('git_auto_rollback', False)
```

#### 回滚入口检查
```python
def handle_rollback_command(user_input):
    """处理回滚指令"""
    # 1. 检查是否包含回滚关键词
    if not contains_rollback_keyword(user_input):
        return
    
    # 2. 检查功能是否启用
    if not is_rollback_enabled():
        print_rollback_disabled_message()
        return
    
    # 3. 解析回滚指令
    rollback_info = parse_rollback_command(user_input)
    
    # 4. 执行回滚流程
    execute_rollback(rollback_info)
```

#### 提示信息模板
```python
def print_rollback_disabled_message():
    """打印回滚功能已关闭的提示"""
    message = """
⚠️ Git 自动回滚功能已关闭

如需启用，请修改 .kiro/kiro.yaml：
experimental:
  git_auto_rollback: true

或者手动执行 Git 命令：
git revert HEAD        # 回滚最近一次提交
git revert HEAD~2..HEAD  # 回滚最近3次提交

提示：回滚是高风险操作，建议在熟悉流程后再启用。

相关文档：
- doc/project/20260302_prompt基座架构设计/19-Git工作流程规范.md
- doc/project/20260302_prompt基座架构设计/22-Git回滚功能架构决策.md
"""
    print(message)
```

### 使用场景

#### 场景 1：个人开发环境（推荐开启）
```yaml
experimental:
  git_auto_rollback: true
```
**理由**：个人开发，可以快速回滚错误

#### 场景 2：团队协作环境（推荐关闭）
```yaml
experimental:
  git_auto_rollback: false
```
**理由**：统一由项目负责人或 Tech Lead 回滚

#### 场景 3：生产环境（必须关闭）
```yaml
experimental:
  git_auto_rollback: false
```
**理由**：生产环境禁止自动回滚，必须走正式流程

#### 场景 4：学习阶段（推荐关闭）
```yaml
experimental:
  git_auto_rollback: false
```
**理由**：新用户先熟悉 Git 基础，再使用高级功能

### 配置管理

#### 配置文件位置
- 全局配置：`.kiro/kiro.yaml`
- 用户可以通过编辑器或命令行修改

#### 配置验证
```python
def validate_rollback_config(config):
    """验证回滚配置"""
    if 'experimental' not in config:
        return True  # 没有配置，使用默认值
    
    if 'git_auto_rollback' not in config['experimental']:
        return True  # 没有配置，使用默认值
    
    value = config['experimental']['git_auto_rollback']
    if not isinstance(value, bool):
        raise ValueError(f"git_auto_rollback 必须是布尔值，当前值：{value}")
    
    return True
```

#### 配置热更新
- 修改 `kiro.yaml` 后，下次对话自动生效
- 不需要重启 Kiro

### 与其他功能的关系

#### 与 Git 工作流程的关系
- Git 工作流程（提交）：始终启用，不受此开关影响
- Git 回滚：受此开关控制

#### 与备份策略的关系
- 如果回滚功能关闭，备份策略也不会触发
- 如果回滚功能开启，备份策略按 ADR-009 执行

#### 与安全确认的关系
- 如果回滚功能关闭，不会进入确认流程
- 如果回滚功能开启，必须经过二次确认（ADR-008）

### 文档更新

需要更新以下文档：
1. `kiro.yaml`：添加 `git_auto_rollback` 配置项
2. `00-快速参考.md`：说明如何启用/禁用回滚功能
3. `19-Git工作流程规范.md`：添加回滚功能开关说明
4. Steering 规则：添加开关检查逻辑

---

## 架构决策总结（更新）

| ADR | 决策内容 | 关键点 |
|-----|---------|--------|
| ADR-005 | 回滚粒度 | 支持单次/多次，默认单次 |
| ADR-006 | 回滚方式 | 优先 revert，可选 reset |
| ADR-007 | 触发方式 | 自然语言 + 标准关键词 |
| ADR-008 | 安全确认 | 必须二次确认 |
| ADR-009 | 备份策略 | 默认自动备份 |
| **ADR-010** | **全局开关** | **默认关闭，安全优先** |

---

**更新时间**：2026-03-02 12:50  
**更新内容**：添加 ADR-010（全局开关设计）
