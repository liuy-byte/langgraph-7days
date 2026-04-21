"""
LangGraph 7天系列 Day 7：生产环境部署

本代码演示：
- PostgresSaver 持久化检查点
- LangGraph Server 部署
- 流式输出 stream_mode
- 错误恢复和重试机制
"""

from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
import operator


# ============ 1. 生产级状态定义 ============
class ProductionState(TypedDict):
    messages: Annotated[list, operator.add]
    status: str


def process_node(state: ProductionState) -> dict:
    """处理节点"""
    return {
        "messages": [f"处理: {state['messages'][-1]}"],
        "status": "completed"
    }


# ============ 2. 构建生产级图 ============
def build_production_graph():
    """构建生产级应用图"""
    builder = StateGraph(ProductionState)
    builder.add_node("process", process_node)
    builder.add_edge(START, "process")
    builder.add_edge("process", END)

    # 注意：生产环境应使用 PostgresSaver 或 RedisSaver
    # 这里演示结构，生产环境配置见下方注释
    return builder.compile()


# ============ 3. 流式输出示例 ============
def stream_example():
    """流式输出示例"""
    graph = build_production_graph()

    print("=== 流式输出 ===")
    for chunk in graph.stream(
        {"messages": ["开始处理"], "status": "pending"},
        stream_mode="values"
    ):
        print(f"Chunk: {chunk}")


# ============ 4. PostgresSaver 配置示例 ============
def postgres_saver_example():
    """
    生产环境使用 PostgresSaver:

    from langgraph.checkpoint.postgres import PostgresSaver

    # 配置数据库连接
    saver = PostgresSaver.from_conn_string(
        "postgresql://user:password@localhost:5432/langgraph"
    )
    saver.setup()  # 初始化表结构

    # 编译图时传入检查点
    graph = builder.compile(checkpointer=saver)
    """
    print("PostgresSaver 配置示例已备注在代码中")


# ============ 5. RedisSaver 配置示例 ============
def redis_saver_example():
    """
    生产环境使用 RedisSaver:

    from langgraph.checkpoint.redis import RedisSaver

    saver = RedisSaver.from_url("redis://localhost:6379/0")

    graph = builder.compile(checkpointer=saver)
    """
    print("RedisSaver 配置示例已备注在代码中")


# ============ 6. 执行示例 ============
if __name__ == "__main__":
    print("=== 生产环境部署示例 ===")
    graph = build_production_graph()

    # 普通执行
    result = graph.invoke({"messages": ["测试消息"], "status": "pending"})
    print(f"执行结果: {result}")

    # 流式执行
    stream_example()

    # 检查点配置备注
    postgres_saver_example()
    redis_saver_example()
