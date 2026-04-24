"""
LangGraph 7天系列 Day 9：Human-in-the-Loop 人机交互

本代码演示如何使用 interrupt() 中断执行，
等待人类确认后再继续：
- interrupt(): 中断执行
- Command(resume=...): 恢复执行
"""

from typing import Optional, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command


# ============ 1. 定义状态 ============
class ApprovalState(TypedDict):
    request: str
    approved: Optional[bool]
    result: str


# ============ 2. 定义节点 ============
def submit_request(state: ApprovalState) -> dict:
    """提交请求并中断，等待人工审批"""
    # interrupt() 会暂停执行，等待 resume
    response = interrupt(f"请审批请求: {state['request']}")
    return {"approved": response}


def process_approved(state: ApprovalState) -> dict:
    """处理已批准的请求"""
    return {"result": f"✅ 请求已批准: {state['request']}"}


def reject_request(state: ApprovalState) -> dict:
    """拒绝请求"""
    return {"result": f"❌ 请求已拒绝: {state['request']}"}


# ============ 3. 构建图 ============
def route_after_approval(state: ApprovalState) -> str:
    """根据人工审批结果路由到 approve / reject"""
    return "approve" if state.get("approved") else "reject"


memory = InMemorySaver()
builder = StateGraph(ApprovalState)
builder.add_node("submit", submit_request)
builder.add_node("approve", process_approved)
builder.add_node("reject", reject_request)
builder.add_edge(START, "submit")
builder.add_conditional_edges(
    "submit",
    route_after_approval,
    {"approve": "approve", "reject": "reject"},
)
builder.add_edge("approve", END)
builder.add_edge("reject", END)

app = builder.compile(checkpointer=memory)


# ============ 4. 执行流程 ============
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "approval-demo"}}

    print("=== Step 1: 提交请求（会中断）===")
    initial_result = app.invoke(
        {"request": "删除所有用户数据", "approved": None, "result": ""},
        config
    )
    print(f"中断结果: {initial_result}")

    # 判断是否需要人工审批
    if "__interrupt__" in initial_result:
        print()
        print("=== 人工审批阶段 ===")
        print("提示: 在实际应用中，用户会在 UI 界面审批")
        print("这里用 Command(resume=...) 模拟审批:")

        # 模拟用户批准：传 True 走 approve，传 False 走 reject
        approved = True
        resume_result = app.invoke(Command(resume=approved), config)
        print(f"审批后结果: {resume_result}")

    print()
    print("✅ Human-in-the-Loop 演示完成！")
