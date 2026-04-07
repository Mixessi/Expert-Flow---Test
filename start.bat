@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo   ========================================
echo        ExpertFlow 专家访谈智能助手
echo           Windows 启动脚本 v1.0
echo   ========================================
echo.

set "ROOT_DIR=%~dp0"

:: --- 检查依赖 ---
echo [1/5] 检查环境依赖...

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 python，请先安装 Python 3.9+
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到 node，请先安装 Node.js 18+
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"') do set PYTHON_VER=%%i
for /f "tokens=*" %%i in ('node -v') do set NODE_VER=%%i
echo   Python: %PYTHON_VER%  ^|  Node: %NODE_VER%

:: --- 创建环境配置文件 ---
echo.
echo [2/5] 配置环境文件...

if not exist "%ROOT_DIR%backend\.env" (
    (
        echo # ExpertFlow 后端配置
        echo # 数据库（默认使用 SQLite，无需额外安装）
        echo DATABASE_URL=sqlite+aiosqlite:///./expertflow.db
        echo.
        echo # Anthropic API Key（用于 AI 调研、提纲生成、JIT追问、纪要生成）
        echo # 不填则使用 Mock 数据演示，填入后启用真实 AI 功能
        echo # 获取地址：https://console.anthropic.com/
        echo ANTHROPIC_API_KEY=
        echo.
        echo # OpenAI Whisper API Key（用于实时语音转录）
        echo # 不填则使用 Mock 转录，填入后启用真实语音识别
        echo WHISPER_API_KEY=
        echo.
        echo # CORS 允许的前端地址
        echo CORS_ORIGINS=http://localhost:3000
        echo.
        echo # 文件上传目录
        echo UPLOAD_DIR=./uploads
    ) > "%ROOT_DIR%backend\.env"
    echo   已创建 backend\.env
) else (
    echo   backend\.env 已存在，跳过
)

if not exist "%ROOT_DIR%frontend\.env.local" (
    echo NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1> "%ROOT_DIR%frontend\.env.local"
    echo   已创建 frontend\.env.local
) else (
    echo   frontend\.env.local 已存在，跳过
)

:: --- 安装后端依赖 ---
echo.
echo [3/5] 安装后端依赖...
cd /d "%ROOT_DIR%backend"
pip install -r requirements.txt -q 2>nul
pip install aiosqlite -q 2>nul
echo   后端依赖安装完成

:: --- 安装前端依赖 ---
echo.
echo [4/5] 安装前端依赖...
cd /d "%ROOT_DIR%frontend"
call npm install --silent 2>nul
echo   前端依赖安装完成

:: --- 清理旧进程 ---
echo.
echo [5/5] 启动服务...

for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000 " ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":3000 " ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)

:: --- 启动后端 ---
cd /d "%ROOT_DIR%backend"
start "ExpertFlow-Backend" cmd /c "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: --- 启动前端 ---
cd /d "%ROOT_DIR%frontend"
start "ExpertFlow-Frontend" cmd /c "npm run dev -- -p 3000"

:: --- 等待启动 ---
echo.
echo   等待服务启动...
timeout /t 8 /nobreak >nul

echo.
echo   ========================================
echo     ExpertFlow 启动成功！
echo   ========================================
echo.
echo   前端界面:  http://localhost:3000
echo   后端 API:  http://localhost:8000
echo   API 文档:  http://localhost:8000/docs
echo.

:: 检查 API key
findstr /c:"ANTHROPIC_API_KEY=" "%ROOT_DIR%backend\.env" | findstr /v /c:"ANTHROPIC_API_KEY=sk-" >nul 2>&1
if %errorlevel% equ 0 (
    echo   提示: 未配置 Anthropic API Key
    echo   AI 功能将使用 Mock 数据演示
    echo   编辑 backend\.env 填入 API Key 启用真实 AI 功能
    echo.
)

echo   关闭此窗口将停止所有服务
echo   或按 Ctrl+C 停止
echo.
pause
