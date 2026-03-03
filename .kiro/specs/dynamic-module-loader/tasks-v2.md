# 实现计划：动态模块加载器（v2.0 - 重构版）

## 概述

本实现计划是对原 v1.0 版本的全量重构，解决了以下核心问题：
1. 任务执行顺序逻辑倒置（上下文管理应在主加载器之前）
2. 核心属性测试被标记为可选（现改为必选）
3. 缺少统一的环境初始化和文件修改备份机制
4. 缺少路径规范校验和数据格式兼容性验证

## 重要说明

- **必选任务**：标记为 `[ ]` 的任务必须完成
- **可选任务**：标记为 `[ ]*` 的任务是边缘场景测试，可根据时间安排选择性完成
- **核心属性测试**：所有验证正确性属性的测试均为必选，确保核心逻辑正确性

---

## 阶段 0：环境初始化与规范校验（新增）

- [ ] 0. 环境初始化与目录规范校验
  - [ ] 0.1 创建项目目录结构
    - 创建 `.kiro/specs/dynamic-module-loader/src/` 源代码目录
    - 创建 `.kiro/specs/dynamic-module-loader/tests/` 测试目录
    - 创建 `.kiro/specs/dynamic-module-loader/test-configs/` 测试配置目录
    - _需求：需求 1, 11_
  
  - [ ] 0.2 设置 Python 虚拟环境
    - 创建虚拟环境
    - 安装依赖包（PyYAML、pytest、hypothesis）
    - 创建 requirements.txt
    - _需求：需求 1_
  
  - [ ] 0.3 创建目录规范校验工具
    - 创建 `src/path_validator.py` 模块
    - 实现 `validate_project_structure()` 函数
    - 验证 `.kiro/` 目录结构符合规范
    - 验证 `requirements/` 目录结构符合规范
    - _需求：需求 1, 17, 21_
  
  - [ ] 0.4 创建文件备份与回滚机制
    - 创建 `src/backup_manager.py` 模块
    - 实现 `backup_file()` 函数（备份单个文件）
    - 实现 `backup_directory()` 函数（备份整个目录）
    - 实现 `rollback()` 函数（回滚到备份）
    - 实现 `cleanup_backups()` 函数（清理旧备份）
    - _需求：隐含需求（数据安全）_
  
  - [ ] 0.5 编写环境初始化测试
    - 测试目录结构创建
    - 测试备份机制的正确性
    - 测试回滚机制的正确性
    - _需求：需求 21_
  
  - [ ] 0.6 定义输出格式规范（新增）
    - 创建 `output-format-spec.md` 文档
    - 定义 current_context.yaml 的标准输出格式
    - 定义模块配置的标准输出格式
    - 定义 Steering 加载结果的标准格式
    - 提供格式示例和字段说明
    - _需求：需求 17, 18, 19_
  
  - [ ] 0.7 创建输出格式校验工具（新增）
    - 创建 `src/output_validator.py` 模块
    - 实现 `validate_context_output()` 函数（校验 current_context.yaml 格式）
    - 实现 `validate_module_config_output()` 函数（校验模块配置格式）
    - 实现 `validate_steering_output()` 函数（校验 Steering 加载结果）
    - 实现 `generate_validation_report()` 函数（生成校验报告）
    - _需求：需求 17, 18, 19_
  
  - [ ] 0.8 编写输出格式校验测试
    - 测试各种格式校验函数
    - 测试校验报告生成
    - 测试错误检测能力
    - _需求：需求 17, 18, 19_

---

## 阶段 1：核心组件实现（配置读取 → 激活计算 → 依赖校验 → 排序）

