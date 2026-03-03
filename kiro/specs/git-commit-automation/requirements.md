# Git 提交自动化联动 - 需求文档

## 简介

Git 提交自动化联动功能旨在增强 Prompt 基座项目的 Git 提交模块，实现与需求管理系统的自动联动。该功能通过自动读取需求元信息（meta.yaml）和当前上下文（current_context.yaml），生成规范的提交信息，并在提交前执行安全检查，确保代码提交的规范性和安全性。

本功能主要服务于 Kiro AI Assistant，帮助其在完成需求开发后快速、规范地提交代码。

## 术语表

- **System**: Git 提交自动化系统
- **Meta_File**: 需求元信息文件（requirements/{module}/{version}/meta.yaml）
- **Context_File**: 当前上下文文件（.kiro/current_context.yaml）
- **Commit_Prefix**: 提交前缀（如 "feat(workflow-v1.0)"）
- **Workspace**: Git 工作区
- **Staged_Files**: 已暂存的文件
- **Protected_Branch**: 保护分支（如 main、master、production）
- **Security_Checker**: 安全检查器模块

## 需求

### 需求 1: 自动读取需求元信息

**用户故事**: 作为 Kiro AI Assistant，我希望系统能够自动读取需求元信息，以便生成规范的提交前缀。

#### 验收标准

1. WHEN 用户触发提交操作，THE System SHALL 首先检查 Context_File 是否存在
2. IF Context_File 存在，THEN THE System SHALL 从 Context_File 读取当前关联的模块名称和版本号
3. WHEN 模块名称和版本号已知，THE System SHALL 根据路径模板 "requirements/{module}/{version}/meta.yaml" 定位 Meta_File
4. WHEN Meta_File 存在且可读，THE System SHALL 提取 git_commit_prefix 字段
5. IF Meta_File 不存在或无法读取，THEN THE System SHALL 提示用户手动输入或选择需求信息
6. WHEN 提取 git_commit_prefix 成功，THE System SHALL 将其存储为提交前缀

### 需求 2: 生成规范提交信息

**用户故事**: 作为 Kiro AI Assistant，我希望系统能够生成符合规范的提交信息，以便保持提交历史的一致性。

#### 验收标准

1. WHEN 用户提供提交描述，THE System SHALL 使用模板 "{prefix}: {description}" 生成完整提交信息
2. WHEN 提交描述包含多行内容，THE System SHALL 将第一行作为标题，其余行作为详细描述
3. THE System SHALL 确保提交信息标题不超过 72 个字符
4. WHEN 提交信息标题超过 72 个字符，THE System SHALL 截断并添加省略号
5. THE System SHALL 在标题和详细描述之间插入空行
6. WHEN 用户未提供提交描述，THE System SHALL 提示用户输入提交描述

### 需求 3: 提交前安全检查

**用户故事**: 作为开发者，我希望系统在提交前执行安全检查，以便避免提交敏感文件或在错误的分支上提交。

#### 验收标准

1. WHEN 执行提交操作前，THE System SHALL 调用 Security_Checker 检查 Staged_Files
2. WHEN Security_Checker 检测到敏感文件，THE System SHALL 列出敏感文件清单并阻止提交
3. WHEN Security_Checker 检测到超过阻止阈值的大文件，THE System SHALL 列出大文件清单并阻止提交
4. WHEN Security_Checker 检测到警告级别的大文件，THE System SHALL 显示警告但允许继续
5. WHEN 当前分支为 Protected_Branch，THE System SHALL 显示警告并要求用户确认
6. WHEN 存在阻止性问题，THE System SHALL 终止提交流程并给出清晰的错误提示
7. WHEN 所有检查通过，THE System SHALL 继续执行提交操作

### 需求 4: 工作区状态检查

**用户故事**: 作为开发者，我希望系统检查工作区状态，以便确保在正确的状态下提交代码。

#### 验收标准

1. WHEN 执行提交操作前，THE System SHALL 检查 Workspace 是否为 Git 仓库
2. IF Workspace 不是 Git 仓库，THEN THE System SHALL 返回错误信息并终止操作
3. WHEN Workspace 是 Git 仓库，THE System SHALL 检查是否有 Staged_Files
4. IF 没有 Staged_Files，THEN THE System SHALL 提示用户先暂存文件
5. WHEN 存在未解决的合并冲突，THE System SHALL 阻止提交并提示用户解决冲突
6. WHEN 当前分支处于 detached HEAD 状态，THE System SHALL 警告用户并要求确认

### 需求 5: 自动推送到远程

**用户故事**: 作为开发者，我希望提交成功后能够自动推送到远程仓库，以便快速同步代码。

#### 验收标准

1. WHEN 提交成功后，THE System SHALL 询问用户是否推送到远程仓库
2. WHEN 用户确认推送，THE System SHALL 执行 git push 命令
3. WHEN 推送成功，THE System SHALL 显示成功消息
4. IF 推送失败，THEN THE System SHALL 捕获错误信息并显示给用户
5. WHEN 推送失败原因为远程分支不存在，THE System SHALL 提示用户使用 --set-upstream 选项
6. WHEN 推送失败原因为本地分支落后于远程，THE System SHALL 提示用户先拉取远程更改
7. WHERE 配置文件中 auto_push 设置为 true，THE System SHALL 跳过询问直接推送

