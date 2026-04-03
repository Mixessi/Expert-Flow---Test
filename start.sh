#!/bin/bash
set -e

# ============================================
# ExpertFlow 一键启动脚本
# ============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "  ╔═══════════════════════════════════════╗"
echo "  ║       ExpertFlow 专家访谈智能助手       ║"
echo "  ║            一键启动脚本 v1.0            ║"
echo "  ╚═══════════════════════════════════════╝"
echo -e "${NC}"

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# --- 检查依赖 ---
echo -e "${YELLOW}[1/5] 检查环境依赖...${NC}"

if ! command -v python3 &>/dev/null; then
    echo -e "${RED}错误: 未找到 python3，请先安装 Python 3.9+${NC}"
    exit 1
fi

if ! command -v node &>/dev/null; then
    echo -e "${RED}错误: 未找到 node，请先安装 Node.js 18+${NC}"
    exit 1
fi

PYTHON_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
NODE_VER=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
echo -e "  Python: ${GREEN}${PYTHON_VER}${NC}  |  Node: ${GREEN}${NODE_VER}${NC}"

# --- 创建环境配置文件 ---
echo -e "${YELLOW}[2/5] 配置环境文件...${NC}"

if [ ! -f "$ROOT_DIR/backend/.env" ]; then
    cat > "$ROOT_DIR/backend/.env" << 'ENV'
# ExpertFlow 后端配置
# 数据库（默认使用 SQLite，无需额外安装）
DATABASE_URL=sqlite+aiosqlite:///./expertflow.db

# Anthropic API Key（用于 AI 调研、提纲生成、JIT追问、纪要生成）
# 不填则使用 Mock 数据演示，填入后启用真实 AI 功能
# 获取地址：https://console.anthropic.com/
ANTHROPIC_API_KEY=

# OpenAI Whisper API Key（用于实时语音转录）
# 不填则使用 Mock 转录，填入后启用真实语音识别
WHISPER_API_KEY=

# CORS 允许的前端地址
CORS_ORIGINS=http://localhost:3000

# 文件上传目录
UPLOAD_DIR=./uploads
ENV
    echo -e "  ${GREEN}已创建 backend/.env${NC}"
else
    echo -e "  backend/.env 已存在，跳过"
fi

if [ ! -f "$ROOT_DIR/frontend/.env.local" ]; then
    cat > "$ROOT_DIR/frontend/.env.local" << 'ENV'
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
ENV
    echo -e "  ${GREEN}已创建 frontend/.env.local${NC}"
else
    echo -e "  frontend/.env.local 已存在，跳过"
fi

# --- 安装后端依赖 ---
echo -e "${YELLOW}[3/5] 安装后端依赖...${NC}"
cd "$ROOT_DIR/backend"
pip install -r requirements.txt -q 2>/dev/null || pip3 install -r requirements.txt -q 2>/dev/null
pip install aiosqlite -q 2>/dev/null || pip3 install aiosqlite -q 2>/dev/null
echo -e "  ${GREEN}后端依赖安装完成${NC}"

# --- 安装前端依赖 ---
echo -e "${YELLOW}[4/5] 安装前端依赖...${NC}"
cd "$ROOT_DIR/frontend"
npm install --silent 2>/dev/null
echo -e "  ${GREEN}前端依赖安装完成${NC}"

# --- 启动服务 ---
echo -e "${YELLOW}[5/5] 启动服务...${NC}"

# 清理可能残留的旧进程
lsof -ti:8000 2>/dev/null | xargs kill 2>/dev/null || true
lsof -ti:3000 2>/dev/null | xargs kill 2>/dev/null || true

# 启动后端
cd "$ROOT_DIR/backend"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 启动前端
cd "$ROOT_DIR/frontend"
npm run dev -- -p 3000 &
FRONTEND_PID=$!

# 等待服务启动
sleep 5

echo ""
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ExpertFlow 启动成功！${NC}"
echo -e "${GREEN}════════════════════════════════════════════${NC}"
echo ""
echo -e "  前端界面:  ${BLUE}http://localhost:3000${NC}"
echo -e "  后端 API:  ${BLUE}http://localhost:8000${NC}"
echo -e "  API 文档:  ${BLUE}http://localhost:8000/docs${NC}"
echo ""

# 检查 API key 配置
if grep -q "^ANTHROPIC_API_KEY=$" "$ROOT_DIR/backend/.env" 2>/dev/null; then
    echo -e "  ${YELLOW}提示: 未配置 Anthropic API Key${NC}"
    echo -e "  ${YELLOW}AI 功能将使用 Mock 数据演示${NC}"
    echo -e "  ${YELLOW}编辑 backend/.env 填入 API Key 启用真实 AI 功能${NC}"
    echo ""
fi

echo -e "  按 ${RED}Ctrl+C${NC} 停止所有服务"
echo ""

# 捕获退出信号，清理子进程
cleanup() {
    echo ""
    echo -e "${YELLOW}正在停止服务...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}已停止所有服务${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 等待子进程
wait
