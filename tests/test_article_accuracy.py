"""
LangGraph 7天系列测试：验证代码示例准确性

测试每个 Day 的代码示例能否正确执行
"""

import sys
from pathlib import Path

# 添加 api 目录到路径
api_dir = Path(__file__).parent.parent / "api"
sys.path.insert(0, str(api_dir))


def test_day1_stategraph():
    """Day 1: StateGraph 核心概念"""
    from day1_stategraph import build_graph

    graph = build_graph()
    result = graph.invoke({"message": "Hello!"})
    assert "message" in result
    print("✓ Day 1 测试通过")


def test_day2_state_reducer():
    """Day 2: 状态管理与 Reducer"""
    from day2_state_reducer import AgentState, ChatState, increment_counter, chat_node
    from langgraph.graph import StateGraph, START, END

    # 验证计数器：operator.add reducer
    builder = StateGraph(AgentState)
    builder.add_node("increment", increment_counter)
    builder.add_edge(START, "increment")
    builder.add_edge("increment", END)
    graph = builder.compile()
    result = graph.invoke({"messages": [], "counter": 0})
    assert result["counter"] == 1

    # 验证消息追加：自定义 add_messages reducer
    builder2 = StateGraph(ChatState)
    builder2.add_node("chat", chat_node)
    builder2.add_edge(START, "chat")
    builder2.add_edge("chat", END)
    graph2 = builder2.compile()
    result2 = graph2.invoke({"messages": ["你好"]})
    assert len(result2["messages"]) == 2
    print("✓ Day 2 测试通过")


def test_day3_tools():
    """Day 3: 工具调用"""
    from day3_tools import multiply, get_weather, tools

    assert len(tools) == 3
    result = multiply.invoke({"a": 3, "b": 4})
    assert result == 12
    print("✓ Day 3 测试通过")


def test_day5_checkpoint():
    """Day 5: Memory 与 Checkpoint"""
    from day5_checkpoint import build_checkpoint_graph

    graph, memory = build_checkpoint_graph()
    config = {"configurable": {"thread_id": "test"}}
    result = graph.invoke({"messages": [], "counter": 0}, config)
    assert result["counter"] == 1
    print("✓ Day 5 测试通过")


def test_day6_subgraph():
    """Day 6: Subgraph 多 Agent"""
    from day6_subgraph import build_main_graph_with_subgraph

    graph = build_main_graph_with_subgraph()
    result = graph.invoke({"messages": [], "result": ""})
    assert "result" in result
    print("✓ Day 6 测试通过")


def test_day7_deploy():
    """Day 7: 生产部署"""
    from day7_deploy import build_production_graph

    graph = build_production_graph()
    result = graph.invoke({"messages": ["测试"], "status": "pending"})
    assert result["status"] == "completed"
    print("✓ Day 7 测试通过")


if __name__ == "__main__":
    print("运行 LangGraph 7天系列测试...\n")

    test_day1_stategraph()
    test_day2_state_reducer()
    test_day3_tools()
    test_day5_checkpoint()
    test_day6_subgraph()
    test_day7_deploy()

    print("\n所有测试通过！✓")
