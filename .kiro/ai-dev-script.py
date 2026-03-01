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