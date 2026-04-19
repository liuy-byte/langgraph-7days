"""
LangGraph 7天系列 Day 12：Chatbot 对话机器人

本代码演示完整的对话机器人，包含：
- 多轮对话记忆
- 模式切换（闲聊/任务）
- 流式输出
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


# ============ 1. 定义状态 ============
class ChatbotState(TypedDict):
    messages: list
    mode: str  # "chat" / "task"
    context: dict


# ============ 2. 定义节点 ============
def router(state: ChatbotState) -> str:
    """路由消息到不同模式"""
    last_msg = state["messages"][-1]["content"] if state["messages"] else ""

    # 简单路由逻辑
    if any(kw in last_msg for kw in ["帮我", "请", "查询", "搜索"]):
        return "task_mode"
    return "chat_mode"


def chat_mode(state: ChatbotState) -> dict:
    """闲聊模式"""
    last_msg = state["messages"][-1]["content"] if state["messages"] else ""
    return {
        "messages": [{"role": "assistant", "content": f"闲聊: {last_msg}"}],
        "mode": "chat"
    }


def task_mode(state: ChatbotState) -> dict:
    """任务模式"""
    last_msg = state["messages"][-1]["content"] if state["messages"] else ""
    return {
        "messages": [{"role": "assistant", "content": f"任务已记录: {last_msg}"}],
        "mode": "task"
    }


# ============ 3. 构建对话机器人图 ============
memory = InMemorySaver()
builder = StateGraph(ChatbotState)

builder.add_node("chat_mode", chat_mode)
builder.add_node("task_mode", task_mode)

# 使用条件边根据输入决定模式
builder.add_conditional_edges(
    START,
    router,
    {"chat_mode": "chat_mode", "task_mode": "task_mode"}
)

builder.add_edge("chat_mode", END)
builder.add_edge("task_mode", END)

app = builder.compile(checkpointer=memory)


# ============ 4. 多轮对话演示 ============
if __name__ == "__main__":
    print("=== Chatbot 对话机器人演示 ===")
    print()

    thread_id = "chatbot-demo"
    config = {"configurable": {"thread_id": thread_id}}

    # 回合 1：闲聊
    print("用户: 你好！")
    result = app.invoke(
        {"messages": [{"role": "user", "content": "你好！"}], "mode": "chat", "context": {}},
        config
    )
    print(f"助手: {result['messages'][-1]['content']}")
    print(f"模式: {result['mode']}")
    print()

    # 回合 2：任务请求
    print("用户: 帮我查询明天的天气")
    result = app.invoke(
        {"messages": [{"role": "user", "content": "帮我查询明天的天气"}], "mode": "task", "context": {}},
        config
    )
    print(f"助手: {result['messages'][-1]['content']}")
    print(f"模式: {result['mode']}")
    print()

    # 回合 3：继续闲聊（检查记忆）
    print("用户: 谢谢！")
    result = app.invoke(
        {"messages": [{"role": "user", "content": "谢谢！"}], "mode": "chat", "context": {}},
        config
    )
    print(f"助手: {result['messages'][-1]['content']}")
    print()

    print("✅ Chatbot 对话机器人演示完成！")
    print("（注意：生产环境需要接入真实 LLM 和工具）")
