# 实现计划：动态模块加载器

## 概述

本实现计划将动态模块加载器的设计转化为可执行的编码任务。实现将使用 Python 语言，并采用模块化、测试驱动的开发方式。

## 任务列表

- [ ] 1. 项目初始化和基础设施
  - 创建项目目录结构
  - 设置 Python 虚拟环境
  - 安装依赖包（PyYAML、pytest、hypothesis）
  - 创建基础配置文件
  - _需求：需求 1, 11_

- [ ] 2. 实现配置读取器（Config Reader）
  - [ ] 2.1 实现基础配置文件读取功能
    - 创建 `config_reader.py` 模块
    - 实现 `read_config()` 函数（读取 YAML 文件）
    - 实现基础错误处理（文件不存在、格式错误）
    - _需求：需求 1.1, 1.2, 1.3_
  
  - [ ]* 2.2 编写配置读取器的单元测试
    - 测试正常配置文件读取
    - 测试文件不存在的情况
    - 测试 YAML 格式错误的情况
    - _需求：需求 1.3_
  
  - [ ] 2.3 实现版本号校验功能
    - 实现 `validate_semver()` 函数
    - 支持 SemVer 2.0.0 规范（MAJOR.MINOR.PATCH[-prerelease][+build]）
    - 在配置读取时自动校验版本号
    - _需求：需求 11, 12_
  
  - [ ]* 2.4 编写版本号校验的属性测试
    - **属性 13：版本号格式校验正确性**
    - **验证需求：需求 11, 12**
    - 生成随机版本号，验证校验逻辑
  
  - [ ]* 2.5 编写配置解析的属性测试
    - **属性 1：配置文件解析正确性**
    - **验证需求：需求 1.1, 1.2, 3.1, 3.2, 11.1**
    - 生成随机配置文件，验证解析结果

- [ ] 3. 实现激活状态计算器（Activation Calculator）
  - [ ] 3.1 实现基础激活状态计算
    - 创建 `activation_calculator.py` 模块
    - 实现 `calculate_activation()` 函数
    - 实现全局开关过滤逻辑
    - _需求：需求 2.2, 2.3, 5.1_
  
  - [ ] 3.2 实现条件评估逻辑
    - 实现 `evaluate_condition()` 递归函数
    - 支持 `always` 条件
    - 支持 `directory_match` 条件
    - 支持 `file_type_match` 条件
    - _需求：需求 3.1, 3.2, 4.2_
  
  - [ ] 3.3 实现 AND/OR 逻辑组合
    - 支持 `and` 逻辑（所有子条件满足）
    - 支持 `or` 逻辑（任一子条件满足）
    - 支持嵌套逻辑组合
    - _需求：需求 4.3_
  
  - [ ]* 3.4 编写激活状态计算的单元测试
    - 测试全局开关过滤
    - 测试各种条件类型
    - 测试 AND/OR 逻辑
    - _需求：需求 2.2, 4.3, 5.1_
  
  - [ ]* 3.5 编写激活状态计算的属性测试
    - **属性 2：全局开关过滤正确性**
    - **验证需求：需求 2.2**
    - **属性 3：激活状态计算正确性**
    - **验证需求：需求 2.3, 5.1, 5.3, 5.4**
    - **属性 4：条件逻辑组合正确性**
    - **验证需求：需求 4.3**

- [ ] 4. 检查点 - 确保配置读取和激活计算正常工作
  - 确保所有测试通过，如有问题请向用户提问

- [ ] 5. 实现依赖校验器（Dependency Validator）
  - [ ] 5.1 实现依赖关系校验
    - 创建 `dependency_validator.py` 模块
    - 实现 `validate_dependencies()` 函数
    - 检查所有依赖模块是否在激活列表中
    - _需求：隐含需求（模块依赖关系校验）_
  
  - [ ] 5.2 实现循环依赖检测
    - 实现 `detect_circular_dependencies()` 函数
    - 使用 DFS 算法检测依赖图中的环
    - 返回所有涉及循环的模块
    - _需求：隐含需求（模块依赖关系校验）_
  
  - [ ]* 5.3 编写依赖校验的单元测试
    - 测试正常依赖关系
    - 测试缺失依赖
    - 测试循环依赖
    - _需求：隐含需求_
  
  - [ ]* 5.4 编写依赖校验的属性测试
    - **属性 14：依赖关系校验正确性**
    - **验证需求：隐含需求**
    - **属性 15：循环依赖检测正确性**
    - **验证需求：隐含需求**

