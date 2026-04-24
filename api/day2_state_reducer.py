"""
LangGraph 7天系列 Day 2：状态管理与 Reducer

本代码演示：
- TypedDict 定义状态结构
- Annotated + reducer 函数实现状态合并
- add_messages 实现消息追加
"""

from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
import operator


# ============ 1. 带 Reducer 的状态定义 ============
class AgentState(TypedDict):
    """带 reducer 的状态：messages 使用 add_messages 追加"""
    messages: Annotated[list, operator.add]
    counter: int


def increment_counter(state: AgentState) -> dict:
    """节点：计数器 +1"""
    return {"counter": state["counter"] + 1}


def process_messages(state: AgentState) -> dict:
    """节点：处理消息"""
    return {"messages": [f"处理: {state['messages'][-1]}"]}


# ============ 2. 使用 add_messages ============
class ChatState(TypedDict):
    """聊天状态：消息自动追加（官方 add_messages 支持按 message ID 去重/覆盖）"""
    messages: Annotated[list, add_messages]


def chat_node(state: ChatState) -> dict:
    """简单聊天节点"""
    last = state["messages"][-1]
    last_text = last.content if hasattr(last, "content") else str(last)
    return {"messages": [AIMessage(content=f"回复: {last_text}")]}


# ============ 3. 构建并执行图 ============
if __name__ == "__main__":
    # 示例 1：计数器
    print("=== 示例 1：计数器 ===")
    builder = StateGraph(AgentState)
    builder.add_node("increment", increment_counter)
    builder.add_edge(START, "increment")
    builder.add_edge("increment", END)
    graph = builder.compile()

    result = graph.invoke({"messages": [], "counter": 0})
    print(f"计数器结果: {result}")  # counter 应该是 1

    # 示例 2：消息追加
    print("\n=== 示例 2：消息追加 ===")
    builder2 = StateGraph(ChatState)
    builder2.add_node("chat", chat_node)
    builder2.add_edge(START, "chat")
    builder2.add_edge("chat", END)
    graph2 = builder2.compile()

    result2 = graph2.invoke({"messages": [HumanMessage(content="你好")]})
    print(f"消息追加结果: {result2}")  # messages 应该有两条
