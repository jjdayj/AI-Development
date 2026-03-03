# 需求文档

## 简介

VibCoding 工作流增强功能旨在为 Prompt 基座项目的双轨工作流系统添加模块化需求管理能力。该功能将在工作流开始时自动收集模块信息，创建标准化的需求目录结构，并在工作流结束时提供状态更新和 Git 提交触发选项。

本功能同时适配 VibCoding 的双轨工作流：简单工作流和复杂 Prompt 工作流，所有增强能力在两套工作流中均可生效。

该功能将增强现有的 VibCoding 工作流（Prompt 工作流），使其能够：
- 自动管理需求元信息（meta.yaml）
- 维护当前工作上下文（current_context.yaml）
- 与 Git 提交模块无缝集成
- 支持多需求并行开发和切换

## 术语表

- **VibCoding_Workflow**: Prompt 基座项目的双轨工作流之一，专门用于 Prompt 工程开发，包含 5 个阶段（理解需求、设计方案、实现、验证、总结反思）
- **Module**: 模块，Prompt 基座项目的功能单元，位于 `.kiro/modules/{module}/{version}/` 目录
- **Requirement**: 需求，描述模块功能的文档，位于 `requirements/{module}/{version}/` 目录
- **Meta_Yaml**: 需求元信息文件，包含需求主题、模块名、版本号、状态等信息
- **Current_Context_Yaml**: 当前上下文文件，记录当前正在开发的需求信息，位于 `.kiro/current_context.yaml`
- **Git_Commit_Module**: Git 提交模块，负责生成规范化的 Git 提交信息
- **Kebab_Case**: 短横线命名法，如 `my-module-name`
- **SemVer**: 语义化版本号，格式为 `vMAJOR.MINOR.PATCH`，如 `v1.0.0`
- **Kiro**: AI 助手，执行工作流的主体

## 需求

### 需求 1：工作流启动时的模块信息收集

**用户故事：** 作为开发者，我希望在启动 VibCoding 工作流时能够方便地指定或选择模块信息，以便系统能够自动创建和管理需求文档。

#### 验收标准

1. WHEN Kiro 检测到用户启动 VibCoding 工作流，THE Kiro SHALL 询问用户提供模块名称、版本号和需求主题
2. WHEN 用户输入模块名称，THE Kiro SHALL 验证模块名称符合 kebab-case 格式（仅包含小写字母、数字和短横线，不以短横线开头或结尾）
3. WHEN 用户输入版本号，THE Kiro SHALL 验证版本号符合 SemVer 2.0.0 格式规范：必须以 `v` 开头，后跟 `MAJOR.MINOR.PATCH` 格式的版本核心（MAJOR、MINOR、PATCH 为非负整数，禁止前导零），可选支持预发布版本后缀（如 `v1.0.0-alpha.1`），可选支持构建元数据后缀（如 `v1.0.0+20260304`）
4. WHEN 版本号格式不符合要求，THE Kiro SHALL 向用户展示官方规范和正确示例，并要求重新输入
5. WHEN 系统检测到 `requirements/` 目录下已存在模块，THE Kiro SHALL 提供现有模块列表供用户选择
6. WHEN 用户选择现有模块，THE Kiro SHALL 读取该模块已有的所有版本，基于 SemVer 规范自动推荐下一个版本号（小迭代推荐 MINOR 版本升级，bug 修复推荐 PATCH 版本升级）
7. WHEN 用户选择推荐的版本号，THE Kiro SHALL 自动填充版本号输入框
8. WHEN 用户提供的信息验证通过，THE Kiro SHALL 记录模块名称、版本号和需求主题以供后续步骤使用

### 需求 2：自动创建需求目录结构

**用户故事：** 作为开发者，我希望系统能够自动创建标准化的需求目录结构，以便我可以专注于需求内容而不是目录管理。

#### 验收标准

1. WHEN Kiro 收集到有效的模块信息，THE Kiro SHALL 检查 `requirements/{module}/{version}/` 目录是否存在
2. IF 目录不存在，THEN THE Kiro SHALL 创建 `requirements/{module}/{version}/` 目录
3. IF 目录已存在，THEN THE Kiro SHALL 询问用户是否覆盖现有目录、使用现有目录或取消操作
4. WHEN 用户选择覆盖现有目录，THE Kiro SHALL 备份现有目录到 `requirements/{module}/{version}.backup.{timestamp}/` 然后创建新目录
5. WHEN 目录创建或确认后，THE Kiro SHALL 在该目录下创建 `docs/` 子目录用于存放需求相关文档
6. WHEN 目录结构创建完成，THE Kiro SHALL 通知用户目录路径并继续工作流
7. WHEN 用户输入的模块为全新模块（`.kiro/modules/` 下无对应目录），THE Kiro SHALL 询问用户是否自动初始化模块目录结构
8. WHEN 用户确认初始化，THE Kiro SHALL 复制 `.kiro/templates/module/` 下的模板，自动创建 `.kiro/modules/{module}/{version}/` 完整目录结构

### 需求 3：自动生成需求元信息文件

