# 需求文档：动态模块加载器

## 简介

动态模块加载器是 Kiro Prompt 基座的核心功能，负责在 AI 启动时根据配置文件动态加载启用的模块 Steering 规则。该功能实现了模块化的 Prompt 管理，支持全局开关控制、条件激活、优先级管理和层级化的 Prompt 组织。

## 术语表

- **System**: 动态模块加载器系统
- **Config_File**: `.kiro/config.yaml` 顶层配置文件
- **Module_Config**: `.kiro/modules/{module}/{version}/config.yaml` 模块配置文件
- **Module**: 功能模块（如 workflow、ai-dev、git-commit 等）
- **Steering_File**: 模块的 Steering 规则文件（`.md` 格式）
- **Priority**: 模块优先级（数值越大优先级越高）
- **Global_Switch**: 顶层全局开关（在 Config_File 中的 `enabled` 字段）
- **Module_Condition**: 模块内部的自定义开启条件（在 Module_Config 中）
- **Activation_State**: 模块的最终激活状态（需同时满足：Global_Switch 开启 + Module_Condition 匹配）
- **Enabled_Module**: Global_Switch 为 `true` 的模块
- **Activated_Module**: Activation_State 为激活的模块（同时满足全局开关和条件）
- **Module_Path**: 模块的文件系统路径（`.kiro/modules/{module}/{version}/`）
- **Loading_Order**: 模块加载顺序（按优先级从高到低）
- **Directory_Match**: 按当前工作目录匹配的开启条件
- **File_Type_Match**: 按文件类型匹配的开启条件
- **Prompt_Hierarchy**: Prompt 层级结构（L0: main.md → L1: 加载器逻辑 → L2: 模块 Steering）
- **Current_Context**: 当前活跃需求的上下文信息（用于 Git 提交等场景）

## 需求

### 需求 1：读取顶层模块配置

**用户故事**：作为 Kiro AI，我需要读取顶层配置文件中的模块信息，以便知道哪些模块的全局开关是开启的。

#### 验收标准

1. WHEN System 启动时，THE System SHALL 读取 Config_File（`.kiro/config.yaml`）的内容
2. WHEN 读取 Config_File 时，THE System SHALL 提取所有 Module 的配置信息（enabled、version、priority）
3. IF Config_File 不存在或格式错误，THEN THE System SHALL 输出错误信息并使用默认配置（空模块列表）
4. THE System SHALL 验证每个 Module 配置包含必需字段（enabled、version、priority）
5. THE System SHALL 定义默认配置为：无启用模块、空模块列表

### 需求 2：顶层全局开关管理

**用户故事**：作为项目维护者，我需要在顶层配置中一键开启/关闭每个模块，以便快速控制 Kiro 的功能组合。

#### 验收标准

1. THE System SHALL 在 Config_File 中为每个 Module 配置 `enabled` 字段作为 Global_Switch
2. WHEN Module 的 `enabled: false` 时，THE System SHALL 直接跳过该模块，不进行任何后续处理
3. WHEN Module 的 `enabled: true` 时，THE System SHALL 继续检查该模块的 Module_Condition
4. THE System SHALL 在加载日志中明确标注每个 Module 的 Global_Switch 状态

### 需求 3：读取模块自定义条件配置

**用户故事**：作为 Kiro AI，我需要读取模块内部的自定义开启条件配置，以便判断模块是否应该在当前场景下激活。

#### 验收标准

1. WHEN Module 的 Global_Switch 为 `true` 时，THE System SHALL 读取该模块的 Module_Config（`.kiro/modules/{module}/{version}/config.yaml`）
2. THE System SHALL 提取 Module_Config 中的 `activation_conditions` 字段
3. IF Module_Config 不存在或 `activation_conditions` 字段缺失，THEN THE System SHALL 使用默认条件（`always: true`）
4. THE System SHALL 支持以下内置条件类型：`directory_match`、`file_type_match`、`always`

### 需求 4：子模块自定义条件激活

**用户故事**：作为项目维护者，我需要在模块内部配置自定义开启规则（如按目录匹配），以便模块只在特定场景下激活。

#### 验收标准

