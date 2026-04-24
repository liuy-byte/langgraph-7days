"""
LangGraph 7天系列 实战项目：RAG Agent

结合向量检索和 Agent，实现自然语言问答
"""

from typing import TypedDict, Annotated
import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
import operator


# ============ 1. 文档处理工具 ============
@tool
def retrieve_documents(query: str) -> str:
    """根据查询从知识库中检索相关文档

    返回与查询最相关的文档内容。
    """
    # 模拟知识库检索
    docs = [
        "LangGraph 是一个用于构建状态化、多步骤 LLM 应用的框架",
        "StateGraph 是 LangGraph 的核心，用于定义工作流",
        "Checkpoint 用于保存和恢复状态"
    ]
    # 简单关键词匹配
    relevant = [d for d in docs if any(k in d for k in query.split())]
    return "\n".join(relevant) if relevant else "未找到相关文档"


@tool
def search_web(query: str) -> str:
    """搜索互联网获取实时信息"""
    return f"搜索 '{query}' 的结果：这是搜索结果摘要..."


# ============ 2. 状态定义 ============
class RAGState(TypedDict):
    question: str
    context: str
    answer: str
    sources: Annotated[list, operator.add]


# ============ 3. RAG Agent 构建 ============
def build_rag_agent():
    """构建 RAG Agent"""
    api_key = os.environ.get("SILICONFLOW_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "请设置环境变量 SILICONFLOW_API_KEY\n"
            "  export SILICONFLOW_API_KEY=sk-your-key-here"
        )
    model = ChatOpenAI(
        model=os.environ.get("MODEL_NAME", "Pro/MiniMaxAI/MiniMax-M2.5"),
        base_url="https://api.siliconflow.cn/v1",
        api_key=api_key,
    )

    tools = [retrieve_documents, search_web]
    memory = InMemorySaver()

    agent = create_react_agent(model, tools, checkpointer=memory)

    return agent


# ============ 4. 执行示例 ============
if __name__ == "__main__":
    print("=== RAG Agent 实战 ===")
    agent = build_rag_agent()
    config = {"configurable": {"thread_id": "rag-1"}}

    # 问关于 LangGraph 的问题
    result = agent.invoke({
        "messages": [{"role": "user", "content": "LangGraph 的核心是什么？"}]
    }, config)

    print("Q: LangGraph 的核心是什么？")
    print("A:", result["messages"][-1].content)