- [ ] 1. 实现配置读取器（Config Reader）
  - [ ] 1.1 实现基础配置文件读取功能
    - 创建 `src/config_reader.py` 模块
    - 实现 `read_config()` 函数（读取 YAML 文件）
    - 实现基础错误处理（文件不存在、格式错误）
    - _需求：需求 1.1, 1.2, 1.3_
  
  - [ ] 1.2 实现版本号校验功能
    - 实现 `validate_semver()` 函数
    - 支持 SemVer 2.0.0 规范（MAJOR.MINOR.PATCH[-prerelease][+build]）
    - 在配置读取时自动校验版本号
    - _需求：需求 11, 12_
  
  - [ ] 1.3 编写配置读取器的单元测试
    - 测试正常配置文件读取
    - 测试文件不存在的情况
    - 测试 YAML 格式错误的情况
    - _需求：需求 1.3_
  
  - [ ] 1.4 编写版本号校验的属性测试（必选）
    - **属性 13：版本号格式校验正确性**
    - **验证需求：需求 11, 12**
    - 生成随机版本号，验证校验逻辑
    - 最少 100 次迭代
  
  - [ ] 1.5 编写配置解析的属性测试（必选）
    - **属性 1：配置文件解析正确性**
    - **验证需求：需求 1.1, 1.2, 3.1, 3.2, 11.1**
    - 生成随机配置文件，验证解析结果
    - 最少 100 次迭代

- [ ] 2. 实现激活状态计算器（Activation Calculator）
  - [ ] 2.1 实现基础激活状态计算
    - 创建 `src/activation_calculator.py` 模块
    - 实现 `calculate_activation()` 函数
    - 实现全局开关过滤逻辑
    - _需求：需求 2.2, 2.3, 5.1_
  
  - [ ] 2.2 实现条件评估逻辑
    - 实现 `evaluate_condition()` 递归函数
    - 支持 `always` 条件
    - 支持 `directory_match` 条件
    - 支持 `file_type_match` 条件
    - _需求：需求 3.1, 3.2, 4.2_
  
  - [ ] 2.3 实现 AND/OR 逻辑组合
    - 支持 `and` 逻辑（所有子条件满足）
    - 支持 `or` 逻辑（任一子条件满足）
    - 支持嵌套逻辑组合
    - _需求：需求 4.3_
  
  - [ ] 2.4 实现路径匹配逻辑
    - 创建 `src/path_matcher.py` 模块
    - 实现 `match_directory()` 函数（支持通配符）
    - 实现 `match_file_type()` 函数
    - _需求：需求 3.1, 3.2_
  
  - [ ] 2.5 编写激活状态计算的单元测试
    - 测试全局开关过滤
    - 测试各种条件类型
    - 测试 AND/OR 逻辑
    - _需求：需求 2.2, 4.3, 5.1_
  
  - [ ] 2.6 编写路径匹配逻辑的专项测试（必选）
    - 测试 directory_match 的各种模式
    - 测试 file_type_match 的各种扩展名
    - 测试通配符匹配的正确性
    - _需求：需求 3.1, 3.2_
  
  - [ ] 2.7 编写激活状态计算的属性测试（必选）
    - **属性 2：全局开关过滤正确性**
    - **验证需求：需求 2.2**
    - **属性 3：激活状态计算正确性**
    - **验证需求：需求 2.3, 5.1, 5.3, 5.4**
    - **属性 4：条件逻辑组合正确性**
    - **验证需求：需求 4.3**
    - 最少 100 次迭代

- [ ] 3. 实现依赖校验器（Dependency Validator）
  - [ ] 3.1 实现依赖关系校验
    - 创建 `src/dependency_validator.py` 模块
    - 实现 `validate_dependencies()` 函数
    - 检查所有依赖模块是否在激活列表中
    - _需求：隐含需求（模块依赖关系校验）_
  
  - [ ] 3.2 实现循环依赖检测
    - 实现 `detect_circular_dependencies()` 函数
    - 使用 DFS 算法检测依赖图中的环
    - 返回所有涉及循环的模块
    - _需求：隐含需求（模块依赖关系校验）_
  
  - [ ] 3.3 编写依赖校验的单元测试
    - 测试正常依赖关系
    - 测试缺失依赖
    - 测试循环依赖
    - _需求：隐含需求_
  
  - [ ] 3.4 编写依赖校验的属性测试（必选）
    - **属性 14：依赖关系校验正确性**
    - **验证需求：隐含需求**
    - **属性 15：循环依赖检测正确性**
    - **验证需求：隐含需求**
    - 最少 100 次迭代

