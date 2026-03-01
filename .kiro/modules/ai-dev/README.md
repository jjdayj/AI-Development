# AI Development 自动化管理模块

通过简单的中文指令完成项目全流程自动化：智能命名转换、目录创建、Git 初始化、GitHub 仓库创建和推送。

## 功能特性

- ✅ **智能命名转换**：中文指令自动转换为符合 GitHub 规范的英文命名
- ✅ **一键项目创建**：自动创建目录结构和 README 文档
- ✅ **Git 自动化**：自动初始化 Git 仓库、提交代码
- ✅ **GitHub 集成**：自动创建远程仓库并推送代码
- ✅ **灵活配置**：支持全局和单步骤开关控制执行流程

## 快速开始

### 1. 安装依赖

```bash
pip install requests gitpython python-dotenv
```

### 2. 配置 GitHub Token

在 `.kiro/.env` 文件中配置：

```ini
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GITHUB_USER=your-username
```

### 3. 使用示例

在 Kiro 中输入：

```
/ai-dev 新建实际项目：自动化工具类，AI 日志分析脚本 v1.0，状态待测试
```

Kiro 会生成 Python 命令，复制执行即可。

## 目录结构

```
.kiro/modules/ai-dev/
├── v1.0/                   # 当前版本
│   ├── steering/
│   │   └── ai-dev.md      # Kiro 命名规则
│   ├── scripts/
│   │   └── ai-dev-script.py  # 执行脚本
│   ├── configs/
│   │   └── ai-dev-config.json  # 配置文件
│   └── meta.yaml          # 模块元数据
├── LICENSE                # MIT License
└── README.md              # 本文件
```

## 配置说明

编辑 `v1.0/configs/ai-dev-config.json`：

```json
{
  "global_execution": false,
  "execution_steps": {
    "init_project": true,   // 初始化项目
    "local_git": true,      // 本地 Git 管理
    "remote_git": true      // 远程 Git 推送
  },
  "default_branch": "master"
}
```

## 版本历史

### v1.0 (2026-03-01)
- 初始版本
- 支持中文指令转英文参数
- 支持项目目录创建和 README 生成
- 支持 Git 仓库初始化和提交
- 支持 GitHub 远程仓库创建和推送
- 支持步骤开关配置

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- 项目主页：https://github.com/your-org/kiro-ai-dev
- 问题反馈：https://github.com/your-org/kiro-ai-dev/issues
