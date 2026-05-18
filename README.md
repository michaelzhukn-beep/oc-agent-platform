# 🎭 OC Agent Platform

一个基于 FastAPI 和 DeepSeek 的角色扮演 AI 聊天系统，支持多角色切换、多轮对话记忆和流式输出。

## ✨ 核心特性

- 🎭 **多角色扮演**：通过 JSON 配置文件管理角色卡（性格、背景、说话风格），支持热扩展
- 💬 **多轮对话记忆**：基于 session_id 的会话隔离，每个用户独立保留上下文
- ⚡ **流式输出**：基于 SSE（Server-Sent Events）实现打字机效果，首字延迟 < 1 秒
- 🛡️ **错误处理**：完善的 HTTP 状态码区分（404 角色不存在 / 400 角色卡字段缺失 / 422 请求体校验失败）
- 🌐 **CORS 支持**：通过中间件配置跨域，前后端分离友好

## 🏗️ 技术栈

| 类别 | 技术 |
|---|---|
| 后端框架 | FastAPI |
| LLM 服务 | DeepSeek API |
| 数据校验 | Pydantic |
| 异步服务器 | Uvicorn |
| 包管理 | uv |

## 📁 项目结构
oc-agent-platform/
├── server.py              # FastAPI 主服务，包含所有路由和业务逻辑
├── characters/            # 角色卡 JSON 配置
│   ├── jingtian.json
│   ├── xuejian.json
│   └── longkui.json
├── pyproject.toml         # 项目依赖配置
├── .env                   # 环境变量（不入库，需自行创建）
└── README.md

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/michaelzhukn-beep/oc-agent-platform.git
cd oc-agent-platform
```

### 2. 安装依赖

使用 [uv](https://github.com/astral-sh/uv) 管理依赖：

```bash
uv sync
```

### 3. 配置环境变量

在项目根目录创建 `.env` 文件：
DEEPSEEK_API_KEY=你的DeepSeek API Key

> 在 [DeepSeek 开放平台](https://platform.deepseek.com/) 申请 API Key。

### 4. 启动服务

```bash
uv run uvicorn server:app --reload
```

访问 `http://127.0.0.1:8000/docs` 打开 Swagger UI 测试接口。

## 📚 API 接口

### `GET /characters`

获取所有可用角色列表。

**响应示例**：

```json
{
  "character": ["jingtian", "longkui", "xuejian"]
}
```

### `POST /chat`

与指定角色进行流式对话。

**请求体**：

```json
{
  "message": "你好啊",
  "character": "jingtian",
  "session_id": "user_001"
}
```

**响应**：`text/event-stream` 流式响应，逐字推送 AI 回复。

**错误码**：

| 状态码 | 含义 |
|---|---|
| 404 | 角色文件不存在 |
| 400 | 角色卡缺少必要字段 |
| 422 | 请求体格式校验失败 |

## 🎨 添加新角色

在 `characters/` 目录下创建新 JSON 文件，遵循以下格式：

```json
{
  "name": "角色名",
  "gender": "性别",
  "personality": "性格描述",
  "speaking_style": "说话风格",
  "backstory": "背景故事"
}
```

服务器会自动识别新角色，**无需重启**。

## 🛣️ 后续规划（Roadmap）

- [ ] **V2**：接入 Milvus 向量数据库 + Neo4j 图数据库，实现 RAG 长期记忆
- [ ] **V2**：基于 LangGraph 编排"记忆检索 + 对话生成"流程
- [ ] **V3**：使用 LoRA 微调垂直角色模型
- [ ] **V3**：Docker 容器化部署

## 📝 技术决策

### 为什么用 JSON 文件管理角色，而不是数据库？
- 配置与代码分离，加角色无需改代码
- 非程序员（如运营）也能维护角色卡
- 支持热更新，修改后无需重启服务

### 为什么用 SSE 而不是 WebSocket？
- 聊天场景是**单向推送**（服务器 → 客户端），SSE 更轻量
- SSE 基于 HTTP，无需额外协议升级
- 浏览器原生支持，前端实现简单

### 为什么用全局字典管理 sessions？
- 当前阶段为单机部署，全局变量足够
- 生产环境会迁移到 Redis 以支持持久化和多实例共享