- [ ] 6. 实现优先级排序器（Priority Sorter）
  - [ ] 6.1 实现优先级排序功能
    - 创建 `priority_sorter.py` 模块
    - 实现 `sort_by_priority()` 函数
    - 按优先级从高到低排序
    - 优先级相同时按名称字母顺序排序
    - _需求：需求 6.1, 6.2_
  
  - [ ]* 6.2 编写优先级排序的属性测试
    - **属性 5：优先级排序正确性**
    - **验证需求：需求 6.1, 6.2**
    - 生成随机模块列表，验证排序结果

- [ ] 7. 实现 Steering 加载器（Steering Loader）
  - [ ] 7.1 实现路径构建功能
    - 创建 `steering_loader.py` 模块
    - 实现路径构建逻辑
    - 处理 workflow 模块的特殊文件名
    - _需求：需求 7.1, 7.3_
  
  - [ ] 7.2 实现 Steering 文件加载
    - 实现 `load_steering()` 函数
    - 读取 Steering 文件内容
    - 添加模块标识注释
    - 处理文件不存在和读取失败的情况
    - _需求：需求 8.1, 8.2, 8.3, 14.3_
  
  - [ ]* 7.3 编写 Steering 加载的单元测试
    - 测试正常文件加载
    - 测试 workflow 特殊路径
    - 测试文件不存在
    - 测试文件读取失败
    - _需求：需求 7.1, 8.1, 8.2, 8.3_
  
  - [ ]* 7.4 编写 Steering 加载的属性测试
    - **属性 6：路径构建正确性**
    - **验证需求：需求 7.1, 11.2**
    - **属性 7：Steering 加载顺序正确性**
    - **验证需求：需求 8.1**
    - **属性 8：Steering 内容完整性**
    - **验证需求：需求 14.1, 14.2, 14.3**

- [ ] 8. 实现 Prompt 整合器（Prompt Integrator）
  - [ ] 8.1 实现 Prompt 整合功能
    - 创建 `prompt_integrator.py` 模块
    - 实现 `integrate_prompts()` 函数
    - 添加层级结构说明
    - 添加激活模块列表
    - 按优先级顺序拼接 Steering 内容
    - _需求：需求 15.3_
  
  - [ ]* 8.2 编写 Prompt 整合的属性测试
    - **属性 9：Prompt 整合完整性**
    - **验证需求：需求 15.3**
    - 验证整合结果包含所有模块内容

- [ ] 9. 实现日志输出器（Logger）
  - [ ] 9.1 实现日志输出功能
    - 创建 `logger.py` 模块
    - 实现 `log_info()`, `log_warning()`, `log_error()` 函数
    - 实现 `log_module_status()` 函数
    - 使用清晰的日志格式
    - _需求：需求 9.1, 9.2, 9.3, 9.4_

- [ ] 10. 检查点 - 确保所有核心组件正常工作
  - 确保所有测试通过，如有问题请向用户提问

- [ ] 11. 实现主加载器逻辑（Main Loader）
  - [ ] 11.1 创建主加载器模块
    - 创建 `dynamic_loader.py` 模块
    - 实现 `DynamicLoader` 类
    - 整合所有组件（配置读取、激活计算、依赖校验、排序、加载、整合）
    - _需求：需求 1-15_
  
  - [ ] 11.2 实现完整的加载流程
    - 读取顶层配置
    - 筛选启用的模块
    - 读取模块配置
    - 计算激活状态
    - 校验依赖关系
    - 按优先级排序
    - 加载 Steering 文件
    - 整合 Prompt 上下文
    - 输出加载日志
    - _需求：需求 1-15_
  
  - [ ]* 11.3 编写主加载器的集成测试
    - 测试完整的加载流程
    - 测试各种配置组合
    - 测试错误处理
    - _需求：需求 1-15_

- [ ] 12. 实现当前上下文管理（Current Context Manager）
  - [ ] 12.1 实现上下文读写功能
    - 创建 `context_manager.py` 模块
    - 实现 `read_context()` 函数
    - 实现 `write_context()` 函数
    - 实现 `update_context()` 函数
    - _需求：需求 17.1, 17.2, 17.3, 17.4_
  
  - [ ]* 12.2 编写上下文管理的属性测试
    - **属性 11：当前上下文一致性**
    - **验证需求：需求 17.1, 17.2, 17.3, 17.4**
    - 验证写入后读取的内容一致（round-trip）

