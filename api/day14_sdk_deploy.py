"""
LangGraph 7天系列 Day 14：LangGraph SDK 与生产部署

本代码演示：
- LangGraph SDK 客户端使用
- langgraph CLI 命令
- Docker 部署配置
"""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver


# ============ 1. 定义状态 ============
class DeployState(TypedDict):
    status: str
    message: str


# ============ 2. 定义节点 ============
def process(state: DeployState) -> dict:
    """处理节点"""
    return {"status": "completed", "message": "处理完成"}


# ============ 3. 构建可部署的图 ============
memory = InMemorySaver()
builder = StateGraph(DeployState)
builder.add_node("process", process)
builder.add_edge(START, "process")
builder.add_edge("process", END)
app = builder.compile(checkpointer=memory)


# ============ 4. SDK 客户端使用示例（注释） ============
"""
# LangGraph SDK 客户端使用示例（连接已部署的服务）

from langgraph_sdk import get_client, get_sync_client

# 异步客户端
async def async_example():
    client = get_client(url="http://localhost:8123")

    # 列出可用助手
    assistants = await client.assistants.search()
    print(assistants)

    # 创建线程
    thread = await client.threads.create()

    # 运行助手
    run = await client.runs.create(
        thread_id=thread["thread_id"],
        assistant_id="my-agent",
        input={"messages": [{"role": "user", "content": "你好"}]}
    )

    # 等待完成
    result = await client.runs.join(thread["thread_id"], run["run_id"])
    print(result)

    # 流式响应
    async for chunk in client.runs.stream(
        thread_id=thread["thread_id"],
        assistant_id="my-agent",
        input={"messages": [{"role": "user", "content": "讲个笑话"}]},
        stream_mode="updates"
    ):
        print(chunk)

# 同步客户端
def sync_example():
    client = get_sync_client(url="http://localhost:8123")
    thread = client.threads.create()
    result = client.runs.wait(
        thread_id=thread["thread_id"],
        assistant_id="my-agent",
        input={"messages": [{"role": "user", "content": "你好"}]}
    )
    print(result)
"""


# ============ 5. CLI 命令说明 ============
CLI_COMMANDS = """
=== LangGraph CLI 常用命令 ===

# 1. 开发环境启动
langgraph dev --port 2024

# 2. 构建 Docker 镜像
langgraph build -t my-agent:latest

# 3. Docker 部署
langgraph up --port 8123 --wait

# 4. 生成 Dockerfile
langgraph dockerfile ./Dockerfile

# 5. 创建新项目（从模板）
langgraph new my-agent --template react-agent
"""


# ============ 6. Docker 配置示例 ============
DOCKERFILE_TEMPLATE = """
FROM langgraph/langgraph:latest

WORKDIR /app

# 复制应用代码
COPY . /app

# 安装依赖
RUN pip install -e .

# 暴露端口
EXPOSE 8123

# 启动命令
CMD ["langgraph", "dev", "--port", "8123"]
"""


# ============ 7. langgraph.json 配置 ============
LANGGRAPH_CONFIG = """
{
  "dependencies": ["./pyproject.toml"],
  "graphs": {
    "agent": "./api/day1_stategraph.py:app"
  },
  "threads": []
}
"""


# ============ 8. 执行演示 ============
if __name__ == "__main__":
    print("=== LangGraph SDK 与生产部署 ===")
    print()

    print("1. 本地运行测试:")
    config = {"configurable": {"thread_id": "deploy-demo"}}
    result = app.invoke({"status": "running", "message": "开始部署..."}, config)
    print(f"   结果: {result}")
    print()

    print("2. SDK 客户端使用（需要部署服务后）:")
    print("   请参考代码中的注释示例")
    print()

    print("3. CLI 命令:")
    print(CLI_COMMANDS)

    print("4. Dockerfile 模板:")
    print(DOCKERFILE_TEMPLATE)

    print("5. langgraph.json 配置:")
    print(LANGGRAPH_CONFIG)

    print()
    print("✅ LangGraph SDK 与生产部署演示完成！")
