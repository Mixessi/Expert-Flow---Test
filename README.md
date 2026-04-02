# ExpertFlow - 专家访谈智能助手

ExpertFlow 是一款面向投资/战略研究团队的专家访谈智能助手，覆盖访谈前、访谈中、访谈后三大阶段。

## 核心功能

### 访谈前
- **AI 智能调研**: 基于核心问题自动搜索公开信息（Claude extended thinking + web search）
- **参考文档管理**: 上传 PDF/Word/文本文档，作为会前和会中的数据参考
- **智能提纲生成**: 整合调研结果和参考文档，生成结构化访谈提纲

### 访谈中
- **实时语音转录**: 音频实时转文字（Whisper ASR）
- **JIT 追问提示**: 基于实时对话生成即时追问建议
- **数字 Cross Check**: 自动提取并交叉校验专家提及的数字
- **专家可信度评估**: 实时评估专家回答的可信度

### 访谈后
- **AI 纪要生成**: 自动生成结构化访谈纪要
- **关键数字必录**: 确保所有专家提及的数字无遗漏（>99% 捕获率）

## 技术栈

- **前端**: Next.js 15 + TypeScript + Tailwind CSS + Zustand
- **后端**: Python FastAPI + SQLAlchemy (async)
- **数据库**: PostgreSQL
- **AI**: Claude API (Anthropic) + OpenAI Whisper
- **实时通信**: WebSocket

## 快速开始

### 1. 启动数据库
```bash
docker-compose up -d
```

### 2. 启动后端
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # 编辑 .env 填入 API keys
uvicorn app.main:app --reload --port 8000
```

### 3. 启动前端
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

访问 http://localhost:3000 开始使用。

## 项目结构

```
├── docker-compose.yml          # PostgreSQL + Redis
├── backend/                    # FastAPI 后端
│   └── app/
│       ├── main.py             # 应用入口
│       ├── models/             # 数据库模型 (8张表)
│       ├── schemas/            # API 请求/响应模型
│       ├── api/                # REST 路由 + WebSocket
│       ├── services/           # AI 业务逻辑
│       └── core/               # Claude 客户端, 提示词模板
└── frontend/                   # Next.js 前端
    └── src/
        ├── app/                # 页面路由
        ├── components/         # UI 组件
        ├── hooks/              # WebSocket, 音频录制等
        ├── lib/                # API 客户端, 类型定义
        └── stores/             # Zustand 状态管理
```
