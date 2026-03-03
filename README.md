# AI Development 智能化项目管理系统

## 项目简介

这是一个基于 Kiro AI 的下一代智能化项目管理系统，采用模块化架构和动态加载技术，提供从需求管理到代码提交的全流程自动化解决方案。系统支持双轨工作流（Prompt 工作流 + 代码工作流），具备智能上下文感知、自动化 Git 提交、模块化配置管理等先进功能。

## 🚀 核心特性

### 🎯 VibeCoding 工作流系统（v2.0 全新）
- **轻量化流程**: 原生开发 4 阶段，二次开发 5 阶段
- **改一点测一点**: 小步快跑，每个最小单元完成后立即测试
- **可选测试和文档**: 根据需求灵活配置，不强制执行
- **支持二次开发**: 评估现有代码，智能改造和复用
- **上下文感知**: 基于 current_context.yaml 维护当前工作状态

### 🔧 模块化架构
- **动态模块加载器**: 支持模块的条件激活、优先级管理、依赖校验
- **模块化配置**: 每个功能模块独立配置，支持版本管理和灵活组合
- **热插拔支持**: 无需重启即可启用/禁用功能模块

### 📝 智能 Git 提交系统
- **自动提交信息生成**: 从需求元信息自动提取提交前缀，生成规范提交信息
- **多层安全检查**: 敏感文件检测、大文件检测、保护分支检测
- **智能推送**: 支持自动推送和错误类型识别

### 🛡️ 安全与可靠性
- **Git 回滚功能**: 支持智能回滚和备份管理
- **安全检查**: 提交前执行全面安全检查，防止敏感信息泄露
- **容错机制**: 优雅处理各种错误情况，提供降级选项

## 快速导航

- **🔧 环境配置**: 查看 `附件：Kiro自动生成项目+git+推送.md` - GitHub Token 配置和环境变量设置
- **📚 模块化配置**: 查看 `.kiro/steering/STEERING_GUIDE.md` - 新架构配置说明
- **⚡ 动态加载器**: 查看 `.kiro/steering/main.md` - 动态模块加载器使用指南
- **🔄 VibeCoding 工作流**: 查看 `kiro/modules/workflow/v2.0/README.md` - 轻量化工作流详细说明
- **📖 完整文档**: 继续阅读本文档下方内容

## 🏗️ 项目架构

### 新架构概览（v2.0）

```
AI Development/
├── .kiro/                          # Kiro 配置目录（模块化架构）
│   ├── config.yaml                 # 顶层配置（全局开关、模块优先级）
│   ├── steering/                   # 顶层 Steering 规则
│   │   ├── main.md                 # 主入口 Prompt（动态加载器）
│   │   └── STEERING_GUIDE.md       # 架构说明文档
│   ├── modules/                    # 功能模块目录
│   │   ├── workflow/v2.0/          # VibeCoding 工作流模块（新版本）
│   │   │   ├── steering/           # 工作流 Steering 规则
│   │   │   ├── config.yaml         # 模块配置
│   │   │   └── README.md           # 模块文档
│   │   ├── ai-dev/v1.0/            # AI 开发自动化模块
│   │   ├── git-commit/v1.0/        # Git 提交自动化模块
│   │   ├── git-rollback/v1.0/      # Git 回滚功能模块
│   │   └── doc-save/v1.0/          # 文档保存模块（可选）
│   ├── templates/                  # 模板文件
│   │   ├── module/                 # 模块模板
│   │   └── requirement/            # 需求文档模板
│   ├── current_context.yaml        # 当前工作上下文
│   └── commit_history.yaml         # 提交历史记录
├── requirements/                   # 需求管理目录
│   └── {module}/{version}/         # 按模块和版本组织的需求
│       ├── meta.yaml               # 需求元信息
│       ├── requirement.md          # 需求文档
│       └── docs/                   # 需求相关文档
├── 00_problem-solve-lib/          # 问题解决项目库
├── 01_actual-project-lib/         # 实际项目库
│   └── automation-tools/          # 自动化工具模块
├── doc/project/                   # 项目文档
│   ├── dynamic-module-loader/     # 动态加载器文档
│   ├── prompt-base-architecture/  # 架构设计文档
│   └── git-commit/                # Git 提交功能文档
├── scripts/                       # 工具脚本
│   └── module_loader.py           # 模块加载器脚本
└── README.md                      # 本文档
```

### 架构升级亮点

#### 🔄 动态模块加载器
- **条件激活**: 模块可根据目录、文件类型等条件自动激活
- **优先级管理**: 支持模块间优先级控制和冲突解决
- **依赖校验**: 自动检测模块依赖关系和循环依赖
- **版本管理**: 支持同一模块的多版本并存（如 workflow v1.0-simple / v1.0-complex）

#### 🎯 VibeCoding 工作流系统（v2.0）
- **原生开发流程**: 4 阶段轻量化流程（了解需求 → 分析需求 → 制定计划 → 落地执行）
- **二次开发流程**: 5 阶段流程（评估代码 → 了解需求 → 分析需求 → 制定计划 → 落地执行）
- **改一点测一点**: 小步快跑，每个最小单元完成后立即测试
- **可选测试和文档**: 根据需求灵活配置，不强制执行
- **主动澄清**: Phase 2 主动提问，澄清所有不确定点
- **支持二次开发**: 评估现有代码的适配性、改造成本、风险

#### 📝 Git 提交自动化联动
- **上下文感知**: 自动从 current_context.yaml 读取当前需求信息
- **智能前缀生成**: 从 meta.yaml 自动提取 git_commit_prefix
- **多层安全检查**: 敏感文件、大文件、保护分支检测
- **智能推送**: 支持错误类型识别和自动重试

#### 🛡️ Git 回滚功能
- **智能回滚**: 支持按提交、文件、时间范围回滚
- **备份管理**: 自动备份和清理机制
- **安全检查**: 回滚前执行安全验证

## 🎮 功能模块详解

### 1. 动态模块加载器 (Dynamic Module Loader)

**核心功能**: 实现模块化的 Prompt 管理系统，支持条件激活和优先级控制

