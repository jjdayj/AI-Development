# 新对话启动提示词 - 动态模块加载器项目

## 📋 项目背景

我正在开发 Kiro AI Prompt 基座项目的**动态模块加载器**模块。这是一个核心功能，负责根据配置文件动态加载和管理 Prompt 模块。

## 🎯 当前进度

### ✅ 已完成的阶段

**Phase 1: 核心组件实现** - 100% 完成
- ✅ Task 1: 配置读取器（27 个测试通过）
- ✅ Task 2: 激活状态计算器（47 个测试通过）
- ✅ Task 3: 依赖校验器（26 个测试通过）
- ✅ Task 4: 优先级排序器（27 个测试通过）

**Phase 2: 上下文管理与 Steering 加载** - 100% 完成
- ✅ Task 6: 当前上下文管理器（32 个测试通过）
- ✅ Task 7: Steering 加载器（26 个测试通过）
- ✅ Task 8: Prompt 整合器（36 个测试通过）
- ✅ Task 9: 日志输出器（37 个测试通过）
- ✅ Task 10: Checkpoint（310 个测试全部通过）

**Phase 3: 主加载器整合与配置冲突处理** - 33% 完成
- ✅ Task 11: 配置冲突合并规则（34 个测试通过）
- ⏳ Task 12: 主加载器逻辑（待开始）
- ⏳ Task 13: Checkpoint（待开始）

### 📊 总体统计

```
总测试数: 344 个单元测试
通过率: 100%
代码文件: 12 个
测试文件: 12 个
完成进度: Phase 1 (100%) + Phase 2 (100%) + Phase 3 (33%) = 约 78%
```

## 📍 下一步任务

**Task 12: 实现主加载器逻辑**

根据 `tasks-v2.md` 的要求，需要：

### Task 12.1: 创建主加载器模块
- 创建 `src/dynamic_loader.py` 模块
- 实现 `DynamicLoader` 类
- 整合所有组件（配置读取、激活计算、依赖校验、排序、加载、整合）

### Task 12.2: 实现完整的加载流程
1. 读取顶层配置
2. 筛选启用的模块
3. 读取模块配置
4. 合并配置（处理冲突）
5. 计算激活状态
6. 校验依赖关系
7. 按优先级排序
8. 加载 Steering 文件
9. 整合 Prompt 上下文
10. 输出加载日志

### Task 12.3: 编写主加载器的集成测试
- 测试完整的加载流程
- 测试各种配置组合
- 测试错误处理

## 📁 关键文件路径

### 工作目录
```
.kiro/specs/dynamic-module-loader/
```

### 任务文档
- `tasks-v2.md` - 任务清单（当前执行的版本）
- `requirements.md` - 需求文档
- `design.md` - 设计文档

### 已完成的源代码
```
src/
├── config_reader.py          # 配置读取器
├── activation_calculator.py  # 激活状态计算器
├── dependency_validator.py   # 依赖校验器
├── priority_sorter.py        # 优先级排序器
├── path_matcher.py           # 路径匹配器
├── context_manager.py        # 上下文管理器
├── steering_loader.py        # Steering 加载器
├── prompt_integrator.py      # Prompt 整合器
├── logger.py                 # 日志输出器
├── config_merger.py          # 配置合并器
├── backup_manager.py         # 备份管理器
└── path_validator.py         # 路径校验器
```

### 测试目录
```
tests/
├── unit/                     # 单元测试（12 个文件）
├── property/                 # 属性测试
└── integration/              # 集成测试（待创建）
```

## 🔧 开发环境

- **Python 版本**: 3.13.12
- **测试框架**: pytest 9.0.2
- **属性测试**: hypothesis 6.151.9
- **虚拟环境**: `.kiro/specs/dynamic-module-loader/venv/`

### 运行测试命令
```bash
cd .kiro/specs/dynamic-module-loader
python -m pytest tests/unit/ -v
```

## 📝 开发规范

1. **严格按照任务清单执行**：每次只执行一个小任务
2. **编写完整的单元测试**：每个功能都要有测试覆盖
3. **使用 pytest 运行测试**：确保所有测试通过
4. **添加详细的文档字符串**：包含需求追溯
5. **保持代码质量**：清晰的命名、模块化设计、错误处理

## 🎯 请求

继续执行 **Task 12.1**：创建主加载器模块，实现 `DynamicLoader` 类。

请按照以下步骤：
1. 查看 `design.md` 中关于主加载器的设计说明
2. 创建 `src/dynamic_loader.py` 文件
3. 实现 `DynamicLoader` 类，整合所有已完成的组件
4. 实现完整的加载流程（10 个步骤）
5. 编写详细的文档字符串和需求追溯

## 📚 参考文档

- 任务清单: `.kiro/specs/dynamic-module-loader/tasks-v2.md`
- 设计文档: `.kiro/specs/dynamic-module-loader/design.md`
- 需求文档: `.kiro/specs/dynamic-module-loader/requirements.md`
- 完成报告: 
  - `CHECKPOINT-PHASE2-REPORT.md`
  - `TASK-11-COMPLETION-REPORT.md`

---

**提示词版本**: v1.0  
**创建日期**: 2026-03-03  
**当前任务**: Task 12.1 - 创建主加载器模块  
**状态**: 准备开始
