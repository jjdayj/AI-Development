@echo off
chcp 65001 >nul
echo ========================================
echo AI Development 目录自动化管理脚本
echo ========================================
echo.

REM 设置变量
set ROOT_DIR=D:\AI Development
set CATEGORY_DIR=%ROOT_DIR%\00_问题解决流程库
set PROJECT_DIR=%CATEGORY_DIR%\2026-03-02-01-Git-解决push权限错误（完成）

REM 步骤1：创建目录
echo [1/6] 创建目录结构...
if not exist "%ROOT_DIR%" mkdir "%ROOT_DIR%"
if not exist "%CATEGORY_DIR%" mkdir "%CATEGORY_DIR%"
if not exist "%PROJECT_DIR%" mkdir "%PROJECT_DIR%"
echo ✓ 目录创建完成
echo.

REM 步骤2：进入项目目录
cd /d "%PROJECT_DIR%"
echo [2/6] 当前工作目录: %CD%
echo.

REM 步骤3：初始化Git仓库
echo [3/6] 初始化Git仓库...
git init
echo ✓ Git仓库初始化完成
echo.

REM 步骤4：创建README.md
echo [4/6] 创建README.md文件...
(
echo # Git Push 权限错误解决方案
echo.
echo ## 问题描述
echo 在执行 `git push` 时遇到权限错误（Permission denied）
echo.
echo ## 解决日期
echo 2026-03-02
echo.
echo ## 问题状态
echo ✅ 已完成
echo.
echo ## 解决步骤
echo 1. 检查SSH密钥配置
echo 2. 验证GitHub账号权限
echo 3. 更新远程仓库URL
echo 4. 重新推送代码
echo.
echo ## 相关文档
echo - [GitHub SSH配置文档](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
echo - [Git权限问题排查指南](https://git-scm.com/book/en/v2/Git-on-the-Server-Getting-Git-on-a-Server)
echo.
echo ## 标签
echo `#Git` `#权限问题` `#SSH` `#GitHub`
) > README.md
echo ✓ README.md创建完成
echo.

REM 步骤5：添加并提交
echo [5/6] 添加文件并提交...
git add .
git commit -m "初始化：Git push权限错误解决流程文档"
echo ✓ 文件提交完成
echo.

REM 步骤6：关联远程仓库并推送
echo [6/6] 关联远程仓库...
echo.
echo ⚠️  请手动执行以下命令（需要替换YOUR_GITHUB_USERNAME）：
echo.
echo git remote add origin https://github.com/YOUR_GITHUB_USERNAME/2026-03-02-01-Git-解决push权限错误.git
echo git branch -M main
echo git push -u origin main
echo.
echo ========================================
echo ✅ 本地操作完成！
echo ========================================
pause
