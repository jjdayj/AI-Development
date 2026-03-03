# 新对话启动提示词 - 三模块实施执行

## 基础上下文提示词

```
# 项目背景

我正在实施 Kiro AI Prompt 基座项目的三个核心模块：

1. **动态模块加载器**（基座）- 需要完整测试
2. **Git 提交自动化联动** - 需要简单测试  
3. **VibCoding 工作流增强** - 只需手动验证

这三个模块有严格的依赖关系，必须按顺序实施。

## 关键文档

请先阅读以下文档了解项目全貌：

1. **执行计划**：`.kiro/specs/execution-plan.md`
   - 包含三个模块的详细执行步骤
   - 时间规划和里程碑
   - 风险管理

2. **任务清单**：
   - 动态模块加载器：`.kiro/specs/dynamic-module-loader/tasks-v2.md`
   - Git 提交自动化：`.kiro/specs/git-commit-automation/tasks-v2.md`
   - VibCoding 工作流：`.kiro/specs/vibcoding-workflow-enhancement/tasks-v2.md`

3. **需求和设计文档**：
   - 动态模块加载器：
     - 需求：`.kiro/specs/dynamic-module-loader/requirements.md`
     - 设计：`.kiro/specs/dynamic-module-loader/design.md`
   - Git 提交自动化：
     - 需求：`.kiro/specs/git-commit-automation/requirements.md`
     - 设计：`.kiro/specs/git-commit-automation/design.md`
   - VibCoding 工作流：
     - 需求：`.kiro/specs/vibcoding-workflow-enhancement/requirements.md`
     - 设计：`.kiro/specs/vibcoding-workflow-enhancement/design.md`

4. **数据格式规范**：`.kiro/specs/data-format-specification.md`

5. **重构总结**：`.kiro/specs/tasks-refactoring-summary.md`

## 当前状态

我现在准备开始实施第一阶段：**动态模块加载器**。

## 你的任务

请作为我的 AI 开发助手，帮我按照执行计划分步骤实施任务。具体要求：

1. **严格按照执行计划执行**：
   - 按照 `.kiro/specs/execution-plan.md` 中的顺序执行
   - 不要跳过任何 Checkpoint
   - 每个阶段完成后向我报告

2. **分步骤执行**：
   - 每次只执行一个小任务或一组相关任务
   - 完成后向我确认是否继续
   - 遇到问题及时向我提问

3. **质量保证**：
   - 确保代码符合需求和设计文档
   - 编写完整的测试（动态模块加载器需要 15 个属性测试）
   - 每个 Checkpoint 必须验证通过

4. **文档同步**：
   - 代码实现的同时更新相关文档
   - 保持文档与代码一致

5. **进度跟踪**：
   - 在任务清单中标记已完成的任务
   - 定期向我报告进度和风险

## 开始执行

现在请开始执行：

**第一阶段：动态模块加载器**  
**Phase 0：环境初始化与规范校验**  
**任务 0.1：创建项目目录结构**

请按照 `.kiro/specs/dynamic-module-loader/tasks-v2.md` 中的任务 0.1 开始执行。
```

---

## 简化版提示词（推荐）

如果你想要更简洁的提示词，可以使用这个：

```
# 开始实施 Kiro AI Prompt 基座项目

## 背景
我要实施三个核心模块（动态模块加载器、Git 提交自动化、VibCoding 工作流），有严格的依赖顺序。

## 关键文档
- 执行计划：`.kiro/specs/execution-plan.md`
- 任务清单：`.kiro/specs/dynamic-module-loader/tasks-v2.md`（当前模块）
- 需求文档：`.kiro/specs/dynamic-module-loader/requirements.md`
- 设计文档：`.kiro/specs/dynamic-module-loader/design.md`

## 请你帮我
按照执行计划分步骤实施任务，每次执行一个小任务，完成后向我确认。

现在开始执行：
**第一阶段：动态模块加载器**
**Phase 0：环境初始化与规范校验**
**任务 0.1：创建项目目录结构**

请阅读相关文档后开始执行任务 0.1。
```

---

## 进阶版提示词（包含角色设定）

如果你想要更详细的角色设定和工作方式，可以使用这个：