**主要特性**:
- ✅ 读取 `.kiro/config.yaml` 配置，按优先级加载模块
- ✅ 支持模块条件激活（目录匹配、文件类型匹配、逻辑组合）
- ✅ 自动校验模块依赖关系和循环依赖
- ✅ 支持模块版本管理（如 workflow v1.0-simple / v1.0-complex）
- ✅ 输出详细的加载日志和错误处理

**使用示例**:
```yaml
# .kiro/config.yaml
modules:
  workflow:
    enabled: true
    version: v1.0-simple  # 或 v1.0-complex
    priority: 200
  
  ai-dev:
    enabled: true
    version: v1.0
    priority: 100
```

**激活条件示例**:
```yaml
# .kiro/modules/doc-save/v1.0/config.yaml
activation_conditions:
  or:
    - directory_match: ["doc/**/*", ".kiro/steering/*"]
    - file_type_match: [".md"]
```

### 2. VibCoding 工作流增强 (VibCoding Workflow Enhancement)

**核心功能**: 为双轨工作流系统添加完整的模块化需求管理能力

**主要特性**:
- ✅ **前置钩子**: 工作流启动时自动收集需求信息
  - 模块名称验证（kebab-case 格式）
  - 版本号验证（SemVer 2.0.0 格式）
  - 需求主题收集
- ✅ **目录结构自动创建**: 创建 `requirements/{module}/{version}/` 标准目录
- ✅ **元信息自动生成**: 生成 meta.yaml 和 requirement.md 文件
- ✅ **上下文管理**: 维护 current_context.yaml 当前工作状态
- ✅ **后置钩子**: 工作流结束时状态更新和 Git 提交触发
- ✅ **需求切换**: 支持多需求并行开发和进度保存/恢复

**工作流程**:
```
用户启动工作流 → 前置钩子收集信息 → VibCoding Phase 1-5 → 后置钩子处理
```

**生成的文件结构**:
```
requirements/my-module/v1.0/
├── meta.yaml          # 需求元信息（包含 git_commit_prefix）
├── requirement.md     # 需求文档模板
└── docs/             # 需求相关文档目录
```

### 3. Git 提交自动化联动 (Git Commit Automation)

**核心功能**: 实现 Git 提交与需求管理系统的无缝集成

**主要特性**:
- ✅ **上下文感知**: 自动从 current_context.yaml 读取当前需求信息
- ✅ **智能前缀生成**: 从 meta.yaml 自动提取 git_commit_prefix
- ✅ **规范提交信息**: 自动生成 `{prefix}: {description}` 格式的提交信息
- ✅ **多层安全检查**:
  - 敏感文件检测（.env、.key、密码文件等）
  - 大文件检测（可配置警告和阻止阈值）
  - 保护分支检测（main、master、production）
- ✅ **智能推送**: 支持错误类型识别和解决建议
- ✅ **提交历史**: 记录最近 10 次提交信息，支持快速重用

**使用示例**:
```
用户: "提交代码: 实现动态模块加载器"

系统自动执行:
1. 读取 current_context.yaml → 获取当前需求
2. 读取 meta.yaml → 提取 git_commit_prefix
3. 生成提交信息: "feat(dynamic-module-loader-v1.0): 实现动态模块加载器"
4. 执行安全检查 → 检查敏感文件、大文件、保护分支
5. 执行 git commit → 询问是否推送
6. 执行 git push → 记录提交历史
```

### 4. Git 回滚功能 (Git Rollback)

**核心功能**: 提供智能化的 Git 回滚和备份管理

**主要特性**:
- ✅ **多种回滚方式**: 按提交哈希、文件路径、时间范围回滚
- ✅ **智能备份**: 回滚前自动创建备份分支
- ✅ **安全检查**: 回滚前检查工作区状态和冲突
- ✅ **备份管理**: 自动清理过期备份（可配置保留天数）

### 5. AI 开发自动化 (AI Development Automation)

**核心功能**: 保留原有的项目创建和 GitHub 集成功能

**主要特性**:
- ✅ **智能命名转换**: 中文指令转换为 GitHub 规范英文命名
- ✅ **一键项目创建**: 自动创建目录结构和 README 文档
- ✅ **GitHub 集成**: 自动创建远程仓库并推送代码
- ✅ **灵活配置**: 支持全局和单步骤开关控制

### 6. 文档保存模块 (Doc Save) - 可选

**核心功能**: 自动保存会话文档和项目文档

**主要特性**:
- 📝 会话文档自动保存
- 📝 项目文档版本管理
- 📝 文档格式标准化

**状态**: 默认禁用，可通过配置启用
## ⚡ 快速开始

### 1. 环境配置（一次性设置）

#### 步骤 1：确认目录结构
确保你的项目根目录包含 `.kiro/` 文件夹，如果没有请创建：

```bash
# Windows
mkdir .kiro
mkdir .kiro\modules
mkdir .kiro\steering
mkdir .kiro\templates

# macOS/Linux  
mkdir -p .kiro/{modules,steering,templates}
```

#### 步骤 2：配置 GitHub Token
选择以下任一方式配置 GitHub Token：

**方式 A：环境变量（推荐）**
```powershell
# Windows PowerShell
[Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "ghp_your_token_here", "User")
```

**方式 B：.env 文件**
```ini
# .kiro/.env
GITHUB_TOKEN=ghp_your_token_here
GITHUB_USER=your_username
```

#### 步骤 3：安装 Python 依赖（如需使用 AI 开发模块）
```bash
pip install requests gitpython python-dotenv
```

### 2. 基础使用

#### 启动 VibeCoding 工作流
```
# 在 Kiro 中输入
开发新功能
```

系统会询问你选择工作流类型：
- A. 原生功能开发流程（4 阶段，2 小时）
- B. 二次开发流程（5 阶段，3 小时）
- C. 不进入工作流，正常作答

选择后，系统会自动：
1. 收集需求信息（模块名、版本号、主题）
2. 创建标准目录结构
3. 生成元信息文件
4. 按阶段执行开发流程