- [ ] 4. 实现优先级排序器（Priority Sorter）
  - [ ] 4.1 实现优先级排序功能
    - 创建 `src/priority_sorter.py` 模块
    - 实现 `sort_by_priority()` 函数
    - 按优先级从高到低排序
    - 优先级相同时按名称字母顺序排序
    - _需求：需求 6.1, 6.2_
  
  - [ ] 4.2 编写优先级排序的属性测试（必选）
    - **属性 5：优先级排序正确性**
    - **验证需求：需求 6.1, 6.2**
    - 生成随机模块列表，验证排序结果
    - 最少 100 次迭代

- [ ] 5. Checkpoint - 确保核心组件测试通过
  - 确保所有必选测试通过
  - 确保所有属性测试至少运行 100 次迭代
  - 如有问题请向用户提问

---

## 阶段 2：上下文管理与 Steering 加载

- [ ] 6. 实现当前上下文管理器（Current Context Manager）
  - [ ] 6.1 实现上下文读写功能
    - 创建 `src/context_manager.py` 模块
    - 实现 `read_context()` 函数
    - 实现 `write_context()` 函数
    - 实现 `update_context()` 函数
    - _需求：需求 17.1, 17.2, 17.3, 17.4_
  
  - [ ] 6.2 实现上下文格式校验
    - 实现 `validate_context_format()` 函数
    - 验证嵌套结构（active_requirement + environment + updated_at）
    - 验证必需字段完整性
    - _需求：需求 17.1, 17.2_
  
  - [ ] 6.3 编写上下文管理的单元测试
    - 测试正常读写操作
    - 测试格式校验逻辑
    - 测试错误处理
    - _需求：需求 17.1, 17.2, 17.3, 17.4_
  
  - [ ] 6.4 编写上下文管理的属性测试（必选）
    - **属性 11：当前上下文一致性（Round-trip）**
    - **验证需求：需求 17.1, 17.2, 17.3, 17.4**
    - 验证写入后读取的内容一致
    - 最少 100 次迭代

- [ ] 7. 实现 Steering 加载器（Steering Loader）
  - [ ] 7.1 实现路径构建功能
    - 创建 `src/steering_loader.py` 模块
    - 实现路径构建逻辑
    - 处理 workflow 模块的特殊文件名
    - _需求：需求 7.1, 7.3_
  
  - [ ] 7.2 实现 Steering 文件加载
    - 实现 `load_steering()` 函数
    - 读取 Steering 文件内容
    - 添加模块标识注释
    - 处理文件不存在和读取失败的情况
    - _需求：需求 8.1, 8.2, 8.3, 14.3_
  
  - [ ] 7.3 编写 Steering 加载的单元测试
    - 测试正常文件加载
    - 测试 workflow 特殊路径
    - 测试文件不存在
    - 测试文件读取失败
    - _需求：需求 7.1, 8.1, 8.2, 8.3_
  
  - [ ] 7.4 编写 Steering 加载的属性测试（必选）
    - **属性 6：路径构建正确性**
    - **验证需求：需求 7.1, 11.2**
    - **属性 7：Steering 加载顺序正确性**
    - **验证需求：需求 8.1**
    - **属性 8：Steering 内容完整性**
    - **验证需求：需求 14.1, 14.2, 14.3**
    - 最少 100 次迭代

