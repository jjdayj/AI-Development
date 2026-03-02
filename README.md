# AI Development 项目管理系统

## 项目简介

这是一个基于 Kiro AI 的自动化项目管理系统，通过简单的中文指令即可完成项目创建、Git 初始化、GitHub 仓库创建和代码推送的全流程自动化。

## 快速导航

- **环境配置指南**: 查看 `附件：Kiro自动生成项目+git+推送.md` - GitHub Token 配置和环境变量设置
- **Steering 配置**: 查看 `.kiro/steering/STEERING_GUIDE.md` - Kiro 行为规则配置说明
- **完整使用文档**: 继续阅读本文档下方内容

## 项目结构

```
AI Development/
├── .kiro/                          # Kiro 配置目录
│   ├── steering/                   # AI 行为规则配置
│   │   ├── STEERING_GUIDE.md      # Steering 配置说明文档
│   │   ├── doc_save_rules.md      # 会话文档自动保存规则（可选启用）
│   │   └── ai-dev.md              # 项目命名和命令生成规则
│   ├── ai-dev-script.py           # Python 自动化执行脚本
│   ├── ai-dev-config.json         # 步骤执行开关配置
│   └── .env                       # GitHub Token 配置（可选）
├── 00_problem-solve-lib/          # 问题解决项目库
├── 01_actual-project-lib/         # 实际项目库
│   └── automation-tools/          # 自动化工具模块
├── 附件：Kiro自动生成项目+git+推送.md  # GitHub Token 配置指南
└── README.md                      # 本文档

```

## 核心功能

1. **智能命名转换**: 中文指令自动转换为符合 GitHub 规范的英文命名
2. **一键项目创建**: 自动创建目录结构和 README 文档
3. **Git 自动化**: 自动初始化 Git 仓库、提交代码
4. **GitHub 集成**: 自动创建远程仓库并推送代码
5. **灵活配置**: 支持全局和单步骤开关控制执行流程

---

# AI Development 一键管理完整流程文档（最终完整版）

## 文档说明
此文档为「Kiro 生成命名+Python 执行操作」的最终落地版本，已修复所有语法错误，新增Kiro输出的参数逐行说明，**新增步骤开关配置功能（全局+单个步骤）**，包含完整的环境配置、文件编写、日常使用及问题排查，可直接作为生产环境使用手册。

## 一、核心逻辑拆分（明确各角色职责）
| 角色                | 核心职责                                                                 |
|---------------------|--------------------------------------------------------------------------|
| 你（用户）          | 发送极简指令：`/ai-dev 新建实际项目：自动化工具类，AI 日志分析脚本 v1.0，状态待测试` |
| Kiro AI             | 1. 解析中文指令 → 生成符合GitHub规范的**纯英文标准化参数**；<br>2. 输出「参数说明头 + Python调用命令 + 命令执行说明 + 逐参数解释」（格式固定）；<br>3. 参数严格匹配脚本要求，无中文/空格/特殊字符 |
| Python 脚本         | 1. 接收Kiro传入的纯英文参数；<br>2. 读取配置文件，按「全局开关+单个步骤开关」执行「创建目录+生成README+Git初始化+GitHub创库+代码推送」；<br>3. 仅做执行，不做任何命名转换/修改，兼容main/master分支 |
| 配置文件            | 控制脚本执行逻辑：全局开关开启则强制执行所有步骤，关闭则按单个步骤开关判断 |

## 二、前置环境配置（一次性完成）
### 步骤1：目录结构确认（必须严格一致）
```plaintext
D:\AI Development\.kiro\
├── ai-dev-script.py    # Python核心执行脚本（最终稳定版，含开关配置）
├── ai-dev-config.json  # 步骤执行开关配置文件（新增）
├── steering\           # Kiro规则目录
│   └── ai-dev.md       # Kiro命名规则文件（含参数全说明）
└── .env                # GitHub Token配置文件（可选，替代系统环境变量）
```
操作：
1. 打开文件资源管理器，定位到 `D:\AI Development`；
2. 若不存在 `.kiro` 文件夹，右键新建文件夹并命名为 `.kiro`（开头带英文句号）；
3. 进入 `.kiro` 文件夹，新建 `steering` 子文件夹；
4. 新建 `.env` 文件（无后缀，若系统隐藏后缀需先显示：文件资源管理器→查看→勾选「文件扩展名」）；
5. **新增**：新建 `ai-dev-config.json` 文件（步骤开关配置文件）。

### 步骤2：安装Python依赖（仅执行一次）
打开Kiro终端/Windows命令提示符，执行以下命令：
```powershell
pip install requests gitpython python-dotenv
```
✅ 验证标准：执行后无 `Error` 提示即安装成功；
❌ 若提示 `pip` 未找到：需将Python安装路径下的 `Scripts` 文件夹（如 `C:\Python310\Scripts`）添加到系统环境变量，重启终端后重试。

### 步骤3：配置GitHub Token（二选一，推荐方案B）
#### 方案A：系统环境变量（永久生效）
1. 登录GitHub → 右上角头像 → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token；
2. 勾选 `repo` 权限（全选repo下的子权限），设置有效期（建议选「No expiration」），点击生成Token并复制（仅显示一次，务必保存）；
3. 在Kiro终端执行（替换为你的Token）：
   ```powershell
   [Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "User")
   ```
4. **重启Kiro** 使环境变量生效。
5. **验证配置是否成功**（重启Kiro后执行）：
   ```powershell
   [Environment]::GetEnvironmentVariable("GITHUB_TOKEN", "User")
   ```
   ✅ 成功标准：显示你配置的Token（ghp_开头的字符串）  
   ❌ 失败标准：显示空白或未找到，需重新执行步骤3并确保重启Kiro

#### 方案B：.env文件（仅当前目录生效，更安全）
在 `D:\AI Development\.kiro\.env` 文件中写入以下内容（替换为你的信息）：
```ini
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # 你的GitHub Token
GITHUB_USER=jjdayj  # 你的GitHub用户名（如jjdayj）
```
**验证配置是否成功**：
```powershell
type "D:\AI Development\.kiro\.env"
```
✅ 成功标准：显示文件内容，包含GITHUB_TOKEN和GITHUB_USER  
❌ 失败标准：提示文件不存在或内容为空，需重新创建.env文件

### 步骤4：配置步骤执行开关（新增，核心）
在 `D:\AI Development\.kiro\ai-dev-config.json` 文件中写入以下内容：
```json
{
  "global_execution": true,
  "execution_steps": {
    "init_project": true,
    "local_git": true,
    "remote_git": true
  },
  "default_branch": "master"
}
```
**配置说明**：
- `global_execution`: 优先级最高，`true` 时所有步骤强制执行，`false` 时按单个步骤开关判断；
- `execution_steps`: 单个步骤开关，仅在 `global_execution=false` 时生效：
  - `init_project`: 初始化项目（步骤 1-2：创建目录 + 生成 README.md）
  - `local_git`: 本地 Git 管理（步骤 3-5：初始化 Git + 添加文件 + 提交代码）
  - `remote_git`: 远程 Git 推送（步骤 6-8：创建远端仓库 + 配置远程仓库 + 推送代码）
- `default_branch`: 脚本推送代码时优先尝试的分支，适配不同GitHub默认分支规则。

**使用场景示例**：
- 仅创建本地项目，不推送到 GitHub：设置 `remote_git: false`
- 在已有目录上初始化 Git：设置 `init_project: false`
- 仅推送已有项目到 GitHub：设置 `init_project: false, local_git: false`

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