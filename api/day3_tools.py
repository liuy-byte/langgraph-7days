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


# ============ 3. 简单执行示例 ============
if __name__ == "__main__":
    print("=== 可用工具 ===")
    for t in tools:
        print(f"- {t.name}: {t.description}")

    # 直接调用工具
    print("\n=== 直接调用工具 ===")
    result = multiply.invoke({"a": 3, "b": 4})
    print(f"multiply(3, 4) = {result}")

    result = get_weather.invoke({"location": "北京"})
    print(f"get_weather('北京') = {result}")

    # 使用 ToolNode 执行工具调用（需要配合 Agent 使用）
    print("\n=== ToolNode 使用示例 ===")
    print("ToolNode 需要配合 create_react_agent 使用，详见 Day 4")
    print("直接调用工具：multiply.invoke({'a': 5, 'b': 6}) =", multiply.invoke({"a": 5, "b": 6}))