- [ ] 8. 实现 Prompt 整合器（Prompt Integrator）
  - [ ] 8.1 实现 Prompt 整合功能
    - 创建 `src/prompt_integrator.py` 模块
    - 实现 `integrate_prompts()` 函数
    - 添加层级结构说明
    - 添加激活模块列表
    - 按优先级顺序拼接 Steering 内容
    - _需求：需求 15.3_
  
  - [ ] 8.2 编写 Prompt 整合的属性测试（必选）
    - **属性 9：Prompt 整合完整性**
    - **验证需求：需求 15.3**
    - 验证整合结果包含所有模块内容
    - 最少 100 次迭代

- [ ] 9. 实现日志输出器（Logger）
  - [ ] 9.1 实现日志输出功能
    - 创建 `src/logger.py` 模块
    - 实现 `log_info()`, `log_warning()`, `log_error()` 函数
    - 实现 `log_module_status()` 函数
    - 使用清晰的日志格式
    - _需求：需求 9.1, 9.2, 9.3, 9.4_

- [ ] 10. Checkpoint - 确保上下文和加载组件正常工作
  - 确保所有必选测试通过
  - 确保上下文格式与下游模块兼容
  - 如有问题请向用户提问

---

## 阶段 3：主加载器整合与配置冲突处理

- [ ] 11. 实现配置冲突合并规则（新增）
  - [ ] 11.1 创建配置合并器
    - 创建 `src/config_merger.py` 模块
    - 实现 `merge_configs()` 函数
    - 定义模块配置与顶层配置的优先级规则
    - _需求：隐含需求（配置冲突处理）_
  
  - [ ] 11.2 编写配置合并的单元测试
    - 测试顶层配置优先
    - 测试模块配置覆盖
    - 测试嵌套配置合并
    - _需求：隐含需求_

- [ ] 12. 实现主加载器逻辑（Main Loader）
  - [ ] 12.1 创建主加载器模块
    - 创建 `src/dynamic_loader.py` 模块
    - 实现 `DynamicLoader` 类
    - 整合所有组件（配置读取、激活计算、依赖校验、排序、加载、整合）
    - _需求：需求 1-15_
  
  - [ ] 12.2 实现完整的加载流程
    - 读取顶层配置
    - 筛选启用的模块
    - 读取模块配置
    - 合并配置（处理冲突）
    - 计算激活状态
    - 校验依赖关系
    - 按优先级排序
    - 加载 Steering 文件
    - 整合 Prompt 上下文
    - 输出加载日志
    - _需求：需求 1-15_
  
  - [ ] 12.3 编写主加载器的集成测试
    - 测试完整的加载流程
    - 测试各种配置组合
    - 测试错误处理
    - _需求：需求 1-15_

- [ ] 13. Checkpoint - 确保主加载器正常工作
  - 确保所有集成测试通过
  - 确保加载流程符合设计规范
  - 如有问题请向用户提问

---

## 阶段 4：main.md 入口与测试套件

- [ ] 14. 更新 main.md 嵌入加载逻辑
  - [ ] 14.1 编写 Prompt 指令
    - 在 `.kiro/steering/main.md` 中添加动态加载器说明
    - 使用自然语言描述加载流程
    - 提供配置文件示例
    - 提供预期日志输出示例
    - _需求：需求 16.1, 16.2, 16.3, 16.4, 16.5_
  
  - [ ] 14.2 添加使用指南
    - 说明如何启用/禁用模块
    - 说明如何配置激活条件
    - 说明如何管理模块依赖
    - 说明如何切换模块版本
    - _需求：需求 16.5_
  
  - [ ] 14.3 添加 Prompt 逻辑与 Python 代码的联动测试（新增）
    - 创建 `tests/prompt_execution_test.py` 测试脚本
    - 实现测试场景 1：验证 main.md 中的加载流程能否正确调用 `dynamic_loader.py`
    - 实现测试场景 2：验证 main.md 中的配置读取逻辑能否正确调用 `config_reader.py`
    - 实现测试场景 3：验证 main.md 中的错误处理逻辑能否正确调用错误处理函数
    - 实现 `simulate_prompt_execution()` 函数（模拟 Prompt 指令执行）
    - 实现 `verify_python_call()` 函数（验证 Python 函数被正确调用）
    - 实现 `check_output_consistency()` 函数（验证输出与预期一致）
    - 编写测试报告生成逻辑
    - _需求：需求 16.1, 16.2_

