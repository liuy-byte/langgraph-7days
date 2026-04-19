"""
LangGraph 7天系列 Day 1：StateGraph 核心概念

本代码演示 LangGraph 的核心三要素：
- StateGraph：状态图容器
- Node：处理节点
- Edge：节点连接边
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# ============ 1. 定义状态结构 ============
class WorkflowState(TypedDict):
    """简单的工作流状态，只包含一条消息"""
    message: str


# ============ 2. 定义节点函数 ============
def first_node(state: WorkflowState) -> dict:
    """第一个节点：处理输入"""
    return {"message": f"处理: {state['message']}"}


def second_node(state: WorkflowState) -> dict:
    """第二个节点：生成输出"""
    return {"message": f"输出: {state['message']}"}


# ============ 3. 构建图 ============
def build_graph():
    """构建并编译状态图"""
    # 创建 StateGraph，指定状态类型
    builder = StateGraph(WorkflowState)

    # 添加节点
    builder.add_node("first", first_node)
    builder.add_node("second", second_node)

    # 添加边：START -> first -> second -> END
    builder.add_edge(START, "first")
    builder.add_edge("first", "second")
    builder.add_edge("second", END)

    # 编译图
    return builder.compile()


# ============ 4. 执行图 ============
if __name__ == "__main__":
    # 构建图
    graph = build_graph()

    # 查看图的结构
    print("=== LangGraph 状态图 ===")
    print(f"节点: {graph.nodes.keys()}")
    print()

    # 执行图
    result = graph.invoke({"message": "Hello LangGraph!"})
    print(f"执行结果: {result}")