**用户故事：** 作为开发者，我希望系统能够自动生成标准化的 meta.yaml 文件，以便需求元信息格式统一且包含所有必需字段。

#### 验收标准

1. WHEN 需求目录结构创建完成，THE Kiro SHALL 根据用户输入的信息生成 `requirements/{module}/{version}/meta.yaml` 文件
2. THE Meta_Yaml SHALL 包含以下必需字段：theme（需求主题）、module（模块名称）、version（版本号）、author（作者）、date（创建日期 YYYY-MM-DD）、status（状态）、description（描述）、git_commit_prefix（Git 提交前缀）
3. THE Meta_Yaml SHALL 将 status 字段初始化为"开发中"
4. THE Meta_Yaml SHALL 将 git_commit_prefix 字段设置为 `feat({module}-{version})` 格式
5. THE Meta_Yaml SHALL 将 author 字段优先从 `git config user.name` 中获取，获取失败时使用默认值"yangzhuo"
6. THE Meta_Yaml SHALL 将 date 字段设置为当前日期（YYYY-MM-DD 格式）
7. WHEN meta.yaml 文件已存在且用户选择使用现有目录，THE Kiro SHALL 保留现有 meta.yaml 文件不做修改
8. WHEN meta.yaml 生成完成，THE Kiro SHALL 复制 `.kiro/templates/requirement/requirement.md.template` 模板到 `requirements/{module}/{version}/requirement.md`，并自动填充模块名、版本号、主题等元信息

### 需求 4：工作流结束时的状态更新

**用户故事：** 作为开发者，我希望在完成工作流后能够更新需求状态，以便跟踪需求的进展情况。

#### 验收标准

1. WHEN VibCoding 工作流的 Phase 5（总结与反思）完成，THE Kiro SHALL 询问用户是否更新 meta.yaml 的状态字段
2. WHEN 用户确认更新状态，THE Kiro SHALL 提供状态选项：开发中、已完成、已暂停、已取消
3. WHEN 用户选择新状态，THE Kiro SHALL 更新 `requirements/{module}/{version}/meta.yaml` 的 status 字段
4. WHEN 状态更新完成，THE Kiro SHALL 在 meta.yaml 中添加或更新 updated_at 字段为当前日期时间（YYYY-MM-DD HH:MM:SS 格式）
5. WHEN 用户选择不更新状态，THE Kiro SHALL 保持 meta.yaml 文件不变并继续后续步骤

### 需求 5：Git 提交触发选项

**用户故事：** 作为开发者，我希望在工作流结束时能够选择是否立即提交代码，以便将需求开发成果及时保存到版本控制系统。

#### 验收标准

1. WHEN VibCoding 工作流结束（5 个核心阶段完成且状态更新步骤完成），THE Kiro SHALL 询问用户是否触发 Git 提交
2. WHEN 用户确认触发 Git 提交，THE Kiro SHALL 确保 current_context.yaml 已写入当前需求的完整信息，然后通过关键词触发 Git_Commit_Module
3. WHEN 调用 Git_Commit_Module，THE Kiro SHALL 向其传递当前需求的提交描述，Git_Commit_Module 自动从 current_context.yaml 读取 meta 路径、提交前缀等信息
4. WHEN Git_Commit_Module 执行完成，THE Kiro SHALL 显示提交结果并结束工作流
5. WHEN 用户选择不触发 Git 提交，THE Kiro SHALL 直接结束工作流

### 需求 6：当前上下文管理

**用户故事：** 作为开发者，我希望系统能够记住当前正在开发的需求，以便在多个需求之间切换时保持上下文连续性。

#### 验收标准

1. WHEN VibCoding 工作流启动且模块信息收集完成，THE Kiro SHALL 将当前需求信息写入 `.kiro/current_context.yaml` 文件
2. THE Current_Context_Yaml SHALL 遵循统一的嵌套结构，包含以下字段：
   - `active_requirement`: 当前活跃需求信息
     - `theme`: 需求主题
     - `module`: 模块名称
     - `version`: 版本号
     - `requirement_path`: 需求目录路径
     - `meta_path`: meta.yaml 文件路径
     - `started_at`: 开始时间（YYYY-MM-DD HH:MM:SS）
     - `current_phase`: 当前工作流阶段（可选）
     - `paused_at`: 暂停时间（可选）
     - `completed_at`: 完成时间（可选）
   - `environment`: 当前工作环境
     - `current_directory`: 当前工作目录
     - `current_file`: 当前打开的文件
     - `current_file_type`: 当前文件类型
   - `updated_at`: 最后更新时间
3. IF `.kiro/current_context.yaml` 文件已存在，THEN THE Kiro SHALL 询问用户是否覆盖现有上下文或取消操作
4. WHEN 用户选择覆盖现有上下文，THE Kiro SHALL 备份现有文件到 `.kiro/current_context.yaml.backup.{timestamp}` 然后写入新上下文
5. WHEN VibCoding 工作流结束，THE Kiro SHALL 询问用户是否清除 current_context.yaml 文件
6. WHEN 用户确认清除上下文，THE Kiro SHALL 删除 `.kiro/current_context.yaml` 文件
7. WHEN 用户选择保留上下文，THE Kiro SHALL 在 current_context.yaml 的 `active_requirement.completed_at` 字段中记录当前日期时间