- [ ] 15. 创建 Workflow 模块双版本支持
  - [ ] 15.1 创建 v1.0-simple 版本目录
    - 创建 `.kiro/modules/workflow/v1.0-simple/` 目录
    - 复制现有 workflow 模块内容
    - 更新 `meta.yaml` 版本信息
    - _需求：需求 12_
  
  - [ ] 15.2 创建 v1.0-complex 版本目录
    - 创建 `.kiro/modules/workflow/v1.0-complex/` 目录
    - 复制现有 workflow 模块内容
    - 更新 `meta.yaml` 版本信息
    - _需求：需求 12_
  
  - [ ]* 15.3 编写 Workflow 版本独立性测试（可选）
    - **属性 10：Workflow 版本独立性**
    - **验证需求：需求 12.2, 12.4**
    - 验证两个版本互不影响

- [ ] 16. 创建测试配置文件套件
  - [ ] 16.1 创建基础测试配置
    - 创建 `test-configs/test-config-basic.yaml`（基本加载）
    - 创建 `test-configs/test-config-filter.yaml`（全局开关过滤）
    - 创建 `test-configs/test-config-priority.yaml`（优先级排序）
    - _需求：需求 1-6_
  
  - [ ] 16.2 创建错误处理测试配置
    - 创建 `test-configs/test-config-error.yaml`（缺少字段）
    - 创建 `test-configs/test-config-version.yaml`（版本号校验）
    - _需求：需求 11, 13_
  
  - [ ] 16.3 创建依赖测试配置
    - 创建 `test-configs/test-config-dependency.yaml`（依赖缺失）
    - 创建 `test-configs/test-config-circular.yaml`（循环依赖）
    - _需求：隐含需求_
  
  - [ ] 16.4 创建条件激活测试配置
    - 创建 `test-configs/test-config-and-condition.yaml`（AND 逻辑）
    - 创建 `test-configs/test-config-or-condition.yaml`（OR 逻辑）
    - 创建对应的模块配置文件
    - _需求：需求 4_

- [ ] 17. Checkpoint - 确保所有功能完整实现
  - 确保所有必选测试通过
  - 确保测试配置文件覆盖所有场景
  - 如有问题请向用户提问

---

## 阶段 5：文档编写与最终验证

- [ ] 18. 创建文档和使用指南
  - [ ] 18.1 创建 README.md
    - 项目简介
    - 安装说明
    - 快速开始
    - 配置说明
    - _需求：需求 16, 20_
  
  - [ ] 18.2 创建测试计划文档
    - 创建 `test-plan.md`
    - 列出所有测试场景
    - 记录预期结果
    - 提供测试执行指南
    - _需求：需求 21_
  
  - [ ] 18.3 创建系统集成文档
    - 说明与 Workflow 模块的集成
    - 说明与 Git 提交模块的集成
    - 说明与 VibCoding 工作流的集成
    - 提供数据传递格式示例
    - 明确数据格式兼容性要求
    - _需求：需求 17, 18, 19_
  
  - [ ] 18.4 创建数据格式规范文档（新增）
    - 定义 current_context.yaml 的标准格式
    - 定义模块配置的标准格式
    - 提供格式校验工具
    - _需求：需求 17, 18, 19_

