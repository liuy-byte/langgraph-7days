"""
LangGraph 7天系列 Day 4：Agent 开发 - ReAct 循环

本代码演示：
- should_continue 条件边函数
- 思考 → 行动 → 观察 循环
- create_react_agent 预建 Agent
"""

from typing import TypedDict, Literal
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END, MessagesState


# ============ 1. 简单 Agent 循环 ============
class AgentState(MessagesState):
    """带消息历史的 Agent 状态"""
    next_action: str


def should_continue(state: AgentState) -> Literal["action", "end"]:
    """决定是否继续：检查最后一条消息是否有 tool_calls"""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "action"
    return "end"


def reasoning_node(state: AgentState) -> dict:
    """推理节点：思考下一步行动"""
    return {"messages": [AIMessage(content="让我思考一下...")]}


def action_node(state: AgentState) -> dict:
    """行动节点：执行工具调用"""
    return {"messages": [AIMessage(content="执行工具...")]}


# ============ 2. 构建条件边图 ============
def build_conditional_graph():
    """构建带条件边的 Agent 图"""
    builder = StateGraph(AgentState)
    builder.add_node("reasoning", reasoning_node)
    builder.add_node("action", action_node)

    builder.add_edge(START, "reasoning")
    builder.add_conditional_edges(
        "reasoning",
        should_continue,
        {
            "action": "action",
            "end": END
        }
    )
    builder.add_edge("action", END)

    return builder.compile()


# ============ 3. 使用 create_react_agent ============
def build_react_agent(model, tools, checkpointer=None):
    """使用预建的 ReAct Agent"""
    from langgraph.prebuilt import create_react_agent

    return create_react_agent(
        model,
        tools,
        checkpointer=checkpointer,
        prompt="你是一个乐于助人的 AI 助手"
    )


# ============ 4. 执行示例 ============
if __name__ == "__main__":
    # 示例 1：条件边图
    print("=== 示例 1：条件边 Agent ===")
    graph = build_conditional_graph()
    result = graph.invoke({"messages": [HumanMessage(content="你好")]})
    print(f"执行结果: {result}")

    # 示例 2：ReAct Agent（需要配置 model 和 tools）
    print("\n=== 示例 2：ReAct Agent ===")
    print("请配置 model 和 tools 后使用 build_react_agent() 创建")
