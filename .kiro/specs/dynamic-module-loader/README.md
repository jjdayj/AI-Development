# 动态模块加载器

## 项目简介

动态模块加载器是 Kiro Prompt 基座的核心功能，负责在 AI 启动时根据配置文件动态加载启用的模块 Steering 规则。

## 目录结构

```
.kiro/specs/dynamic-module-loader/
├── README.md              # 本文件
├── requirements.md        # 需求文档
├── design.md             # 设计文档
├── tasks-v2.md           # 实施计划（v2.0 重构版）
├── requirements.txt      # Python 依赖包
├── src/                  # 源代码目录
│   ├── config_reader.py
│   ├── activation_calculator.py
│   ├── dependency_validator.py
│   ├── priority_sorter.py
│   ├── steering_loader.py
│   ├── prompt_integrator.py
│   ├── logger.py
│   ├── context_manager.py
│   ├── path_validator.py
│   ├── backup_manager.py
│   ├── config_merger.py
│   ├── output_validator.py
│   └── dynamic_loader.py
├── tests/                # 测试目录
│   ├── unit/            # 单元测试
│   ├── property/        # 属性测试
│   └── integration/     # 集成测试
└── test-configs/        # 测试配置文件
```

## 快速开始

### 1. 设置 Python 虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 激活虚拟环境（Linux/Mac）
source venv/bin/activate

# 安装依赖包
pip install -r requirements.txt
```

### 2. 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行属性测试
pytest tests/property/

# 运行集成测试
pytest tests/integration/

# 生成测试覆盖率报告
pytest --cov=src --cov-report=html
```

## 开发状态

- [x] Phase 0: 环境初始化与规范校验
  - [x] 0.1 创建项目目录结构
  - [x] 0.2 设置 Python 虚拟环境
  - [x] 0.3 创建目录规范校验工具
  - [x] 0.4 创建文件备份与回滚机制
  - [x] 0.5 编写环境初始化测试

- [ ] Phase 1: 核心组件实现
  - [x] 1.1-1.3 实现配置读取器 + 单元测试
  - [x] 1.4 编写版本号校验的属性测试（属性 13）
  - [x] 1.5 编写配置解析的属性测试（属性 1）
  - [ ] 0.3 创建目录规范校验工具
  - [ ] 0.4 创建文件备份与回滚机制
  - [ ] 0.5 编写环境初始化测试
  - [ ] 0.6 定义输出格式规范
  - [ ] 0.7 创建输出格式校验工具
  - [ ] 0.8 编写输出格式校验测试

- [ ] Phase 1: 核心组件实现
- [ ] Phase 2: 上下文管理与 Steering 加载
- [ ] Phase 3: 主加载器整合与配置冲突处理
- [ ] Phase 4: main.md 入口与测试套件
- [ ] Phase 5: 文档编写与最终验证

## 相关文档

- [需求文档](requirements.md)
- [设计文档](design.md)
- [实施计划](tasks-v2.md)
- [执行计划](../../execution-plan.md)

---

**项目版本**: v1.0  
**创建日期**: 2026-03-03  
**状态**: 🚧 开发中
