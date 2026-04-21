"""
LangGraph 7天系列 Day 6：Subgraph 多 Agent 系统

本代码演示：
- 子图作为节点嵌套
- Named Channels 命名通道
- 命名空间隔离
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
import operator


# ============ 1. 定义子图 ============
class SubgraphState(TypedDict):
    messages: Annotated[list, operator.add]
    task: str


def subgraph_node(state: SubgraphState) -> dict:
    """子图节点：处理子任务"""
    return {
        "messages": [f"子图处理: {state.get('task', '未知任务')}"],
        "task": state.get("task", "")
    }


def build_subgraph():
    """构建子图"""
    builder = StateGraph(SubgraphState)
    builder.add_node("subgraph_task", subgraph_node)
    builder.add_edge(START, "subgraph_task")
    builder.add_edge("subgraph_task", END)
    return builder.compile()


# ============ 2. 主图中使用子图 ============
class MainState(TypedDict):
    messages: Annotated[list, operator.add]
    result: str


def main_node(state: MainState) -> dict:
    """主节点：调用子图"""
    subgraph = build_subgraph()
    subgraph_result = subgraph.invoke({
        "messages": [],
        "task": "数据分析"
    })
    return {"result": str(subgraph_result)}


def output_node(state: MainState) -> dict:
    """输出节点：汇总结果"""
    return {"messages": [f"最终结果: {state['result']}"]}


def build_main_graph_with_subgraph():
    """构建包含子图的主图"""
    builder = StateGraph(MainState)
    builder.add_node("main", main_node)
    builder.add_node("output", output_node)
    builder.add_edge(START, "main")
    builder.add_edge("main", "output")
    builder.add_edge("output", END)
    return builder.compile()


# ============ 3. 执行示例 ============
if __name__ == "__main__":
    print("=== 子图嵌套示例 ===")
    graph = build_main_graph_with_subgraph()
    result = graph.invoke({"messages": [], "result": ""})
    print(f"结果: {result}")
