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
    from langgraph.graph.message import add_messages as official_add_messages
    from langchain_core.messages import HumanMessage, AIMessage

    # 验证计数器：operator.add reducer
    builder = StateGraph(AgentState)
    builder.add_node("increment", increment_counter)
    builder.add_edge(START, "increment")
    builder.add_edge("increment", END)
    graph = builder.compile()
    result = graph.invoke({"messages": [], "counter": 0})
    assert result["counter"] == 1

    # 验证消息追加：使用官方 add_messages reducer（而非自定义）
    import day2_state_reducer
    assert day2_state_reducer.add_messages is official_add_messages, \
        "Day 2 必须使用 langgraph.graph.message.add_messages，而不是自定义函数"

    builder2 = StateGraph(ChatState)
    builder2.add_node("chat", chat_node)
    builder2.add_edge(START, "chat")
    builder2.add_edge("chat", END)
    graph2 = builder2.compile()
    result2 = graph2.invoke({"messages": [HumanMessage(content="你好")]})
    assert len(result2["messages"]) == 2
    assert isinstance(result2["messages"][-1], AIMessage)
    print("✓ Day 2 测试通过")


def test_day4_agent():
    """Day 4: ReAct Agent 条件边与消息类型"""
    from day4_agent import build_conditional_graph, reasoning_node, action_node
    from langchain_core.messages import AIMessage, HumanMessage

    # 推理/行动节点应返回 AIMessage（AI 产出，而非人类消息）
    r1 = reasoning_node({"messages": []})
    r2 = action_node({"messages": []})
    assert isinstance(r1["messages"][0], AIMessage)
    assert isinstance(r2["messages"][0], AIMessage)

    # 条件图：无 tool_calls 的消息 → 走 end 分支
    graph = build_conditional_graph()
    result = graph.invoke({"messages": [HumanMessage(content="你好")]})
    assert "messages" in result

    # 验证 create_react_agent 来自正确的包
    import inspect
    from day4_agent import build_react_agent
    src = inspect.getsource(build_react_agent)
    assert "langgraph.prebuilt" in src, "必须使用 langgraph.prebuilt.create_react_agent"
    assert "create_react_agent" in src
    print("✓ Day 4 测试通过")


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


def test_day9_hitl_approve_and_reject():
    """Day 9: Human-in-the-Loop 必须支持批准/拒绝两条分支"""
    from day9_hitl import app
    from langgraph.types import Command

    # 批准路径
    cfg_ok = {"configurable": {"thread_id": "hitl-approve"}}
    initial = app.invoke({"request": "批准测试", "approved": None, "result": ""}, cfg_ok)
    assert "__interrupt__" in initial
    approved = app.invoke(Command(resume=True), cfg_ok)
    assert approved["result"].startswith("✅")

    # 拒绝路径：必须真的走 reject 节点
    cfg_no = {"configurable": {"thread_id": "hitl-reject"}}
    initial = app.invoke({"request": "拒绝测试", "approved": None, "result": ""}, cfg_no)
    assert "__interrupt__" in initial
    rejected = app.invoke(Command(resume=False), cfg_no)
    assert rejected["result"].startswith("❌"), \
        f"拒绝路径未生效（reject 节点不可达），实际结果: {rejected['result']}"
    print("✓ Day 9 测试通过")


def test_day13_decide_next():
    """Day 13: decide_next 必须被条件边真正使用"""
    from day13_code_assistant import decide_next, app

    # 无错误 → finalize
    assert decide_next({"error": "no", "iterations": 1, "task": "", "code": "", "result": ""}) == "finalize"
    # 达到迭代上限 → finalize
    assert decide_next({"error": "yes", "iterations": 3, "task": "", "code": "", "result": ""}) == "finalize"
    # 有错但未到上限 → fix
    assert decide_next({"error": "yes", "iterations": 1, "task": "", "code": "", "result": ""}) == "fix"

    # 端到端：简单任务应产生 result
    config = {"configurable": {"thread_id": "day13-test"}}
    result = app.invoke({
        "task": "Hello World", "code": "", "error": "",
        "iterations": 0, "result": "",
    }, config)
    assert result["result"].startswith("最终代码:")
    print("✓ Day 13 测试通过")


if __name__ == "__main__":
    print("运行 LangGraph 7天系列测试...\n")

    test_day1_stategraph()
    test_day2_state_reducer()
    test_day3_tools()
    test_day4_agent()
    test_day5_checkpoint()
    test_day6_subgraph()
    test_day7_deploy()
    test_day9_hitl_approve_and_reject()
    test_day13_decide_next()

    print("\n所有测试通过！✓")