1. THE System SHALL 支持在 Module_Config 中配置 `activation_conditions` 字段
2. THE System SHALL 支持以下内置条件类型：
   - `directory_match`: 按当前工作目录路径匹配（支持通配符 `*`）
   - `file_type_match`: 按当前打开的文件类型匹配（如 `.py`、`.md`）
   - `always`: 始终激活（无条件）
3. WHEN Module 配置了多个条件时，THE System SHALL 支持 AND/OR 逻辑组合
4. THE System SHALL 在加载日志中明确标注每个 Module 的条件匹配结果
5. IF Module 未配置 `activation_conditions`，THEN THE System SHALL 默认使用 `always: true` 条件

### 需求 5：计算模块激活状态

**用户故事**：作为 Kiro AI，我需要计算每个模块的最终激活状态，以便只加载应该激活的模块。

#### 验收标准

1. WHEN 读取 Module 的 Global_Switch 和 Module_Condition 后，THE System SHALL 计算 Activation_State
2. THE System SHALL 定义 Activation_State 的计算规则：`Activation_State = Global_Switch AND Module_Condition`
3. WHEN Activation_State 为 `false` 时，THE System SHALL 跳过该模块的加载
4. WHEN Activation_State 为 `true` 时，THE System SHALL 将该模块标记为 Activated_Module
5. THE System SHALL 输出所有 Activated_Module 的列表

### 需求 6：按优先级排序激活的模块

**用户故事**：作为 Kiro AI，我需要按优先级顺序加载激活的模块，以便高优先级模块的规则能够优先生效。

#### 验收标准

1. WHEN 获得 Activated_Module 列表后，THE System SHALL 按 Priority 从高到低排序
2. IF 两个 Module 的 Priority 相同，THEN THE System SHALL 按模块名称字母顺序排序
3. THE System SHALL 输出排序后的 Loading_Order

### 需求 7：构建模块 Steering 文件路径

**用户故事**：作为 Kiro AI，我需要知道每个激活模块的 Steering 文件位置，以便加载正确的规则文件。

#### 验收标准

1. WHEN 处理每个 Activated_Module 时，THE System SHALL 构建 Steering_File 的完整路径
2. THE System SHALL 使用路径模板：`.kiro/modules/{module}/{version}/steering/{module}.md`
3. WHERE Module 名称为 "workflow"，THE System SHALL 使用特殊文件名 `workflow_selector.md`
4. THE System SHALL 验证构建的路径格式正确

### 需求 8：加载模块 Steering 文件

**用户故事**：作为 Kiro AI，我需要按顺序加载每个激活模块的 Steering 规则，以便应用这些规则。

#### 验收标准

1. WHEN 按 Loading_Order 处理每个 Activated_Module 时，THE System SHALL 读取对应的 Steering_File 内容
2. IF Steering_File 不存在，THEN THE System SHALL 输出警告信息并跳过该模块
3. IF Steering_File 读取失败，THEN THE System SHALL 输出错误信息并继续处理下一个模块
4. WHEN 成功加载 Steering_File 时，THE System SHALL 输出加载成功的日志（包含模块名、版本、优先级、激活条件）

### 需求 9：输出加载日志

**用户故事**：作为项目维护者，我需要看到清晰的模块加载日志，以便了解哪些模块被激活以及加载顺序。

#### 验收标准

1. WHEN System 开始加载模块时，THE System SHALL 输出加载开始的标题信息
2. WHEN 处理每个 Module 时，THE System SHALL 输出该模块的详细信息（名称、版本、优先级、全局开关状态、条件匹配结果、激活状态）
3. WHEN 所有模块加载完成后，THE System SHALL 输出加载完成的摘要信息（总共激活的模块数量、跳过的模块数量）
4. THE System SHALL 使用清晰的格式化输出（如表格或列表）

### 需求 10：处理模块冲突

**用户故事**：作为 Kiro AI，我需要知道如何处理多个模块规则冲突的情况，以便正确应用规则。

#### 验收标准

1. WHEN 多个 Activated_Module 的规则冲突时，THE System SHALL 应用 Priority 更高的模块规则
2. IF 两个 Activated_Module 的 Priority 相同且规则冲突，THEN THE System SHALL 应用字母顺序靠前的模块规则
3. THE System SHALL 在加载日志中说明冲突处理机制

### 需求 11：支持模块版本管理

**用户故事**：作为项目维护者，我需要能够切换模块的版本，以便使用不同版本的功能。

#### 验收标准

