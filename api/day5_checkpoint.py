"""
LangGraph 7天系列 Day 5：Memory 与 Checkpoint

本代码演示：
- InMemorySaver 检查点持久化
- thread_id 会话管理
- get_state / put_state 手动控制
- 时间回溯 Replay
"""

from typing import Annotated, TypedDict
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
import operator


# ============ 1. 带 Checkpoint 的状态 ============
class CheckpointState(TypedDict):
    messages: Annotated[list, operator.add]
    counter: int


def increment(state: CheckpointState) -> dict:
    return {"counter": state["counter"] + 1}


def process(state: CheckpointState) -> dict:
    return {"messages": [f"处理 #{state['counter']}"]}


# ============ 2. 构建带 Checkpoint 的图 ============
def build_checkpoint_graph():
    builder = StateGraph(CheckpointState)
    builder.add_node("increment", increment)
    builder.add_node("process", process)
    builder.add_edge(START, "increment")
    builder.add_edge("increment", "process")
    builder.add_edge("process", END)

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
