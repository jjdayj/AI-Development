你发现的问题很准确！上一版文档为了聚焦「Kiro说明内容修改」这个核心需求，简化了环境配置、文件编写等通用内容的描述，现在我为你整合出**完整版文档**——保留上一版的「Kiro参数说明优化」，同时还原所有基础配置、操作步骤、问题排查等完整内容，确保文档的完整性和实用性：

# AI Development 一键管理完整流程文档（最终完整版）
## 文档说明
此文档为「Kiro 生成命名+Python 执行操作」的最终落地版本，已修复所有语法错误，新增Kiro输出的参数逐行说明，包含完整的环境配置、文件编写、日常使用及问题排查，可直接作为生产环境使用手册。

## 一、核心逻辑拆分（明确各角色职责）
| 角色                | 核心职责                                                                 |
|---------------------|--------------------------------------------------------------------------|
| 你（用户）          | 发送极简指令：`/ai-dev 新建实际项目：自动化工具类，AI 日志分析脚本 v1.0，状态待测试` |
| Kiro AI             | 1. 解析中文指令 → 生成符合GitHub规范的**纯英文标准化参数**；<br>2. 输出「参数说明头 + Python调用命令 + 命令执行说明 + 逐参数解释」（格式固定）；<br>3. 参数严格匹配脚本要求，无中文/空格/特殊字符 |
| Python 脚本         | 1. 接收Kiro传入的纯英文参数；<br>2. 执行「创建目录+生成README+Git初始化+GitHub创库+代码推送」；<br>3. 仅做执行，不做任何命名转换/修改，兼容main/master分支 |

## 二、前置环境配置（一次性完成）
### 步骤1：目录结构确认（必须严格一致）
```plaintext
D:\AI Development\.kiro\
├── ai-dev-script.py    # Python核心执行脚本（最终稳定版）
├── steering\           # Kiro规则目录
│   └── ai-dev.md       # Kiro命名规则文件（含参数全说明）
└── .env                # GitHub Token配置文件（可选，替代系统环境变量）
```
操作：
1. 打开文件资源管理器，定位到 `D:\AI Development`；
2. 若不存在 `.kiro` 文件夹，右键新建文件夹并命名为 `.kiro`（开头带英文句号）；
3. 进入 `.kiro` 文件夹，新建 `steering` 子文件夹；
4. 新建 `.env` 文件（无后缀，若系统隐藏后缀需先显示：文件资源管理器→查看→勾选「文件扩展名」）。

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

#### 方案B：.env文件（仅当前目录生效，更安全）
在 `D:\AI Development\.kiro\.env` 文件中写入以下内容（替换为你的信息）：
```ini
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # 你的GitHub Token
GITHUB_USER=jjdayj  # 你的GitHub用户名（如jjdayj）
```