### 需求 7：需求切换支持

**用户故事：** 作为开发者，我希望能够在工作流执行过程中切换到其他需求，以便灵活应对多任务开发场景。

#### 验收标准

1. WHEN 用户在 VibCoding 工作流的任意阶段请求切换需求，THE Kiro SHALL 询问用户是否保存当前进度
2. WHEN 用户确认保存进度，THE Kiro SHALL 除了更新 current_context.yaml 的 `active_requirement.paused_at` 和 `active_requirement.current_phase` 字段，还需将完整的进度信息备份到 `requirements/{module}/{version}/.workflow_progress.yaml` 文件中
3. WHEN 进度保存完成，THE Kiro SHALL 重新执行需求 1 的模块信息收集流程
4. WHEN 新需求信息收集完成，THE Kiro SHALL 更新 current_context.yaml 为新需求信息
5. WHEN 用户选择不保存进度，THE Kiro SHALL 直接更新 current_context.yaml 为新需求信息
6. WHEN 用户选择恢复之前暂停的需求，THE Kiro SHALL 从对应需求目录的 `.workflow_progress.yaml` 中读取进度信息，恢复到当前工作流中

### 需求 8：错误处理和验证

**用户故事：** 作为开发者，我希望系统能够妥善处理各种错误情况，以便在出现问题时得到清晰的提示和恢复选项。

#### 验收标准

1. WHEN 文件系统操作失败（如权限不足、磁盘空间不足），THE Kiro SHALL 显示详细错误信息并询问用户是否重试或取消
2. WHEN YAML 文件解析失败，THE Kiro SHALL 显示解析错误位置和原因，并提供修复建议
3. WHEN 用户输入的模块名称或版本号格式无效，THE Kiro SHALL 显示格式要求和示例，并要求用户重新输入
4. WHEN Git_Commit_Module 调用失败，THE Kiro SHALL 显示失败原因并询问用户是否重试或跳过
5. WHEN 备份文件创建失败，THE Kiro SHALL 警告用户并询问是否继续操作（可能导致数据丢失）

### 需求 9：工作流集成点

**用户故事：** 作为系统架构师，我希望该功能能够无缝集成到现有的 VibCoding 工作流中，以便不破坏现有工作流的执行逻辑。

本功能通过前置钩子 + 后置钩子的方式集成到现有 VibCoding 工作流中，不修改现有 5 个核心阶段（理解需求、设计方案、实现、验证、总结反思）的执行逻辑，仅在固定节点插入增强功能：

- **前置钩子（工作流启动前）**：在现有 5 个阶段开始前执行
- **后置钩子（工作流结束后）**：在现有 5 个阶段全部完成后执行

#### 验收标准

1. THE Kiro SHALL 在 VibCoding 工作流的前置钩子中，依次执行「模块信息收集（需求 1）→ 需求目录创建（需求 2）→ 元信息生成（需求 3）→ 当前上下文写入（需求 6）」的功能
2. THE Kiro SHALL 在 VibCoding 工作流的后置钩子中，依次执行「需求状态更新（需求 4）→ Git 提交触发（需求 5）→ 上下文清理询问（需求 6）」的功能
3. WHEN 用户在工作流 5 个核心阶段的任意节点请求切换需求，THE Kiro SHALL 暂停当前工作流，执行需求 7 的需求切换功能，切换完成后可选择恢复工作流或重新开始
4. THE Kiro SHALL 确保所有增强功能的执行不影响现有 5 个核心阶段的正常执行流程
5. THE Kiro SHALL 确保在任何增强功能执行失败时，提供降级选项（跳过该功能）以保证核心工作流能够继续执行


## 非功能性需求

### 性能需求

1. THE System SHALL 在 3 秒内完成模块信息验证、目录创建、元信息生成的全流程
2. THE System SHALL 在 2 秒内完成需求切换和上下文备份/恢复操作

### 可靠性需求

1. THE System SHALL 在执行所有文件修改操作前先创建备份，确保任何异常情况下都不会丢失用户数据
2. WHEN 单个步骤的执行失败，THE System SHALL 不影响整个工作流的继续执行，并提供降级/跳过选项

### 兼容性需求

1. THE System SHALL 完全兼容现有的 VibCoding 双轨工作流（简单工作流/复杂工作流）
2. THE System SHALL 完全兼容「动态模块加载器」「Git 提交自动化联动」的所有数据格式和接口规范
3. THE System SHALL 支持 Windows、macOS、Linux 全平台的文件系统操作

### 可维护性需求

1. THE System SHALL 将所有工作流增强逻辑与现有工作流核心逻辑完全解耦，通过钩子方式集成，便于后续修改和扩展
2. THE System SHALL 将所有文件路径、命名规范、字段格式采用统一常量定义，避免硬编码
