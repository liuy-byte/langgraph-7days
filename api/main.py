"""
LangGraph 14 天实战：RAG 知识库问答机器人

串联所有核心概念：
- StateGraph 状态机
- ToolNode 工具调用
- Checkpoint 持久化
- Conditional Edges 条件路由
- Streaming 流式输出
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode


# ============ 1. 定义状态 ============
class RAGState(TypedDict):
    question: str
    documents: list
    generation: str
    mode: str  # "local" / "search"


# ============ 2. 模拟工具 ============
def search_vectorstore(query: str) -> list:
    """模拟向量库检索"""
    docs = [
        "LangGraph 是一个用于构建状态化 AI 应用的框架",
        "LangChain 是 LangGraph 的前身，提供了丰富的组件",
        "Deep Agents 是基于 LangChain 的高级 Agent 封装"
    ]
    if "LangGraph" in query:
        return [docs[0]]
    elif "LangChain" in query:
        return [docs[1]]
    elif "Deep Agents" in query:
        return [docs[2]]
    return []


def search_web(query: str) -> str:
    """模拟联网搜索"""
    return f"[联网搜索结果] {query} 相关信息：这是一段关于 {query} 的最新内容..."


# ============ 3. 节点函数 ============
def retrieve(state: RAGState) -> dict:
    """检索文档"""
    docs = search_vectorstore(state["question"])
    return {"documents": docs}


def generate(state: RAGState) -> dict:
    """生成答案"""
    docs = state.get("documents", [])
    if docs:
        context = "\n".join(docs)
        answer = f"根据知识库：{context}"
    else:
        answer = "抱歉，知识库中没有找到相关信息。"
    return {"generation": answer}


def web_search(state: RAGState) -> dict:
    """联网搜索"""
    result = search_web(state["question"])
    return {"generation": result}


def route_mode(state: RAGState) -> Literal["generate", "web_search"]:
    """根据模式路由"""
    if state.get("mode") == "search":
        return "web_search"
    return "generate"


def route_docs(state: RAGState) -> Literal["generate", "web_search"]:
    """根据是否有文档路由"""
    if state.get("documents"):
        return "generate"
    return "web_search"


# ============ 4. 构建图 ============
memory = InMemorySaver()
builder = StateGraph(RAGState)

builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_node("web_search", web_search)

builder.add_edge(START, "retrieve")

# 检索后根据是否有文档路由：有则生成，没有则联网搜索
builder.add_conditional_edges(
    "retrieve",
    route_docs,
    {"generate": "generate", "web_search": "web_search"}
)

builder.add_edge("generate", END)
builder.add_edge("web_search", END)

app = builder.compile(checkpointer=memory)


# ============ 5. 流式对话接口 ============
def chat(question: str, thread_id: str = "default", mode: str = "local"):
    """流式对话"""
    config = {"configurable": {"thread_id": thread_id}}

    print(f"问题: {question}")
    print("答案: ", end="", flush=True)

    for chunk in app.stream(
        {"question": question, "documents": [], "generation": "", "mode": mode},
        config,
        stream_mode="values"
    ):
        if "generation" in chunk and chunk["generation"]:
            print(chunk["generation"], end="", flush=True)

    print()
    return chunk.get("generation", "") if chunk else ""


# ============ 6. CLI 交互 ============
def main():
    print("=" * 50)
    print("LangGraph 14 天实战 - RAG 知识库问答机器人")
    print("=" * 50)
    print()

    thread_id = "rag-bot-001"

    while True:
        try:
            user_input = input("👤 你: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit", "退出"]:
                print("再见！")
                break

            chat(user_input, thread_id=thread_id)
            print()

        except KeyboardInterrupt:
            print("\n再见！")
            break


if __name__ == "__main__":
    main()
