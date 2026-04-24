"""
LangGraph 7天系列 Day 13：Code Assistant 编程助手

本代码演示如何使用 LangGraph 构建代码助手：
- 代码生成
- 语法检查
- 执行测试
- 迭代优化
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


# ============ 1. 定义状态 ============
class CodeAssistantState(TypedDict):
    task: str
    code: str
    error: str  # "yes" / "no"
    iterations: int
    result: str


# ============ 2. 定义节点 ============
def generate_code(state: CodeAssistantState) -> dict:
    """生成代码（模拟）"""
    task = state["task"]

    # 简单模拟：根据任务生成代码
    if "hello" in task.lower():
        code = 'print("Hello, World!")'
    elif "加法" in task or "add" in task.lower():
        code = "def add(a, b):\n    return a + b"
    else:
        code = "# TODO: 实现功能"

    return {"code": code, "iterations": state["iterations"] + 1}


def check_code(state: CodeAssistantState) -> dict:
    """检查代码（模拟语法检查）"""
    code = state["code"]

    # 简单检查
    if "print" not in code and "def " not in code:
        return {"error": "yes"}

    # 模拟执行
    try:
        exec(code)
        return {"error": "no"}
    except Exception as e:
        return {"error": "yes", "result": f"执行错误: {e}"}


def fix_code(state: CodeAssistantState) -> dict:
    """修复代码问题（模拟）"""
    code = state["code"]

    if "print" not in code and "def " not in code:
        code = 'print("Hello from fixed code!")'

    return {"code": code, "iterations": state["iterations"] + 1}


def decide_next(state: CodeAssistantState) -> Literal["finalize", "fix"]:
    """根据检查结果决定下一步：完成 or 修复重试"""
    if state["error"] == "no" or state["iterations"] >= 3:
        return "finalize"
    return "fix"


def finalize(state: CodeAssistantState) -> dict:
    """完成代码生成"""
    return {"result": f"最终代码:\n{state['code']}"}


# ============ 3. 构建代码助手图 ============
memory = InMemorySaver()
builder = StateGraph(CodeAssistantState)

builder.add_node("generate", generate_code)
builder.add_node("check", check_code)
builder.add_node("fix", fix_code)
builder.add_node("finalize", finalize)

builder.add_edge(START, "generate")
builder.add_edge("generate", "check")

# 条件边：根据检查结果决定
builder.add_conditional_edges(
    "check",
    decide_next,
    {"finalize": "finalize", "fix": "fix"},
)

builder.add_edge("fix", "check")  # 修复后重新检查
builder.add_edge("finalize", END)

app = builder.compile(checkpointer=memory)


# ============ 4. 执行演示 ============
if __name__ == "__main__":
    print("=== Code Assistant 编程助手演示 ===")
    print()

    config = {"configurable": {"thread_id": "code-assistant-demo"}}

    # 测试 1：简单任务
    print("任务: 写一个 Hello World 程序")
    result = app.invoke({
        "task": "Hello World 程序",
        "code": "",
        "error": "",
        "iterations": 0,
        "result": ""
    }, config)
    print(f"最终结果:\n{result['result']}")
    print()

    # 测试 2：需要修复的任务
    print("任务: 实现一个加法函数")
    result = app.invoke({
        "task": "实现加法函数",
        "code": "",
        "error": "",
        "iterations": 0,
        "result": ""
    }, config)
    print(f"最终结果:\n{result['result']}")

    print()
    print("✅ Code Assistant 编程助手演示完成！")
    print("（注意：生产环境需要接入真实 LLM 进行代码生成）")