1. WHEN 读取 Module 配置时，THE System SHALL 提取 `version` 字段
2. WHEN 构建 Module_Path 时，THE System SHALL 使用配置中指定的 `version`
3. THE System SHALL 在加载日志中显示每个模块的版本信息
4. THE System SHALL 支持同一模块的多个版本共存（通过不同的 `version` 值）

### 需求 12：Workflow 模块的双版本管理

**用户故事**：作为项目维护者，我需要为 Workflow 模块管理"简单"和"复杂"两个版本，以便在不同场景下使用不同的工作流。

#### 验收标准

1. THE System SHALL 支持 Workflow 模块的两个独立版本：`v1.0-simple` 和 `v1.0-complex`
2. WHEN 配置 Workflow 模块时，THE System SHALL 允许通过 `version` 字段选择版本（`v1.0-simple` 或 `v1.0-complex`）
3. THE System SHALL 为每个版本维护独立的目录结构：
   - `.kiro/modules/workflow/v1.0-simple/`
   - `.kiro/modules/workflow/v1.0-complex/`
4. THE System SHALL 确保两个版本可以独立配置、独立激活
5. THE System SHALL 在加载日志中明确标注 Workflow 模块使用的版本

### 需求 13：错误处理和容错

**用户故事**：作为 Kiro AI，我需要优雅地处理各种错误情况，以便系统能够继续运行。

#### 验收标准

1. IF Config_File 不存在，THEN THE System SHALL 输出错误信息并使用空的模块列表
2. IF Config_File 格式错误，THEN THE System SHALL 输出错误详情并尝试使用默认配置
3. IF Module 配置缺少必需字段，THEN THE System SHALL 输出警告并跳过该模块
4. IF Module_Config 不存在或格式错误，THEN THE System SHALL 使用默认条件（`always: true`）
5. IF Steering_File 不存在或无法读取，THEN THE System SHALL 输出警告并继续处理其他模块
6. THE System SHALL 确保至少一个错误不会导致整个加载过程失败

### 需求 14：Prompt 格式输出

**用户故事**：作为 Kiro AI，我需要以 Prompt 格式输出加载的 Steering 规则，以便能够理解和应用这些规则。

#### 验收标准

1. WHEN 加载 Steering_File 后，THE System SHALL 将内容以 Markdown 格式输出
2. THE System SHALL 保持 Steering_File 的原始格式和结构
3. THE System SHALL 在每个 Steering_File 内容前添加模块标识注释，格式为：`<!-- Module: {module_name} | Version: {version} | Priority: {priority} | Activated: {activation_conditions} -->`
4. THE System SHALL 确保输出的 Prompt 格式符合 Kiro 的 Steering 规范

### 需求 15：顶层与子 Prompt 的层级联系

**用户故事**：作为 Kiro AI，我需要明确顶层 Prompt 与子 Prompt 的层级关系，以便正确应用所有激活的规则。

#### 验收标准

1. THE System SHALL 定义明确的 Prompt_Hierarchy：
   - L0: 顶层入口 Prompt（`.kiro/steering/main.md`）
   - L1: 动态模块加载器逻辑（嵌入在 main.md 中）
   - L2: 激活的模块 Steering 规则（按优先级加载）
2. THE System SHALL 确保层级优先级：L0 > L1 > L2（高优先级规则可覆盖低优先级）
3. WHEN 所有 Activated_Module 的 Steering 规则加载完成后，THE System SHALL 将它们整合为一个完整的 Prompt 上下文
4. THE System SHALL 在整合后的 Prompt 开头明确标注 Prompt_Hierarchy 和 Activated_Module 列表

### 需求 16：与顶层入口 main.md 的集成

**用户故事**：作为项目维护者，我需要了解动态加载器如何与 main.md 集成，以便正确使用该功能。

#### 验收标准

1. THE System SHALL 将动态加载逻辑嵌入到 `.kiro/steering/main.md` 文件中
2. WHEN Kiro AI 读取 main.md 时，THE System SHALL 自动执行模块加载流程
3. THE System SHALL 在 main.md 中包含加载逻辑的 Prompt 指令（描述如何读取配置、筛选模块、计算激活状态、加载 Steering）
4. THE System SHALL 确保 main.md 既是文档又是可执行的 Prompt
5. THE System SHALL 在 main.md 中说明加载器的工作原理和使用方法