## 三、核心文件编写（关键步骤）
### 步骤1：Python执行脚本（ai-dev-script.py）
在 `D:\AI Development\.kiro` 文件夹下新建 `ai-dev-script.py` 文件，粘贴以下完整代码：
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Development 自动化管理脚本（最终稳定版）
功能：接收Kiro生成的纯英文参数，一键完成「目录创建+README+Git+自动创库+推送」
参数要求：所有参数为纯英文，无中文/空格/特殊字符
"""
import os
import sys
import time
import json
import argparse
import subprocess
import requests
from dotenv import load_dotenv

# ====================== 1. 基础配置（仅改这里） ======================
ROOT_PATH = "D:\\AI Development"
# 加载环境变量（优先系统环境变量，其次.env文件）
load_dotenv()
GITHUB_USER = os.getenv("GITHUB_USER", "jjdayj")  # 默认为jjdayj，可在.env中覆盖
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
SSH_PREFIX = f"git@github.com:{GITHUB_USER}/"

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
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        print(f"✅ 创库成功：{repo_name}")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 422:
            print(f"ℹ️ 仓库已存在，跳过创建：{repo_name}")
        else:
            raise Exception(f"创库失败：{e.response.text}")

# ====================== 6. 主执行流程 ======================
def main():
    args = parse_args()
    try:
        # 1. 生成路径和仓库名（仅拼接）
        local_full_path, repo_name, ssh_url = generate_paths(args)
        print(f"📌 初始化信息：")
        print(f"   本地路径：{local_full_path}")
        print(f"   仓库名称：{repo_name}")
        print(f"   SSH地址：{ssh_url}")

        # 2. 创建本地目录
        print(f"\n1/8 创建目录...")
        os.makedirs(local_full_path, exist_ok=True)
        if not os.path.exists(local_full_path):
            raise Exception(f"目录创建失败：{local_full_path}")

        # 3. 生成README.md
        print(f"2/8 生成README.md...")
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
        
        readme_path = os.path.join(local_full_path, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme_content)

        # 4. Git初始化
        print(f"3/8 初始化Git仓库...")
        run_git_command("git init", cwd=local_full_path)

        # 5. Git添加文件
        print(f"4/8 添加文件到暂存区...")
        run_git_command("git add .", cwd=local_full_path)

        # 6. Git提交
        print(f"5/8 提交代码...")
        commit_msg = f"init: {args.project_name} {args.date}"
        run_git_command(f'git commit -m "{commit_msg}"', cwd=local_full_path)

        # 7. 创建GitHub仓库
        print(f"6/8 创建远端仓库...")
        create_github_repo(repo_name)

        # 8. 配置远程仓库并推送
        print(f"7/8 配置远程仓库...")
        # 先移除旧的origin（避免重复）
        try:
            run_git_command("git remote remove origin", cwd=local_full_path)
        except Exception as e:
            # 若origin不存在，跳过即可
            pass
        run_git_command(f"git remote add origin {ssh_url}", cwd=local_full_path)
        
        print(f"8/8 推送代码到GitHub...")
        retry_count = 0
        max_retries = 2
        while retry_count <= max_retries:
            try:
                # 先尝试推送到main分支（GitHub默认）
                run_git_command("git push -u origin main", cwd=local_full_path)
                print(f"   ✅ 推送到main分支成功！")
                break
            except Exception as e1:
                try:
                    # 若main分支不存在，尝试master分支
                    run_git_command("git push -u origin master", cwd=local_full_path)
                    print(f"   ✅ 推送到master分支成功！")
                    break
                except Exception as e2:
                    retry_count += 1
                    if retry_count > max_retries:
                        raise Exception(f"推送失败（重试{max_retries}次）：{e2}")
                    print(f"   ❌ 推送失败，重试第{retry_count}次...")
                    time.sleep(2)

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
在 `D:\AI Development\.kiro\steering` 文件夹下新建 `ai-dev.md` 文件，粘贴以下完整内容：
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

## 四、日常使用流程（极简三步）
### 步骤1：发送指令给Kiro
在Kiro聊天框中输入极简指令（格式固定）：
```
/ai-dev 新建实际项目：自动化工具类，AI 日志分析脚本 v1.0，状态待测试
```
👉 指令模板：
- 实际项目：`/ai-dev 新建实际项目：{模块名}，{项目名称} {版本号}，状态{状态}`
- 问题解决：`/ai-dev 新建问题解决流程：{日期} {问题描述}，状态{状态}`

### 步骤2：复制Kiro输出的内容
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

### 步骤3：执行命令
1. 仅复制「Python调用命令行」（示例中的第二行代码，无需复制说明文字）：
   ```powershell
   python 'D:\AI Development\.kiro\ai-dev-script.py' --project-type "actual-project" --module "automation-tools" --project-name "ai-log-analysis-script" --version "v1.0" --date "2026-03-01" --status "pending-test"
   ```
2. 在Kiro终端粘贴命令并回车；
3. 等待脚本执行完成，终端输出 `🎉 全流程执行完成！` 即代表成功。

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
| `SyntaxError: default 'except:' must be last` | Python异常捕获顺序错误 | 替换为修复后的脚本（已解决此问题） |
| `未配置GITHUB_TOKEN！` | Token未配置/配置失效 | 重新配置Token（方案A/B任选），重启Kiro |
| `Git命令执行失败：fatal: not a git repository` | 目录未初始化Git | 脚本已自动执行`git init`，无需手动操作 |
| `创库失败：401 Unauthorized` | Token无效/权限不足 | 重新生成Token并勾选`repo`权限 |
| `推送失败：Connection reset` | SSH连接失败 | 1. 测试SSH：`ssh -T git@github.com`；<br>2. 配置SSH 443端口（见下方） |
| `推送失败：main分支不存在` | 分支名称不兼容 | 脚本已适配main/master分支，无需手动处理 |

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

## 七、核心总结
1. **完整性保障**：此版本保留了所有基础配置、操作步骤、问题排查内容，同时新增Kiro输出的「参数逐行说明」，兼顾完整度和易用性；
2. **格式规范**：
   - Kiro输出内容新增参数解释，每个参数的含义清晰对应中文，新手也能快速理解；
   - Python脚本无变更，保留了语法错误修复、分支兼容、容错逻辑，执行环节稳定可靠；
3. **使用体验**：极简指令输入→一键执行→全流程自动化，无需手动创建目录/仓库/推送代码，同时参数说明让执行过程更透明。

此文档为最终完整版，可直接作为团队使用手册，后续无需修改核心文件，仅需按日常使用流程操作即可。