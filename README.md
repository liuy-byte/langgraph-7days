# LangGraph 14 天系列教程代码

微信公众号：技术洋的编程笔记

## 系列文章

| Day | 主题 | 文章 |
|-----|------|------|
| Day 1 | StateGraph 核心概念 | [链接]() |
| Day 2 | 状态管理与 Reducer | [链接]() |
| Day 3 | 工具调用 | [链接]() |
| Day 4 | Agent 开发 | [链接]() |
| Day 5 | Memory 与 Checkpoint | [链接]() |
| Day 6 | Subgraph 多 Agent | [链接]() |
| Day 7 | 生产部署 | [链接]() |
| Day 8 | Streaming 流式输出 | [链接]() |
| Day 9 | Human-in-the-Loop | [链接]() |
| Day 10 | Conditional Edges 条件路由 | [链接]() |
| Day 11 | RAG 深入实战 | [链接]() |
| Day 12 | Chatbot 对话机器人 | [链接]() |
| Day 13 | Code Assistant 编程助手 | [链接]() |
| Day 14 | LangGraph SDK 与生产部署 | [链接]() |

## 环境安装

```bash
# 克隆仓库（含 submodule）
gh repo clone liuy-byte/langgraph-7days --recursive

# 安装依赖
uv sync
```

## 运行示例

```bash
# Day 1: StateGraph 入门
uv run python api/day1_stategraph.py

# Day 8: Streaming 流式输出
uv run python api/day8_streaming.py

# Day 9: Human-in-the-Loop
uv run python api/day9_hitl.py

# Day 14: SDK 与生产部署
uv run python api/day14_sdk_deploy.py
```

## 文件结构

```
langgraph-7days/
├── api/
│   ├── day1_stategraph.py           # Day 1: StateGraph 核心
│   ├── day2_state_reducer.py        # Day 2: 状态管理
│   ├── day3_tools.py                # Day 3: 工具调用
│   ├── day4_agent.py                 # Day 4: Agent 开发
│   ├── day4_rag_agent.py            # Day 4: RAG Agent
│   ├── day4_sql_agent.py            # Day 4: SQL Agent
│   ├── day5_checkpoint.py           # Day 5: Checkpoint
│   ├── day6_subgraph.py             # Day 6: Subgraph
│   ├── day6_multi_agent.py          # Day 6: 多 Agent
│   ├── day7_deploy.py               # Day 7: 生产部署
│   ├── day8_streaming.py           # Day 8: 流式输出
│   ├── day9_hitl.py                # Day 9: 人机交互
│   ├── day10_conditional_retry.py  # Day 10: 条件路由
│   ├── day11_rag_deep.py           # Day 11: RAG 深入
│   ├── day12_chatbot.py            # Day 12: 对话机器人
│   ├── day13_code_assistant.py     # Day 13: 编程助手
│   └── day14_sdk_deploy.py         # Day 14: SDK 部署
└── pyproject.toml
```
