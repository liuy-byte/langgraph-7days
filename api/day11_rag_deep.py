"""
LangGraph 7天系列 Day 11：RAG 深入实战

本代码演示完整的 RAG 工作流：
- 检索 -> 文档评分 -> 生成
- 条件边控制流程
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


# ============ 1. 定义 RAG 状态 ============
class RAGState(TypedDict):
    question: str
    documents: list
    generation: str
    has_docs: bool  # 用于条件边路由


# ============ 2. 定义节点 ============
def retrieve(state: RAGState) -> dict:
    """检索相关文档（模拟）"""
    docs = [
        "LangGraph 是一个用于构建状态化、多步骤 AI 应用的框架",
        "LangChain 是 LangGraph 的前身，提供了丰富的组件库",
    ]
    if "LangGraph" in state["question"] or "LangChain" in state["question"]:
        has_docs = True
        docs_result = [docs[0] if "LangGraph" in state["question"] else docs[1]]
    else:
        has_docs = False
        docs_result = []
    return {"documents": docs_result, "has_docs": has_docs}


def generate(state: RAGState) -> dict:
    """生成答案"""
    doc = state["documents"][0] if state["documents"] else "未找到相关文档"
    return {"generation": f"根据文档内容：{doc}"}


def fallback(state: RAGState) -> dict:
    """降级处理"""
    return {"generation": "抱歉，我无法找到相关文档来回答这个问题。"}


# ============ 3. Router 函数（用于条件边） ============
def route_based_on_docs(state: RAGState) -> Literal["generate", "fallback"]:
    """根据是否有文档决定路由"""
    if state["has_docs"]:
        return "generate"
    return "fallback"


# ============ 4. 构建 RAG 图 ============
memory = InMemorySaver()
builder = StateGraph(RAGState)

builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_node("fallback", fallback)

# 边
builder.add_edge(START, "retrieve")

# 条件边：检索后根据是否有文档决定下一步
builder.add_conditional_edges(
    "retrieve",
    route_based_on_docs,
    {"generate": "generate", "fallback": "fallback"}
)

builder.add_edge("generate", END)
builder.add_edge("fallback", END)

app = builder.compile(checkpointer=memory)


# ============ 5. 执行演示 ============
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "rag-demo"}}

    print("=== RAG 深入实战演示 ===")
    print()

    # 测试 1：成功检索
    print("问题: LangGraph 是什么？")
    result = app.invoke({
        "question": "LangGraph 是什么",
        "documents": [],
        "generation": "",
        "has_docs": False
    }, config)
    print(f"最终答案: {result['generation']}")
    print()

    # 测试 2：检索失败
    print("问题: Kubernetes 是什么？")
    result = app.invoke({
        "question": "Kubernetes 是什么",
        "documents": [],
        "generation": "",
        "has_docs": False
    }, config)
    print(f"最终答案: {result['generation']}")

    print()
    print("✅ RAG 深入实战演示完成！")