- [ ] 13. 更新 main.md 嵌入加载逻辑
  - [ ] 13.1 编写 Prompt 指令
    - 在 `.kiro/steering/main.md` 中添加动态加载器说明
    - 使用自然语言描述加载流程
    - 提供配置文件示例
    - 提供预期日志输出示例
    - _需求：需求 16.1, 16.2, 16.3, 16.4, 16.5_
  
  - [ ] 13.2 添加使用指南
    - 说明如何启用/禁用模块
    - 说明如何配置激活条件
    - 说明如何管理模块依赖
    - 说明如何切换模块版本
    - _需求：需求 16.5_

- [ ] 14. 创建测试配置文件套件
  - [ ] 14.1 创建基础测试配置
    - 创建 `test-config-basic.yaml`（基本加载）
    - 创建 `test-config-filter.yaml`（全局开关过滤）
    - 创建 `test-config-priority.yaml`（优先级排序）
    - _需求：需求 1-6_
  
  - [ ] 14.2 创建错误处理测试配置
    - 创建 `test-config-error.yaml`（缺少字段）
    - 创建 `test-config-version.yaml`（版本号校验）
    - _需求：需求 11, 13_
  
  - [ ] 14.3 创建依赖测试配置
    - 创建 `test-config-dependency.yaml`（依赖缺失）
    - 创建 `test-config-circular.yaml`（循环依赖）
    - _需求：隐含需求_
  
  - [ ] 14.4 创建条件激活测试配置
    - 创建 `test-config-and-condition.yaml`（AND 逻辑）
    - 创建 `test-config-or-condition.yaml`（OR 逻辑）
    - 创建对应的模块配置文件
    - _需求：需求 4_

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
  
  - [ ]* 15.3 编写 Workflow 版本独立性测试
    - **属性 10：Workflow 版本独立性**
    - **验证需求：需求 12.2, 12.4**
    - 验证两个版本互不影响

- [ ] 16. 检查点 - 确保所有功能完整实现
  - 确保所有测试通过，如有问题请向用户提问

- [ ] 17. 创建文档和使用指南
  - [ ] 17.1 创建 README.md
    - 项目简介
    - 安装说明
    - 快速开始
    - 配置说明
    - _需求：需求 16, 20_
  
  - [ ] 17.2 创建测试计划文档
    - 创建 `test-plan.md`
    - 列出所有测试场景
    - 记录预期结果
    - 提供测试执行指南
    - _需求：需求 21_
  
  - [ ] 17.3 创建系统集成文档
    - 说明与 Workflow 模块的集成
    - 说明与 Git 提交模块的集成
    - 说明与 VibCoding 工作流的集成
    - 提供数据传递格式示例
    - _需求：需求 17, 18, 19_

- [ ] 18. 运行完整测试套件
  - [ ] 18.1 运行所有单元测试
    - 执行 `pytest tests/unit/`
    - 确保所有单元测试通过
  
  - [ ] 18.2 运行所有属性测试
    - 执行 `pytest tests/property/`
    - 确保所有属性测试通过（每个至少 100 次迭代）
  
  - [ ] 18.3 运行集成测试
    - 执行 `pytest tests/integration/`
    - 测试完整的加载流程
    - 测试与其他模块的集成

- [ ] 19. 最终检查点 - 确保所有测试通过
  - 确保所有测试通过，如有问题请向用户提问

## 注意事项

### 测试标记

所有属性测试必须使用以下标记格式：
```python
@pytest.mark.property
@pytest.mark.parametrize("iterations", [100])
def test_property_X():
    """
    Feature: dynamic-module-loader
    Property X: [属性描述]
    Validates: Requirements X.Y
    """
    # 测试代码
```

### 可选任务说明

标记为 `*` 的任务是可选的测试任务。这些任务对于确保系统正确性非常重要，但如果时间紧迫，可以先跳过，专注于核心实现。

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
├── tasks.md                # 本文件
├── test-plan.md            # 测试计划（待创建）
├── src/                    # 源代码目录
│   ├── config_reader.py
│   ├── activation_calculator.py
│   ├── dependency_validator.py
│   ├── priority_sorter.py
│   ├── steering_loader.py
│   ├── prompt_integrator.py
│   ├── logger.py
│   ├── context_manager.py
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

**计划版本**: v1.0  
**创建日期**: 2026-03-03  
**状态**: ✅ 待执行