#### 智能 Git 提交
```
# 在 Kiro 中输入
提交代码: 实现某功能
```

系统会自动：
1. 读取当前需求上下文
2. 生成规范提交信息
3. 执行安全检查
4. 提交并询问是否推送

#### 需求切换
```
# 在 Kiro 中输入
切换需求
```

系统会询问是否保存当前进度，然后切换到新需求。

### 3. 模块配置

#### 启用/禁用模块
编辑 `.kiro/config.yaml`：

```yaml
modules:
  workflow:
    enabled: true      # 启用 VibeCoding 工作流
    version: v2.0
    priority: 200
  
  git-commit:
    enabled: true      # 启用智能 Git 提交
    version: v1.0
    priority: 80
  
  doc-save:
    enabled: false     # 禁用文档保存模块
    version: v1.0
    priority: 90
```

#### 配置模块激活条件
编辑 `kiro/modules/{module}/v1.0/config.yaml`：

```yaml
# 示例：配置测试和文档的默认行为
defaults:
  testing:
    enabled: false  # 默认关闭测试
    ask_user: true  # 每次询问用户
  
  documentation:
    enabled: true   # 默认生成文档
    ask_user: true  # 每次询问用户
```

## 🔧 高级配置

### VibeCoding 工作流配置
系统支持灵活的测试和文档配置：

```yaml
# kiro/modules/workflow/v2.0/config.yaml
defaults:
  testing:
    enabled: false  # 默认关闭测试
    ask_user: true  # 每次询问用户是否需要测试
  
  documentation:
    enabled: true   # 默认生成总结文档
    ask_user: true  # 每次询问用户是否需要文档
```

### Git 提交安全配置
```yaml
# .kiro/modules/git-commit/v1.0/config.yaml
security:
  sensitive_patterns:
    - "*.secret"
    - "**/private/*"
  
  warn_size_mb: 10      # 大文件警告阈值
  block_size_mb: 100    # 大文件阻止阈值
  
  protected_branches:
    - "main"
    - "master"
    - "production"
```

### 模块版本管理
支持同一模块的多版本并存：

```yaml
modules:
  workflow:
    enabled: true
    version: v2.0    # VibeCoding 工作流（轻量化）
    priority: 200
```

## 📊 使用统计

### 使用统计

- ✅ **workflow** (v2.0) - VibeCoding 工作流系统
- ✅ **ai-dev** (v1.0) - AI 开发自动化
- ✅ **git-commit** (v1.0) - Git 提交自动化
- ✅ **git-rollback** (v1.0) - Git 回滚功能
- ❌ **doc-save** (v1.0) - 文档保存模块（已禁用）

### 功能覆盖率
- 🎯 需求管理: 100% 自动化
- 📝 Git 提交: 100% 自动化 + 安全检查
- 🔄 工作流: 双轨自动识别
- 🛡️ 安全检查: 多层防护
- 📚 文档生成: 模板化自动生成

## 🚨 常见问题

### Q: 如何查看当前激活的模块？
A: 查看 Kiro 启动时的日志输出，或检查 `.kiro/config.yaml` 配置。

### Q: 模块加载失败怎么办？
A: 检查模块配置文件格式，确认依赖关系，查看错误日志定位问题。

### Q: 如何自定义提交信息格式？
A: 编辑需求的 `meta.yaml` 文件中的 `git_commit_prefix` 字段。

### Q: 需求切换时进度会丢失吗？
A: 不会，系统会询问是否保存进度，保存的进度可以随时恢复。

### Q: 如何回滚错误的提交？
A: 使用 Git 回滚功能：`回滚到上一次提交` 或 `回滚指定文件`。

## 📖 详细文档

- **VibeCoding 工作流**: `kiro/modules/workflow/v2.0/README.md`
- **动态模块加载器**: `.kiro/specs/dynamic-module-loader/README.md`
- **Git 提交自动化**: `.kiro/specs/git-commit-automation/README.md`
- **架构设计文档**: `doc/project/prompt-base-architecture/`
- **QA 对话记录**: `doc/project/dynamic-module-loader/20260303_QA对话记录/`

---

## 📜 传统 AI Development 功能文档

> 以下是原有 AI Development 功能的完整文档，现已集成到新的模块化架构中

### 核心逻辑拆分（明确各角色职责）
| 角色                | 核心职责                                                                 |
|---------------------|--------------------------------------------------------------------------|

## 三、核心文件编写（关键步骤）
### 步骤1：Python执行脚本（ai-dev-script.py，含开关逻辑+边界处理）
在 `D:\AI Development\.kiro` 文件夹下新建/替换 `ai-dev-script.py` 文件，粘贴以下完整代码（已整合开关配置逻辑+边界情况处理）：

