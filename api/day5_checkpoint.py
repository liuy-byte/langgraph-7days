"""
LangGraph 7天系列 Day 5：Memory 与 Checkpoint

本代码演示：
- InMemorySaver 检查点持久化
- thread_id 会话管理
- get_state / put_state 手动控制
- 时间回溯 Replay
"""

from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
import operator


# ============ 1. 带 Checkpoint 的状态 ============
class ConversationState(TypedDict):
    messages: Annotated[list, operator.add]
    counter: int


def chat_node(state: ConversationState) -> dict:
    return {
        "messages": [f"回复: {state['messages'][-1] if state['messages'] else '你好'}"],
        "counter": state["counter"] + 1
    }


# ============ 2. 构建带 Checkpoint 的图 ============
def build_checkpoint_graph():
    builder = StateGraph(ConversationState)
    builder.add_node("chat", chat_node)
    builder.add_edge(START, "chat")
    builder.add_edge("chat", END)

    # 使用 InMemorySaver 作为检查点
    memory = InMemorySaver()
    return builder.compile(checkpointer=memory), memory


# ============ 3. 执行和检查状态 ============
if __name__ == "__main__":
    graph, memory = build_checkpoint_graph()

    # 第一次执行
    print("=== 第一次执行 ===")
    config = {"configurable": {"thread_id": "session-1"}}
    result = graph.invoke({"messages": [], "counter": 0}, config)
    print(f"结果: {result}")

    # 获取当前状态
    print("\n=== 获取状态快照 ===")
    snapshot = graph.get_state(config)
    print(f"当前状态: {snapshot.values}")
    print(f"下一个节点: {snapshot.next}")

    # 列出所有检查点
    print("\n=== 检查点历史 ===")
    for checkpoint in memory.list(config):
        checkpoint_id = checkpoint.config["configurable"].get("checkpoint_id", "unknown")
        print(f"- checkpoint_id: {checkpoint_id}")

    # 第二次执行（从断点继续）
    print("\n=== 第二次执行（继续） ===")
    result2 = graph.invoke({"messages": [], "counter": 5}, config)
    print(f"结果: {result2}")