- [ ] 19. 运行完整测试套件
  - [ ] 19.1 运行所有单元测试
    - 执行 `pytest tests/unit/`
    - 确保所有单元测试通过
  
  - [ ] 19.2 运行所有属性测试（必选）
    - 执行 `pytest tests/property/`
    - 确保所有属性测试通过（每个至少 100 次迭代）
    - 验证所有 15 个正确性属性
  
  - [ ] 19.3 运行集成测试
    - 执行 `pytest tests/integration/`
    - 测试完整的加载流程
    - 测试与其他模块的集成
  
  - [ ] 19.4 运行上下游兼容性测试（新增）
    - 验证 current_context.yaml 格式与 Git 提交模块兼容
    - 验证 current_context.yaml 格式与 VibCoding 工作流兼容
    - 验证模块配置格式与下游模块兼容
    - _需求：需求 17, 18, 19_

- [ ] 20. 最终检查点 - 确保所有测试通过
  - 确保所有必选测试通过
  - 确保所有属性测试至少运行 100 次迭代
  - 确保数据格式与下游模块完全兼容
  - 向用户报告完成情况

---

## 重构说明

### 主要改进

1. **新增阶段 0**：环境初始化与规范校验
   - 统一的目录结构创建
   - 文件备份与回滚机制
   - 目录规范校验工具

2. **任务顺序调整**：
   - 上下文管理（任务 6）移到主加载器（任务 12）之前
   - Workflow 双版本支持（任务 15）移到测试配置（任务 16）之前

3. **核心属性测试改为必选**：
   - 所有验证正确性属性的测试（属性 1-15）均为必选
   - 仅边缘场景测试（如 Workflow 版本独立性）保留可选标记

4. **新增功能**：
   - 配置冲突合并规则（任务 11）
   - Prompt 逻辑与 Python 代码的联动测试（任务 14.3）
   - 路径匹配逻辑的专项测试（任务 2.6）
   - 上下游兼容性测试（任务 19.4）
   - 数据格式规范文档（任务 18.4）

5. **需求追溯完善**：
   - 所有任务都明确标注对应的需求编号
   - 隐含需求（依赖校验、配置冲突）显式化

### 测试策略

- **必选测试**：所有核心正确性属性测试（15 个）
- **可选测试**：边缘场景测试（如 Workflow 版本独立性）
- **属性测试迭代次数**：最少 100 次
- **测试标记格式**：`Feature: dynamic-module-loader, Property {number}: {property_text}`

### 依赖包

项目需要以下 Python 包：
- `PyYAML`: YAML 文件解析
- `pytest`: 单元测试框架
- `hypothesis`: 基于属性的测试框架
- `pytest-cov`: 测试覆盖率报告

安装命令：
```bash
pip install PyYAML pytest hypothesis pytest-cov
```

### 目录结构

```
.kiro/specs/dynamic-module-loader/
├── requirements.md          # 需求文档
├── design.md               # 设计文档
├── tasks.md                # 原版本（v1.0）
├── tasks-v2.md             # 本文件（v2.0 重构版）
├── test-plan.md            # 测试计划（待创建）
├── data-format-spec.md     # 数据格式规范（待创建）
├── src/                    # 源代码目录
│   ├── config_reader.py
│   ├── activation_calculator.py
│   ├── dependency_validator.py
│   ├── priority_sorter.py
│   ├── steering_loader.py
│   ├── prompt_integrator.py
│   ├── logger.py
│   ├── context_manager.py
│   ├── path_validator.py       # 新增
│   ├── backup_manager.py       # 新增
│   ├── config_merger.py        # 新增
│   └── dynamic_loader.py
├── tests/                  # 测试目录
│   ├── unit/              # 单元测试
│   ├── property/          # 属性测试
│   └── integration/       # 集成测试
└── test-configs/          # 测试配置文件
    ├── test-config-basic.yaml
    ├── test-config-filter.yaml
    └── ...
```

---

**计划版本**: v2.0  
**创建日期**: 2026-03-03  
**状态**: ✅ 待执行