**新增边界情况处理：**
- 参数格式验证（日期、项目名、模块名、版本号）
- 目录重复创建检测
- 模块目录自动创建
- README 覆盖警告
- Git 仓库状态检查
- 暂存区空提交检测
- 远程仓库 URL 冲突处理
- 网络超时和错误分类处理

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Development 自动化管理脚本（最终稳定版，含步骤开关配置）
功能：
1. 读取配置文件（全局+单个步骤开关）；
2. 接收Kiro生成的纯英文参数；
3. 按配置开关一键完成「目录创建+README+Git+自动创库+推送」；
参数要求：所有参数为纯英文，无中文/空格/特殊字符
"""
import os
import sys
import time
import json
import argparse
import subprocess
import requests
from copy import deepcopy
from dotenv import load_dotenv

# ====================== 修复版：加载执行步骤配置文件 ======================
def load_config():
    """加载执行步骤配置文件，含全局开关+单个步骤开关（修复变量作用域+JSON解析）"""
    config_path = os.path.join(os.path.dirname(__file__), "ai-dev-config.json")
    # 先定义默认配置（全局作用域，避免UnboundLocalError）
    default_config = {
        "global_execution": True,
        "execution_steps": {
            "init_project": True,
            "local_git": True,
            "remote_git": True
        },
        "default_branch": "master"
    }
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        # 合并配置（用户配置覆盖默认）
        final_config = deepcopy(default_config)
        if "global_execution" in config:
            final_config["global_execution"] = config["global_execution"]
        if "execution_steps" in config:
            final_config["execution_steps"].update(config["execution_steps"])
        if "default_branch" in config:
            final_config["default_branch"] = config["default_branch"]
        return final_config
    except FileNotFoundError:
        print(f"⚠️  配置文件未找到（{config_path}），使用默认配置执行所有步骤")
        return default_config
    except json.JSONDecodeError:
        print(f"⚠️  配置文件格式错误（JSON不支持//注释/单引号），使用默认配置执行所有步骤")
        return default_config

# ====================== 1. 基础配置（仅改这里） ======================
ROOT_PATH = "D:\\AI Development"
# 加载环境变量（优先系统环境变量，其次.env文件）
load_dotenv()
GITHUB_USER = os.getenv("GITHUB_USER", "jjdayj")  # 默认为jjdayj，可在.env中覆盖
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
SSH_PREFIX = f"git@github.com:{GITHUB_USER}/"
# 加载步骤执行配置（修复后无变量作用域错误）
CONFIG = load_config()

# ====================== 2. 解析命令行参数（纯英文） ======================
def parse_args():
    parser = argparse.ArgumentParser(description="AI Development 自动化执行脚本")
    parser.add_argument("--project-type", required=True, 
                        choices=["problem-solve", "actual-project"], 
                        help="项目类型（纯英文）：problem-solve/actual-project")
    parser.add_argument("--project-name", required=True, 
                        help="项目名称（纯英文，无特殊字符）")
    parser.add_argument("--date", required=True, 
                        help="日期：YYYY-MM-DD")
    parser.add_argument("--status", required=True, 
                        help="状态（纯英文）：completed/incomplete/pending-test")
    parser.add_argument("--module", default="default-module", 
                        help="实际项目模块（纯英文）：automation-tools/ai-script-dev等")
    parser.add_argument("--version", default="v1.0", 
                        help="版本号（如：v1.0）")
    return parser.parse_args()

# ====================== 2.5 参数验证 ======================
def validate_args(args):
    """验证参数格式和合法性"""
    import re
    # 验证日期格式
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', args.date):
        raise Exception(f"日期格式错误：{args.date}，正确格式为 YYYY-MM-DD（如 2026-03-01）")
    
    # 验证项目名称（仅允许字母、数字、短横线）
    if not re.match(r'^[a-z0-9-]+$', args.project_name):
        raise Exception(f"项目名称格式错误：{args.project_name}，仅允许小写字母、数字、短横线")
    
    # 验证模块名称
    if args.module != "default-module" and not re.match(r'^[a-z0-9-]+$', args.module):
        raise Exception(f"模块名称格式错误：{args.module}，仅允许小写字母、数字、短横线")
    
    # 验证版本号格式（可选，但如果提供必须符合规范）
    if args.version and not re.match(r'^v?\d+(\.\d+)*$', args.version):
        raise Exception(f"版本号格式错误：{args.version}，正确格式为 v1.0 或 1.0.0")

# ====================== 3. 生成路径（仅拼接参数，不做转换） ======================
def generate_paths(args):
    # 仅拼接参数，无任何命名转换
    if args.project_type == "actual-project":
        # 实际项目路径：ROOT/01_actual-project-lib/模块/模块-项目名-版本-状态
        local_dir_name = f"{args.module}-{args.project_name}-{args.version}-{args.status}"
        local_full_path = os.path.join(ROOT_PATH, "01_actual-project-lib", args.module, local_dir_name)
        # GitHub仓库名：actual-project-项目名-版本号（去掉v）
        repo_name = f"actual-project-{args.project_name}-{args.version.replace('v','')}"
    else:
        # 问题解决路径：ROOT/00_problem-solve-lib/日期-01-项目名-状态
        local_dir_name = f"{args.date}-01-{args.project_name}-{args.status}"
        local_full_path = os.path.join(ROOT_PATH, "00_problem-solve-lib", local_dir_name)
        repo_name = f"problem-solve-{args.date.replace('-','')}-{args.project_name}"
    
    ssh_url = f"{SSH_PREFIX}{repo_name}.git"
    return local_full_path, repo_name, ssh_url

# ====================== 4. 执行Git命令（兼容Windows） ======================
def run_git_command(cmd, cwd=None):
    try:
        result = subprocess.run(
            cmd, cwd=cwd, shell=True, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8"
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise Exception(f"Git命令执行失败：{e.stderr}")

# ====================== 5. 创建GitHub远端仓库 ======================
def create_github_repo(repo_name):
    if not GITHUB_TOKEN:
        raise Exception("未配置GITHUB_TOKEN！（检查系统环境变量或.env文件）")
    
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "Python/requests"
    }
    data = {
        "name": repo_name,
        "private": False,
        "auto_init": False
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=30)
        response.raise_for_status()
        print(f"✅ 创库成功：{repo_name}")
    except requests.exceptions.Timeout:
        raise Exception("GitHub API 请求超时，请检查网络连接")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            print(f"ℹ️ 仓库已存在，跳过创建：{repo_name}")
        elif e.response.status_code == 401:
            raise Exception("GitHub Token 无效或已过期，请重新配置")
        else:
            raise Exception(f"创库失败：{e.response.text}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求失败：{e}")

# ====================== 6. 主执行流程（含开关判断） ======================
def main():
    args = parse_args()
    try:
        # 0. 参数验证
        validate_args(args)
        
        # 1. 生成路径和仓库名（仅拼接）
        local_full_path, repo_name, ssh_url = generate_paths(args)
        print(f"📌 初始化信息：")
        print(f"   本地路径：{local_full_path}")
        print(f"   仓库名称：{repo_name}")
        print(f"   SSH地址：{ssh_url}")
        print(f"   配置模式：{'全局强制执行' if CONFIG['global_execution'] else '按单个步骤开关执行'}")

        # 2. 创建本地目录（开关判断：全局true OR 单个true → 执行）
        if CONFIG["global_execution"] or CONFIG["execution_steps"]["create_directory"]:
            print(f"\n1/8 创建目录...")
            # 检查目录是否已存在
            if os.path.exists(local_full_path):
                raise Exception(f"项目目录已存在：{local_full_path}\n请检查是否重复创建，或手动删除后重试")
            # 确保父目录存在（实际项目需要模块目录）
            parent_dir = os.path.dirname(local_full_path)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
                print(f"   ✅ 创建模块目录：{parent_dir}")
            os.makedirs(local_full_path, exist_ok=False)
        else:
            print(f"\n1/8 创建目录... [跳过]")
            # 即使跳过创建，也要检查目录是否存在（后续步骤需要）
            if not os.path.exists(local_full_path):
                raise Exception(f"目录不存在且创建步骤已关闭：{local_full_path}\n请开启 create_directory 或手动创建目录")

        # 3. 生成README.md（开关判断）
        if CONFIG["global_execution"] or CONFIG["execution_steps"]["generate_readme"]:
            print(f"2/8 生成README.md...")
            readme_path = os.path.join(local_full_path, "README.md")
            # 检查README是否已存在
            if os.path.exists(readme_path):
                print(f"   ⚠️  README.md 已存在，将被覆盖")
            readme_content = f"""# {args.project_name.replace('-',' ').title()}
