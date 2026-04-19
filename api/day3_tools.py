"""
LangGraph 7天系列 Day 3：工具调用

本代码演示：
- @tool 装饰器定义工具
- bind_tools 绑定工具到 LLM
- ToolNode 执行工具调用
"""

from typing import TypedDict
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END


# ============ 1. 定义工具 ============
@tool
def multiply(a: int, b: int) -> int:
    """将两个数字相乘"""
    return a * b


@tool
def get_weather(location: str) -> str:
    """获取指定位置的天气"""
    return f"{location} 今天晴天，25°C"


@tool
def search_web(query: str) -> str:
    """搜索网页获取信息"""
    return f"搜索 '{query}' 的结果：找到 10 条相关内容"


# ============ 2. 工具列表 ============
tools = [multiply, get_weather, search_web]

print("=== 可用工具 ===")
for t in tools:
    print(f"- {t.name}: {t.description}")


# ============ 3. 简单执行示例 ============
if __name__ == "__main__":
    # 直接调用工具
    print("\n=== 直接调用工具 ===")
    result = multiply.invoke({"a": 3, "b": 4})
    print(f"multiply(3, 4) = {result}")

    result = get_weather.invoke({"location": "北京"})
    print(f"get_weather('北京') = {result}")

    # 使用 ToolNode 执行工具调用
    print("\n=== ToolNode 执行 ===")
    from langgraph.prebuilt import ToolNode

    tool_node = ToolNode(tools)

    # 模拟 LLM 产生的工具调用
    from langchain_core.messages import AIMessage

    ai_message = AIMessage(
        content="",
        tool_calls=[
            {"name": "multiply", "args": {"a": 5, "b": 6}, "id": "1"}
        ]
    )

    result = tool_node.invoke({"messages": [ai_message]})
    print(f"ToolNode 执行结果: {result}")
