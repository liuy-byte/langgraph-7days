"""
LangGraph 7天系列 Day 8：Streaming 流式输出

本代码演示 LangGraph 的三种流式输出模式：
- stream_mode="values": 流式输出完整状态
- stream_mode="updates": 流式输出节点更新
- stream_mode="custom": 流式输出自定义内容
"""

from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver


# ============ 1. 定义状态 ============
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]


# ============ 2. 定义节点 ============
def chatbot(state: ChatState) -> dict:
    """模拟聊天机器人，返回一条消息"""
    return {"messages": [{"role": "assistant", "content": "你好！我是 LangGraph 流式助手。"}]}


def process(state: ChatState) -> dict:
    """处理消息"""
    return {"messages": [{"role": "system", "content": "处理完成"}]}


# ============ 3. 构建图（带 Checkpointer 以支持流式） ============
memory = InMemorySaver()
builder = StateGraph(ChatState)
builder.add_node("chatbot", chatbot)
builder.add_node("process", process)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", "process")
builder.add_edge("process", END)
app = builder.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "stream-demo"}}


# ============ 4. 三种流式模式 ============
if __name__ == "__main__":
    input_data = {"messages": [{"role": "user", "content": "你好"}]}

    print("=" * 50)
    print("模式 1: stream_mode='values'（流式完整状态）")
    print("=" * 50)
    for chunk in app.stream(input_data, config, stream_mode="values"):
        print(f"  {chunk}")

    print()
    print("=" * 50)
    print("模式 2: stream_mode='updates'（流式节点更新）")
    print("=" * 50)
    for chunk in app.stream(input_data, config, stream_mode="updates"):
        print(f"  节点: {list(chunk.keys())}")

    print()
    print("=" * 50)
    print("模式 3: stream_mode=['values', 'updates']（同时输出）")
    print("=" * 50)
    for chunk in app.stream(input_data, config, stream_mode=["values", "updates"]):
        print(f"  {chunk}")

    print()
    print("✅ 流式输出演示完成！")