### 需求 6: 与 current_context.yaml 集成

**用户故事**: 作为 Kiro AI Assistant，我希望系统能够读取和更新 current_context.yaml，以便跟踪当前工作的需求上下文。

#### 验收标准

1. WHEN 执行提交操作时，THE System SHALL 优先从 Context_File 读取当前需求信息
2. IF Context_File 不存在，THEN THE System SHALL 提示用户选择或输入需求信息
3. WHEN 用户选择需求信息后，THE System SHALL 询问是否创建 Context_File
4. WHEN 用户确认创建 Context_File，THE System SHALL 将需求信息写入 Context_File
5. WHEN 提交成功后，THE System SHALL 询问是否更新 Context_File 的状态字段
6. WHERE 配置文件中 update_meta_status 设置为 true，THE System SHALL 自动更新状态

### 需求 7: 用户交互与错误处理

**用户故事**: 作为用户，我希望系统提供清晰的交互提示和错误信息，以便我能够理解系统状态并采取正确的操作。

#### 验收标准

1. WHEN 系统需要用户输入时，THE System SHALL 提供清晰的提示信息
2. WHEN 发生错误时，THE System SHALL 显示错误类型和具体原因
3. WHEN 显示警告时，THE System SHALL 明确标注为警告并说明影响
4. WHEN 需要用户确认时，THE System SHALL 提供明确的选项（是/否）
5. WHEN 操作成功时，THE System SHALL 显示成功消息和相关信息（如提交哈希）
6. WHEN 执行耗时操作时，THE System SHALL 显示进度提示
7. THE System SHALL 使用中文提供所有用户交互信息

### 需求 8: 提交信息历史记录

**用户故事**: 作为开发者，我希望系统能够记录最近的提交信息，以便我可以快速重用或参考。

#### 验收标准

1. WHEN 提交成功后，THE System SHALL 将提交信息保存到历史记录文件
2. THE System SHALL 保留最近 10 条提交信息
3. WHEN 用户触发提交操作时，THE System SHALL 提供选项显示历史提交信息
4. WHEN 用户选择历史提交信息，THE System SHALL 将其填充到当前提交描述中
5. THE System SHALL 在历史记录中包含提交时间、分支名称和提交哈希

### 需求 9: 配置管理

**用户故事**: 作为项目维护者，我希望能够通过配置文件自定义系统行为，以便适应不同的项目需求。

#### 验收标准

1. THE System SHALL 从 .kiro/modules/git-commit/v1.0/config.yaml 读取配置
2. WHEN 配置文件不存在，THE System SHALL 使用默认配置
3. THE System SHALL 支持配置提交信息模板
4. THE System SHALL 支持配置是否自动推送
5. THE System SHALL 支持配置安全检查阈值（敏感文件模式、大文件阈值）
6. THE System SHALL 支持配置保护分支列表
7. WHEN 配置文件格式错误，THE System SHALL 显示错误信息并使用默认配置

### 需求 10: 触发方式识别

**用户故事**: 作为 Kiro AI Assistant，我希望能够识别用户的提交意图，以便自动触发提交流程。

#### 验收标准

1. WHEN 用户输入包含"提交代码"关键词，THE System SHALL 触发提交流程
2. WHEN 用户输入包含"git 提交"关键词，THE System SHALL 触发提交流程
3. WHEN 用户输入包含"commit"关键词，THE System SHALL 触发提交流程
4. WHEN 用户输入包含"推送代码"关键词，THE System SHALL 触发提交并推送流程
5. WHEN 用户输入包含"git push"关键词，THE System SHALL 触发提交并推送流程
6. THE System SHALL 支持用户在触发时直接指定提交描述
7. WHEN 用户指定提交描述，THE System SHALL 跳过提交描述输入步骤

## 非功能性需求

### 性能需求

1. THE System SHALL 在 2 秒内完成元信息读取和提交信息生成
2. THE System SHALL 在 5 秒内完成安全检查（针对少于 100 个文件）
3. THE System SHALL 支持处理包含最多 1000 个文件的提交

### 可靠性需求

1. WHEN 文件读取失败，THE System SHALL 提供降级方案（使用默认值或提示用户输入）
2. WHEN Git 命令执行失败，THE System SHALL 捕获错误并提供有意义的错误信息
3. THE System SHALL 确保不会因为配置错误而导致系统崩溃

### 兼容性需求

1. THE System SHALL 支持 Git 2.0 及以上版本
2. THE System SHALL 支持 Windows、macOS 和 Linux 操作系统
3. THE System SHALL 兼容现有的 .kiro 目录结构

### 可维护性需求

1. THE System SHALL 将核心逻辑与 Prompt 逻辑分离
2. THE System SHALL 提供清晰的日志记录功能
3. THE System SHALL 使用模块化设计，便于扩展和修改
