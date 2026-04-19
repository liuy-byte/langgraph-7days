"""
LangGraph 7天系列 实战项目：SQL Agent

自然语言查询数据库
"""

from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_agent
from langgraph.checkpoint.memory import InMemorySaver


# ============ 1. 数据库工具 ============
@tool
def query_database(sql: str) -> str:
    """执行 SQL 查询并返回结果

    Args:
        sql: 要执行的 SQL 语句
    """
    # 模拟数据库查询
    if "SELECT" in sql.upper():
        return "查询结果：[(1, 'Alice', 25), (2, 'Bob', 30), (3, 'Charlie', 35)]"
    return "Query executed successfully"


@tool
def describe_table(table_name: str) -> str:
    """获取表结构信息

    Args:
        table_name: 表名
    """
    schemas = {
        "users": "id INTEGER, name TEXT, age INTEGER, email TEXT",
        "orders": "id INTEGER, user_id INTEGER, amount REAL, status TEXT",
        "products": "id INTEGER, name TEXT, price REAL, category TEXT"
    }
    return schemas.get(table_name, "Table not found")


@tool
def list_tables() -> str:
    """列出数据库中所有可用的表"""
    return "Available tables: users, orders, products"


# ============ 2. SQL Agent 构建 ============
def build_sql_agent():
    """构建自然语言到 SQL 的 Agent"""
    model = ChatOpenAI(
        model="Pro/MiniMaxAI/MiniMax-M2.5",
        base_url="https://api.siliconflow.cn/v1",
        api_key="sk-xxxx"
    )

    tools = [query_database, describe_table, list_tables]
    memory = InMemorySaver()

    agent = create_agent(
        model,
        tools,
        checkpointer=memory,
        prompt="你是一个 SQL 专家。用户用自然语言提问时，你需要：
1. 先查看有哪些表
2. 查看表结构
3. 编写并执行 SQL
4. 用中文回答用户问题"
    )

    return agent


# ============ 3. 执行示例 ============
if __name__ == "__main__":
    print("=== SQL Agent 实战 ===")
    agent = build_sql_agent()
    config = {"configurable": {"thread_id": "sql-1"}}

    # 问关于用户数据的问题
    result = agent.invoke({
        "messages": [{"role": "user", "content": "查看用户表有多少条记录？"}]
    }, config)

    print("Q: 查看用户表有多少条记录？")
    print("A:", result["messages"][-1].content)