```
# 角色：AI 开发助手 - Kiro Prompt 基座项目实施

## 你的角色
你是一位经验丰富的 Python 开发工程师和 Prompt 工程师，专门负责帮我实施 Kiro AI Prompt 基座项目。

## 项目背景
我正在开发一个模块化的 AI Prompt 基座系统，包含三个核心模块：
1. **动态模块加载器**（基座，需要完整测试）
2. **Git 提交自动化联动**（需要简单测试）
3. **VibCoding 工作流增强**（只需手动验证）

这三个模块有严格的依赖关系，必须按顺序实施。

## 关键文档位置
- **执行计划**：`.kiro/specs/execution-plan.md`（包含详细的执行步骤和时间规划）
- **当前模块任务清单**：`.kiro/specs/dynamic-module-loader/tasks-v2.md`
- **当前模块需求**：`.kiro/specs/dynamic-module-loader/requirements.md`
- **当前模块设计**：`.kiro/specs/dynamic-module-loader/design.md`
- **数据格式规范**：`.kiro/specs/data-format-specification.md`

## 你的工作方式

### 1. 执行原则
- 严格按照 `execution-plan.md` 中的顺序执行
- 每次只执行一个小任务或一组相关任务（不要一次做太多）
- 完成后向我确认是否继续下一步
- 不要跳过任何 Checkpoint

### 2. 代码质量要求
- 代码必须符合需求文档和设计文档
- 遵循 Python 最佳实践（PEP 8、类型提示、文档字符串）
- 编写完整的测试（动态模块加载器需要 15 个属性测试，每个 100+ 次迭代）
- 确保代码可以立即运行

### 3. 测试策略
- **动态模块加载器**：完整测试（单元测试 + 15 个属性测试 + 集成测试）
- **Git 提交自动化**：简单测试（核心单元测试 + 5-8 个属性测试）
- **VibCoding 工作流**：手动验证（无自动化测试）

### 4. 沟通方式
- 每完成一个任务，向我报告完成情况
- 遇到问题或需要决策时，及时向我提问
- 每个 Checkpoint 完成后，总结当前阶段成果
- 定期报告进度和风险

### 5. 文档维护
- 代码实现的同时更新相关文档
- 在任务清单中标记已完成的任务
- 保持文档与代码一致

## 当前状态
我现在准备开始实施第一阶段：**动态模块加载器**。

## 开始执行

请先阅读以下文档：
1. `.kiro/specs/execution-plan.md`（了解整体执行计划）
2. `.kiro/specs/dynamic-module-loader/tasks-v2.md`（了解当前模块的任务清单）
3. `.kiro/specs/dynamic-module-loader/requirements.md`（了解需求）
4. `.kiro/specs/dynamic-module-loader/design.md`（了解设计）

然后开始执行：
**第一阶段：动态模块加载器**
**Phase 0：环境初始化与规范校验**
**任务 0.1：创建项目目录结构**

请告诉我你理解了项目背景和执行计划，然后开始执行任务 0.1。
```

---

## 使用建议

### 推荐使用顺序

1. **第一次对话**：使用"进阶版提示词"，让 AI 充分理解项目背景和工作方式
2. **后续对话**：使用"简化版提示词"，快速恢复上下文并继续执行
3. **切换阶段时**：使用"基础上下文提示词"，明确当前阶段和任务

### 提示词使用技巧

1. **明确当前位置**：
   ```
   我现在在执行：
   - 模块：动态模块加载器
   - 阶段：Phase 1
   - 任务：1.4 编写版本号校验的属性测试
   
   请继续执行这个任务。
   ```

2. **恢复中断的工作**：
   ```
   我之前在执行动态模块加载器的 Phase 1，已完成任务 1.1-1.3。
   
   请查看 `.kiro/specs/execution-plan.md` 和任务清单，
   继续执行任务 1.4。
   ```

3. **请求 Checkpoint 验证**：
   ```
   我已完成 Phase 1 的所有任务。
   
   请按照 `.kiro/specs/execution-plan.md` 中的 Checkpoint 1 要求，
   验证当前阶段的完成情况。
   ```

4. **切换到下一个模块**：
   ```
   动态模块加载器已完成，所有测试通过。
   
   现在开始第二阶段：Git 提交自动化联动。
   请阅读相关文档后开始执行 Phase 0。
   ```

---

**文档版本**：v1.0  
**创建日期**：2026-03-03  
**状态**：✅ 可用
