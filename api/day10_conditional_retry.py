"""
LangGraph 7天系列 Day 10：Conditional Edges 条件边 + Error Handling 错误处理

本代码演示：
- add_conditional_edges: 动态路由
- 错误重试机制
- Router 函数
"""

from typing import Literal, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


# ============ 1. 定义状态 ============
class RoutingState(TypedDict):
    input: str
    route: str
    attempts: int


# ============ 2. 定义节点 ============
def process_urgent(state: RoutingState) -> dict:
    """处理紧急请求"""
    return {"route": "urgent_handler"}


def process_normal(state: RoutingState) -> dict:
    """处理普通请求"""
    return {"route": "normal_handler"}


def fallback(state: RoutingState) -> dict:
    """兜底处理"""
    return {"route": "fallback"}


# ============ 3. Router 函数（条件边的核心） ============
def router(state: RoutingState) -> Literal["process_urgent", "process_normal", "fallback"]:
    """
    根据输入内容决定路由
    这是 add_conditional_edges 的核心
    """
    if "紧急" in state["input"] or "urgent" in state["input"].lower():
        return "process_urgent"
    elif "普通" in state["input"] or "normal" in state["input"].lower():
        return "process_normal"
    return "fallback"


# ============ 4. 构建带条件边的图 ============
memory = InMemorySaver()
builder = StateGraph(RoutingState)

builder.add_node("process_urgent", process_urgent)
builder.add_node("process_normal", process_normal)
builder.add_node("fallback", fallback)

# 从 START 开始，使用条件边动态路由
builder.add_conditional_edges(
    START,
    router,  # 路由函数
    {
        "process_urgent": "process_urgent",
        "process_normal": "process_normal",
        "fallback": "fallback"
    }
)

# 所有节点都可以结束
builder.add_edge("process_urgent", END)
builder.add_edge("process_normal", END)
builder.add_edge("fallback", END)

app = builder.compile(checkpointer=memory)


# ============ 5. 错误重试示例 ============
class RetryState(TypedDict):
    value: int
    error_count: int


def might_fail(state: RetryState) -> dict:
    """可能失败的节点"""
    if state["value"] < 0:
        raise ValueError("值不能为负数")
    return {"value": state["value"] * 2}


def retry_node(state: RetryState) -> dict:
    """重试处理"""
    return {"error_count": state["error_count"] + 1}


retry_builder = StateGraph(RetryState)
retry_builder.add_node("action", might_fail)
retry_builder.add_node("retry", retry_node)
retry_builder.add_edge(START, "action")
retry_builder.add_edge("action", END)

retry_app = retry_builder.compile()


# ============ 6. 执行演示 ============
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "routing-demo"}}

    print("=== 条件边路由演示 ===")
    print()

    # 测试紧急请求
    result = app.invoke({"input": "紧急：系统故障", "route": "", "attempts": 0}, config)
    print(f"输入 '紧急：系统故障' -> 路由到: {result['route']}")

    # 测试普通请求
    result = app.invoke({"input": "normal request", "route": "", "attempts": 0}, config)
    print(f"输入 'normal request' -> 路由到: {result['route']}")

    # 测试兜底
    result = app.invoke({"input": "其他请求", "route": "", "attempts": 0}, config)
    print(f"输入 '其他请求' -> 路由到: {result['route']}")

    print()
    print("✅ Conditional Edges + Error Handling 演示完成！")
