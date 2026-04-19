"""
LangGraph 7天系列 实战项目：多 Agent 协作系统

一个协调器 Agent 调度多个专业 Agent
"""

from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import operator


# ============ 1. 专业 Agent 工具 ============
@tool
def research_topic(topic: str) -> str:
    """研究主题，返回相关信息"""
    return f"关于 {topic} 的研究资料：这是一个研究摘要..."


@tool
def write_content(topic: str, style: str) -> str:
    """根据主题和风格撰写内容"""
    return f"以 {style} 风格撰写的关于 {topic} 的内容..."


@tool
def review_content(content: str) -> str:
    """审核内容，返回改进建议"""
    return f"审核意见：内容整体良好，建议在第三段添加具体案例"


# ============ 2. 状态定义 ============
class MultiAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    task: str
    research_result: str
    draft_content: str
    review_result: str
    final_content: str


# ============ 3. 各节点定义 ============
def coordinator_node(state: MultiAgentState) -> dict:
    """协调器：分析任务并分发"""
    task = state["task"]
    return {
        "messages": [f"任务已接收：{task}，正在分发..."]
    }


def researcher_node(state: MultiAgentState) -> dict:
    """研究 Agent：收集信息"""
    result = research_topic.invoke({"topic": state["task"]})
    return {
        "research_result": result,
        "messages": ["研究完成"]
    }


def writer_node(state: MultiAgentState) -> dict:
    """写作 Agent：撰写内容"""
    result = write_content.invoke({
        "topic": state["task"],
        "style": "专业简洁"
    })
    return {
        "draft_content": result,
        "messages": ["初稿完成"]
    }


def reviewer_node(state: MultiAgentState) -> dict:
    """审核 Agent：审核内容"""
    result = review_content.invoke({"content": state["draft_content"]})
    return {
        "review_result": result,
        "messages": ["审核完成"]
    }


def finalizer_node(state: MultiAgentState) -> dict:
    """最终整理"""
    return {
        "final_content": f"{state['draft_content']}\n\n---\n审核意见：{state['review_result']}",
        "messages": ["任务完成"]
    }


# ============ 4. 构建多 Agent 系统 ============
def build_multi_agent_system():
    """构建多 Agent 协作系统"""
    builder = StateGraph(MultiAgentState)

    # 添加节点
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("writer", writer_node)
    builder.add_node("reviewer", reviewer_node)
    builder.add_node("finalizer", finalizer_node)

    # 定义流程
    builder.add_edge(START, "coordinator")
    builder.add_edge("coordinator", "researcher")
    builder.add_edge("researcher", "writer")
    builder.add_edge("writer", "reviewer")
    builder.add_edge("reviewer", "finalizer")
    builder.add_edge("finalizer", END)

    return builder.compile()


# ============ 5. 执行示例 ============
if __name__ == "__main__":
    print("=== 多 Agent 协作实战 ===")
    graph = build_multi_agent_system()

    result = graph.invoke({
        "messages": [],
        "task": "LangGraph 多 Agent 系统",
        "research_result": "",
        "draft_content": "",
        "review_result": "",
        "final_content": ""
    })

    print("\n=== 最终输出 ===")
    print(result["final_content"])