### 需求 17：当前活跃需求上下文管理

**用户故事**：作为 Kiro AI，我需要知道当前正在处理的需求上下文，以便在 Git 提交等场景下使用正确的需求信息。

#### 验收标准

1. THE System SHALL 在项目根目录或 `.kiro/` 下维护一个 `current_context.yaml` 文件
2. THE System SHALL 在 `current_context.yaml` 中记录当前活跃需求的信息（需求路径、需求主题、版本号）
3. WHEN VibCoding 工作流开始处理某个需求时，THE System SHALL 自动将该需求的信息写入 `current_context.yaml`
4. WHEN Git 提交时，THE System SHALL 优先读取 `current_context.yaml` 来确定当前提交关联的需求
5. IF `current_context.yaml` 不存在，THEN THE System SHALL 提示用户选择/输入当前关联的需求

### 需求 18：Git 提交范围边界约定

**用户故事**：作为项目维护者，我需要明确 Git 提交规范的适用范围，以便避免在历史提交上浪费精力。

#### 验收标准

1. THE System SHALL 定义 Git 提交规范的范围边界：仅保证新提交的规范性和可追溯性
2. THE System SHALL 明确约定：2026-03-03 之前的所有历史 Git 提交不做任何处理、不进行追溯改造
3. THE System SHALL 在相关文档中明确标注此范围边界
4. THE System SHALL 确保 Git 提交模块不会尝试处理历史提交

### 需求 19：VibCoding 工作流增强

**用户故事**：作为项目维护者，我需要增强 VibCoding 工作流以支持新的模块化架构，以便能够自动创建标准化的模块结构。

#### 验收标准

1. THE System SHALL 修改 VibCoding 工作流以支持自动创建新的模块化目录结构
2. THE System SHALL 支持自动生成标准化的 `meta.yaml` 文件
3. THE System SHALL 支持与 Git 提交模块的联动（自动更新 `current_context.yaml`）
4. THE System SHALL 在 VibCoding 工作流文档中说明为什么需要这些修改

### 需求 20：业内最佳实践参照

**用户故事**：作为项目维护者，我需要了解模块化架构设计参照了哪些业内最佳实践，以便理解设计决策。

#### 验收标准

1. THE System SHALL 在设计文档中说明模块化结构参考了哪些业内标准（如 LangChain Hub、Kubernetes CRD 等）
2. THE System SHALL 在设计文档中说明元信息（meta.yaml）设计参考了哪些最佳实践
3. THE System SHALL 在设计文档中说明版本管理策略参考了哪些标准（如语义化版本 2.0.0）
4. THE System SHALL 提供相关参考资料的链接或引用

### 需求 21：文件迁移验证

**用户故事**：作为项目维护者，我需要验证文件迁移是否正确完成，以便确保新架构的完整性。

#### 验收标准

1. WHEN 文件迁移完成后，THE System SHALL 生成迁移前后的目录结构对比报告
2. THE System SHALL 验证所有关键配置文件（config.yaml、meta.yaml）的完整性
3. THE System SHALL 验证所有 Steering 文件的内容完整性
4. THE System SHALL 生成《文件迁移完成报告》文档
5. THE System SHALL 在报告中列出所有迁移的文件、新创建的文件、删除的文件

### 需求 22：后续新增 Prompt 需求的标准流程

**用户故事**：作为项目维护者，我需要了解后续新增 Prompt 需求的完整操作流程，以便按照标准流程管理新需求。

#### 验收标准

1. THE System SHALL 在文档中提供《后续新增 Prompt 需求操作指南》
2. THE System SHALL 说明标准流程包含以下步骤：
   - 在 VibCoding 中选择"新建需求"，选择/输入模块名、版本号、需求主题
   - 工作流自动创建 `requirements/{module}/{version}/` 目录结构和 `meta.yaml`
   - 在 `requirement.md` 中编写详细需求
   - 完成需求开发后，工作流自动更新 `meta.yaml` 的 `status: 已完成`
   - （可选）触发 Git 提交，自动生成规范的提交信息
   - （如为新模块）将实现代码/Steering 文件放入 `.kiro/modules/{module}/{version}/`
3. THE System SHALL 确保此流程与 VibCoding 工作流、Git 提交模块、动态加载器无缝集成