- Creation Date: {args.date}
- Status: {args.status.replace('-',' ').title()}
- Project Type: {args.project_type.replace('-',' ').title()}
- Remote Repo: {ssh_url}
"""
            if args.module != "default-module":
                readme_content += f"- Module: {args.module.replace('-',' ').title()}\n"
            if args.version:
                readme_content += f"- Version: {args.version}\n"
            
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
        else:
            print(f"2/8 生成README.md... [跳过]")

        # 4. Git初始化（开关判断）
        if CONFIG["global_execution"] or CONFIG["execution_steps"]["init_git"]:
            print(f"3/8 初始化Git仓库...")
            # 检查是否已经是Git仓库
            git_dir = os.path.join(local_full_path, ".git")
            if os.path.exists(git_dir):
                print(f"   ℹ️  Git仓库已存在，跳过初始化")
            else:
                run_git_command("git init", cwd=local_full_path)
            # 确保Git配置存在（避免提交失败）
            try:
                run_git_command("git config user.name", cwd=local_full_path)
            except:
                run_git_command(f"git config user.name '{GITHUB_USER}'", cwd=local_full_path)
            try:
                run_git_command("git config user.email", cwd=local_full_path)
            except:
                run_git_command(f"git config user.email '{GITHUB_USER}@users.noreply.github.com'", cwd=local_full_path)
        else:
            print(f"3/8 初始化Git仓库... [跳过]")

        # 5. Git添加文件（开关判断）
        if CONFIG["global_execution"] or CONFIG["execution_steps"]["git_add"]:
            print(f"4/8 添加文件到暂存区...")
            run_git_command("git add .", cwd=local_full_path)
        else:
            print(f"4/8 添加文件到暂存区... [跳过]")

        # 6. Git提交（开关判断）
        if CONFIG["global_execution"] or CONFIG["execution_steps"]["git_commit"]:
            print(f"5/8 提交代码...")
            # 检查是否有文件可提交
            try:
                status_output = run_git_command("git status --porcelain", cwd=local_full_path)
                if not status_output.strip():
                    print(f"   ⚠️  暂存区为空，跳过提交")
                else:
                    commit_msg = f"init: {args.project_name} {args.date}"
                    run_git_command(f'git commit -m "{commit_msg}"', cwd=local_full_path)
            except Exception as e:
                # 如果没有初始化Git或没有文件，给出友好提示
                if "not a git repository" in str(e).lower():
                    raise Exception("Git仓库未初始化，请开启 init_git 步骤")
                raise
        else:
            print(f"5/8 提交代码... [跳过]")

        # 7. 创建GitHub仓库（开关判断）
        if CONFIG["global_execution"] or CONFIG["execution_steps"]["create_github_repo"]:
            print(f"6/8 创建远端仓库...")
            create_github_repo(repo_name)
        else:
            print(f"6/8 创建远端仓库... [跳过]")

        # 8. 配置远程仓库（开关判断）
        if CONFIG["global_execution"] or CONFIG["execution_steps"]["config_remote_repo"]:
            print(f"7/8 配置远程仓库...")
            # 检查origin是否已存在
            try:
                existing_origin = run_git_command("git remote get-url origin", cwd=local_full_path).strip()
                if existing_origin != ssh_url:
                    print(f"   ⚠️  origin 已存在但URL不同，将更新为：{ssh_url}")
                    run_git_command("git remote remove origin", cwd=local_full_path)
                    run_git_command(f"git remote add origin {ssh_url}", cwd=local_full_path)
                else:
                    print(f"   ℹ️  origin 已正确配置")
            except Exception:
                # origin不存在，直接添加
                run_git_command(f"git remote add origin {ssh_url}", cwd=local_full_path)
        else:
            print(f"7/8 配置远程仓库... [跳过]")
        
        # 9. 推送代码到GitHub（开关判断+分支兼容）
        if CONFIG["global_execution"] or CONFIG["execution_steps"]["git_push"]:
            print(f"8/8 推送代码到GitHub...")
            retry_count = 0
            max_retries = 2
            while retry_count <= max_retries:
                try:
                    # 先尝试推送到配置的默认分支
                    run_git_command(f"git push -u origin {CONFIG['default_branch']}", cwd=local_full_path)
                    print(f"   ✅ 推送到{CONFIG['default_branch']}分支成功！")
                    break
                except Exception as e1:
                    try:
                        # 若默认分支失败，尝试另一个分支
                        fallback_branch = "main" if CONFIG["default_branch"] == "master" else "master"
                        run_git_command(f"git push -u origin {fallback_branch}", cwd=local_full_path)
                        print(f"   ✅ 推送到{fallback_branch}分支成功！")
                        break
                    except Exception as e2:
                        retry_count += 1
                        if retry_count > max_retries:
                            raise Exception(f"推送失败（重试{max_retries}次）：{e2}")
                        print(f"   ❌ 推送失败，重试第{retry_count}次...")
                        time.sleep(2)
        else:
            print(f"8/8 推送代码到GitHub... [跳过]")

        # 执行完成
        print(f"\n🎉 全流程执行完成！")
        print(f"🔗 本地路径：{local_full_path}")
        print(f"🔗 GitHub仓库：https://github.com/{GITHUB_USER}/{repo_name}")

    except Exception as e:
        print(f"\n❌ 执行失败：{e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 步骤2：Kiro规则文件（ai-dev.md·含参数全说明）
（此文件无变更，保留原有内容，粘贴以下完整代码）
```markdown
---
inclusion: manual
command_description: AI Development自动化管理（含参数全说明）
---

# AI Development命名与命令生成规则V11.0
## 核心角色
你是AI Development命名管理员，需完成：
1. 解析用户中文指令 → 转换为**纯英文标准化参数**（符合GitHub规则：仅字母/数字/短横线，无中文/空格/特殊字符）；
2. 输出「参数说明头 + Python调用命令 + 命令执行说明 + 逐参数解释」，格式严格按示例；
3. 所有参数解释需准确对应脚本接收的参数含义，无遗漏。

## 强制命名映射规则
### 1. 项目类型（--project-type）
- 问题解决 → problem-solve
- 实际项目 → actual-project

### 2. 模块名（--module）
- 自动化工具类 → automation-tools
- AI脚本开发 → ai-script-dev
- 模型部署 → model-deployment
- 数据处理 → data-processing
- 其他 → 核心关键词转英文（短横线分隔，全小写）

### 3. 项目名称（--project-name）
- AI日志分析脚本 → ai-log-analysis-script
- Git权限错误 → git-permission-error
- 数据清洗工具 → data-cleaning-tool
- 其他 → 中文转英文关键词，短横线分隔，全小写

### 4. 状态（--status）
- 完成 → completed
- 未完成 → incomplete
- 待测试 → pending-test
- 开发中 → in-development

### 5. 版本号（--version）
- 保留原格式（如 v1.0 → v1.0），仅移除空格

### 6. 日期（--date）
- 自动补充当前日期，格式：YYYY-MM-DD

## 输出格式（强制严格遵守）
### 输出结构（按顺序）
1. 参数说明头：`根据你的指令，我将生成Python脚本调用命令：`
2. 空行
3. Python调用命令（单行，无代码块包裹）
4. 空行
5. 命令执行说明：`命令执行说明： 此命令将在 01_实际项目库 目录下创建新项目：`
6. 执行说明详情（每行以 `- ` 开头，单独占行）
7. 空行
8. 逐参数解释标题：`以下是调用指令中每个参数的说明：`
9. 逐参数解释列表（每行以 `- ` 开头，单独占行）

### 实际项目输出示例
根据你的指令，我将生成Python脚本调用命令：

python 'D:\AI Development\.kiro\ai-dev-script.py' --project-type "actual-project" --module "automation-tools" --project-name "ai-log-analysis-script" --version "v1.1" --date "2026-03-01" --status "pending-test"

命令执行说明： 此命令将在 01_实际项目库 目录下创建新项目：
- 项目目录：2026-03-01-01-automation-tools-ai-log-analysis-script-v1.1(pending-test)
- 自动初始化Git仓库
- 生成标准README.md模板
- 项目类型：实际项目
- 所属模块：自动化工具类
- 当前状态：待测试

以下是调用指令中每个参数的说明：
- --project-type "actual-project"：项目类型（实际项目）
- --module "automation-tools"：所属模块（自动化工具类）
- --project-name "ai-log-analysis-script"：项目名称（AI日志分析脚本）
- --version "v1.1"：项目版本号（v1.1）
- --date "2026-03-01"：创建日期（2026年03月01日）
- --status "pending-test"：项目状态（待测试）

### 问题解决输出示例
根据你的指令，我将生成Python脚本调用命令：

python 'D:\AI Development\.kiro\ai-dev-script.py' --project-type "problem-solve" --project-name "git-permission-error" --date "2026-03-01" --status "completed"

命令执行说明： 此命令将在 00_问题解决库 目录下创建新项目：
- 项目目录：2026-03-01-01-git-permission-error-completed
- 自动初始化Git仓库
- 生成标准README.md模板
- 项目类型：问题解决
- 所属模块：默认模块
- 当前状态：完成

以下是调用指令中每个参数的说明：
- --project-type "problem-solve"：项目类型（问题解决）
- --project-name "git-permission-error"：项目名称（Git权限错误）
- --date "2026-03-01"：创建日期（2026年03月01日）
- --status "completed"：项目状态（完成）

### 实际项目输出示例
根据你的指令，我将生成Python脚本调用命令：

python 'D:\AI Development\.kiro\ai-dev-script.py' --project-type "actual-project" --module "automation-tools" --project-name "ai-log-analysis-script" --version "v1.0" --date "2026-03-01" --status "pending-test"
命令执行说明： 此命令将在 01_实际项目库 目录下创建新项目：

项目目录：2026-03-01-01-automation-tools-ai-log-analysis-script-v1.0（pending-test）
自动初始化Git仓库
生成标准README.md模板
项目类型：实际项目
所属模块：自动化工具类
当前状态：待测试

以下是调用指令中每个参数的说明：
--project-type "actual-project"：项目类型（实际项目）
--module "automation-tools"：所属模块（自动化工具类）
--project-name "ai-log-analysis-script"：项目名称（AI日志分析脚本）
--version "v1.0"：项目版本号（v1.0）
--date "2026-03-01"：创建日期（2026年03月01日）
--status "pending-test"：项目状态（待测试）

### 问题解决输出示例
根据你的指令，我将生成Python脚本调用命令：

python 'D:\AI Development\.kiro\ai-dev-script.py' --project-type "problem-solve" --project-name "git-permission-error" --date "2026-03-01" --status "completed"
命令执行说明： 此命令将在 00_问题解决库 目录下创建新项目：

项目目录：2026-03-01-01-git-permission-error-completed
自动初始化Git仓库
生成标准README.md模板
项目类型：问题解决
所属模块：默认模块
当前状态：完成

以下是调用指令中每个参数的说明：
--project-type "problem-solve"：项目类型（问题解决）
--project-name "git-permission-error"：项目名称（Git权限错误）
--date "2026-03-01"：创建日期（2026年03月01日）
--status "completed"：项目状态（完成）

## 输出要求
1. 命令部分：脚本路径必须用单引号包裹，参数值用双引号，顺序严格按示例；
2. 执行说明：
   - 实际项目：目录名格式为「日期-01-模块-项目名-版本（状态）」，项目类型/模块/状态对应中文；
   - 问题解决：目录名格式为「日期-01-项目名-状态」，模块默认显示「默认模块」；
3. 逐参数解释：
   - 每个参数单独一行，格式为「参数名 "参数值"：参数含义（中文）」；
   - 实际项目包含所有6个参数，问题解决包含4个参数（无--module/--version）；
4. 禁止删减/新增任何输出内容，格式和示例完全对齐。

## 输入输出示例
### 用户输入
/ai-dev 新建实际项目：自动化工具类，AI 日志分析脚本 v1.0，状态待测试

### 最终输出
根据你的指令，我将生成Python脚本调用命令：

python 'D:\AI Development\.kiro\ai-dev-script.py' --project-type "actual-project" --module "automation-tools" --project-name "ai-log-analysis-script" --version "v1.0" --date "2026-03-01" --status "pending-test"
命令执行说明： 此命令将在 01_实际项目库 目录下创建新项目：

项目目录：2026-03-01-01-automation-tools-ai-log-analysis-script-v1.0（pending-test）
自动初始化Git仓库
生成标准README.md模板
项目类型：实际项目
所属模块：自动化工具类
当前状态：待测试

以下是调用指令中每个参数的说明：
--project-type "actual-project"：项目类型（实际项目）
--module "automation-tools"：所属模块（自动化工具类）
--project-name "ai-log-analysis-script"：项目名称（AI日志分析脚本）
--version "v1.0"：项目版本号（v1.0）
--date "2026-03-01"：创建日期（2026年03月01日）
--status "pending-test"：项目状态（待测试）
```

## 四、日常使用流程（极简四步，新增配置调整）
### 步骤1：调整执行开关配置（可选）
根据需求修改 `D:\AI Development\.kiro\ai-dev-config.json`：
- 需强制执行所有步骤：保持 `global_execution: true`；
- 需跳过特定步骤：设置 `global_execution: false`，并将对应步骤的开关改为 `false`（如 `git_push: false` 跳过推送）。

### 步骤2：发送指令给Kiro
在Kiro聊天框中输入极简指令（格式固定）：
```
/ai-dev 新建实际项目：自动化工具类，AI 日志分析脚本 v1.0，状态待测试
```
👉 指令模板：
- 实际项目：`/ai-dev 新建实际项目：{模块名}，{项目名称} {版本号}，状态{状态}`
- 问题解决：`/ai-dev 新建问题解决流程：{日期} {问题描述}，状态{状态}`

### 步骤3：复制Kiro输出的内容
Kiro会输出「参数说明头 + 调用命令 + 执行说明 + 逐参数解释」完整内容（示例）：
```
根据你的指令，我将生成Python脚本调用命令：

python 'D:\AI Development\.kiro\ai-dev-script.py' --project-type "actual-project" --module "automation-tools" --project-name "ai-log-analysis-script" --version "v1.0" --date "2026-03-01" --status "pending-test"
命令执行说明： 此命令将在 01_实际项目库 目录下创建新项目：

项目目录：2026-03-01-01-automation-tools-ai-log-analysis-script-v1.0（pending-test）
自动初始化Git仓库
生成标准README.md模板
项目类型：实际项目
所属模块：自动化工具类
当前状态：待测试

以下是调用指令中每个参数的说明：
--project-type "actual-project"：项目类型（实际项目）
--module "automation-tools"：所属模块（自动化工具类）
--project-name "ai-log-analysis-script"：项目名称（AI日志分析脚本）
--version "v1.0"：项目版本号（v1.0）
--date "2026-03-01"：创建日期（2026年03月01日）
--status "pending-test"：项目状态（待测试）
```

### 步骤4：执行命令
1. 仅复制「Python调用命令行」（示例中的第二行代码，无需复制说明文字）：
   ```powershell
   python 'D:\AI Development\.kiro\ai-dev-script.py' --project-type "actual-project" --module "automation-tools" --project-name "ai-log-analysis-script" --version "v1.0" --date "2026-03-01" --status "pending-test"
   ```
2. 在Kiro终端粘贴命令并回车；
3. 等待脚本执行完成，终端输出 `🎉 全流程执行完成！` 即代表成功；
4. 查看终端输出，跳过的步骤会标注 `[跳过]`，便于确认执行状态。

## 五、Kiro 免确认执行配置（可选）
为避免每次执行命令都需要确认，配置Kiro信任命令：
1. 打开Kiro → 左下角「设置」（齿轮图标）；
2. 顶部搜索框输入 `kiroAgent.trustedCommands`；
3. 点击「Add Item」按钮，新增一行并输入：`python *`；
4. 点击右上角 ✔️ 保存设置；
5. 完全关闭Kiro（包括后台）→ 重新打开，配置生效。

## 六、常见问题排查（速查手册）
| 报错信息 | 原因 | 修复方案 |
|----------|------|----------|
| `日期格式错误` | 日期不符合 YYYY-MM-DD 格式 | 检查日期参数，确保格式正确（如 2026-03-01） |
| `项目名称格式错误` | 项目名包含大写字母/中文/特殊字符 | 仅使用小写字母、数字、短横线 |
| `项目目录已存在` | 重复创建同名项目 | 检查是否重复创建，或手动删除旧目录后重试 |
| `目录不存在且创建步骤已关闭` | init_project=false 但目录不存在 | 开启 init_project 或手动创建目录 |
| `README.md 已存在，将被覆盖` | README 文件已存在 | 警告提示，文件将被覆盖（正常行为） |
| `Git仓库已存在，跳过初始化` | .git 目录已存在 | 正常提示，跳过重复初始化 |
| `暂存区为空，跳过提交` | 没有文件可提交 | 检查 generate_readme 是否开启，或手动添加文件 |
| `Git仓库未初始化` | 提交时 Git 未初始化 | 开启 local_git 步骤 |
| `origin 已存在但URL不同` | 远程仓库 URL 冲突 | 脚本会自动更新为新 URL |
| `未配置GITHUB_TOKEN！` | Token未配置/配置失效 | 重新配置Token（方案A/B任选），重启Kiro |
| `GitHub Token 无效或已过期` | Token 失效或权限不足 | 重新生成Token并勾选`repo`权限 |
| `GitHub API 请求超时` | 网络连接问题 | 检查网络连接，重试命令 |
| `仓库已存在，跳过创建` | GitHub 仓库已存在 | 正常提示，跳过重复创建 |
| `推送失败：Connection reset` | SSH连接失败 | 1. 测试SSH：`ssh -T git@github.com`；<br>2. 配置SSH 443端口（见下方） |
| `推送失败：main分支不存在` | 分支名称不兼容 | 脚本已适配main/master分支，可在配置文件修改`default_branch` |
| `⚠️  配置文件格式错误` | JSON语法错误 | 检查`ai-dev-config.json`：逗号是否遗漏、引号是否配对、注释是否规范 |

### 补充：SSH 443端口配置（22端口屏蔽时）
1. 打开Kiro终端，执行：
   ```powershell
   notepad C:\Users\{你的用户名}\.ssh\config
   ```
2. 粘贴以下内容并保存：
   ```plaintext
   Host github.com
     Hostname ssh.github.com
     Port 443
     User git
   ```
3. 重新测试SSH连接：`ssh -T git@github.com`，提示 `Hi jjdayj! You've successfully authenticated` 即成功。

### 补充：配置文件常见错误修复
| 错误类型 | 错误示例 | 正确示例 |
|----------|----------|----------|
| 注释格式错误 | `// 全局开关`（JSON不支持//注释） | 移除//注释，或改用/* */（不推荐） |
| 逗号多余 | `"git_push": true,`（最后一个字段后有逗号） | `"git_push": true` |
| 引号不配对 | `"global_execution: true` | `"global_execution": true` |

## 七、核心总结
1. **功能完整性**：此版本采用「全局+3个分组开关」配置，可灵活控制脚本执行逻辑，同时保留所有基础配置、操作步骤、问题排查内容；
2. **配置核心规则**：
   - 全局开关`global_execution=true`：强制执行所有步骤，忽略单个开关；
   - 全局开关`global_execution=false`：按3个分组开关判断是否执行：
     - `init_project`：初始化项目（创建目录 + 生成 README）
     - `local_git`：本地 Git 管理（初始化 + 添加 + 提交）
     - `remote_git`：远程 Git 推送（创建仓库 + 配置远程 + 推送）
   - 配置文件缺失/错误时，脚本会自动使用默认配置（执行所有步骤）；
3. **边界情况处理**：
   - 参数格式自动验证（日期、项目名、模块名、版本号）；
   - 目录重复创建检测，避免覆盖已有项目；
   - 模块目录自动创建，无需手动准备；
   - Git 仓库状态智能检查，避免重复初始化；
   - 暂存区空提交检测，避免无意义提交；
   - 远程仓库 URL 冲突自动处理；
   - 网络超时和错误分类提示，便于快速定位问题；
4. **使用体验**：极简指令输入→按需调整配置→一键执行→全流程自动化，跳过步骤会标注`[跳过]`，执行状态清晰可查。

此文档为最终完整版，可直接作为团队使用手册，后续仅需调整`ai-dev-config.json`中的开关配置，无需修改核心脚本和Kiro规则文件。

---

## 🎉 总结

AI Development 项目管理系统已成功升级到 v2.0，实现了从单一功能到模块化智能系统的重大跃升：

### 🚀 核心升级亮点

1. **模块化架构重构**: 采用动态模块加载器，支持条件激活、优先级管理、依赖校验
2. **智能工作流增强**: VibCoding 双轨工作流支持需求管理、上下文感知、进度保存
3. **Git 提交自动化**: 智能提交信息生成、多层安全检查、错误类型识别
4. **完整的开发生态**: 从需求收集到代码提交的全流程自动化

### 📈 功能对比

| 功能 | v1.0 | v2.0 |
|------|------|------|
| 项目创建 | ✅ 基础功能 | ✅ 增强 + 需求管理 |
| Git 提交 | ✅ 基础提交 | ✅ 智能提交 + 安全检查 |
| 工作流 | ❌ 无 | ✅ 双轨工作流 |
| 模块管理 | ❌ 无 | ✅ 动态加载 + 条件激活 |
| 上下文感知 | ❌ 无 | ✅ 智能上下文管理 |
| 需求切换 | ❌ 无 | ✅ 多需求并行开发 |
| 安全检查 | ❌ 无 | ✅ 多层安全防护 |
| 回滚功能 | ❌ 无 | ✅ 智能回滚 + 备份 |

### 🎯 使用建议

- **新用户**: 直接使用新的模块化架构，体验完整的智能化开发流程
- **老用户**: 原有 AI Development 功能完全保留，可逐步迁移到新架构
- **团队协作**: 利用需求管理和上下文感知功能，提升团队协作效率
- **企业用户**: 使用安全检查和回滚功能，确保代码质量和安全性

### 🔮 未来规划

- **v2.1**: 增加更多模块（测试自动化、文档生成、代码审查）
- **v2.2**: 支持多语言项目和跨平台部署
- **v3.0**: 引入 AI 辅助决策和智能推荐系统

---

**项目状态**: ✅ 生产就绪  
**最后更新**: 2026-03-03  
**版本**: v2.0  
**维护者**: yangzhuo

感谢使用 AI Development 智能化项目管理系统！🚀