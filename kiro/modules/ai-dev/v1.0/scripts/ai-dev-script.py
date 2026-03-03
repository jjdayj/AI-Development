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
    # 支持模块化目录结构：从 ../configs/ 查找配置文件
    script_dir = os.path.dirname(__file__)
    config_path = os.path.join(script_dir, "..", "configs", "ai-dev-config.json")
    config_path = os.path.normpath(config_path)  # 规范化路径
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
        if CONFIG["global_execution"] or CONFIG["execution_steps"]["init_project"]:
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
                raise Exception(f"目录不存在且创建步骤已关闭：{local_full_path}\n请开启 init_project 或手动创建目录")

        # 3. 生成README.md（开关判断）
        if CONFIG["global_execution"] or CONFIG["execution_steps"]["init_project"]:
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
        if CONFIG["global_execution"] or CONFIG["execution_steps"]["local_git"]:
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
        if CONFIG["global_execution"] or CONFIG["execution_steps"]["local_git"]:
            print(f"4/8 添加文件到暂存区...")
            run_git_command("git add .", cwd=local_full_path)
        else:
            print(f"4/8 添加文件到暂存区... [跳过]")

        # 6. Git提交（开关判断）
        if CONFIG["global_execution"] or CONFIG["execution_steps"]["local_git"]:
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
                    raise Exception("Git仓库未初始化，请开启 local_git 步骤")
                raise
        else:
            print(f"5/8 提交代码... [跳过]")

        # 7. 创建GitHub仓库（开关判断）
        if CONFIG["global_execution"] or CONFIG["execution_steps"]["remote_git"]:
            print(f"6/8 创建远端仓库...")
            create_github_repo(repo_name)
        else:
            print(f"6/8 创建远端仓库... [跳过]")

        # 8. 配置远程仓库（开关判断）
        if CONFIG["global_execution"] or CONFIG["execution_steps"]["remote_git"]:
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
        if CONFIG["global_execution"] or CONFIG["execution_steps"]["remote_git"]:
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