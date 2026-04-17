# core/tool_module.py
import os
from typing import List
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from pydantic import BaseModel, Field

load_dotenv()

# ========== 1. 自定义工具（保留原有） ==========
class ItineraryItem(BaseModel):
    name: str = Field(description="景点名称或活动名称")
    type: str = Field(description="类型：'visit' (游玩) 或 'travel' (路程)")
    duration_min: int = Field(description="该环节耗费的时长，单位为分钟")

@tool
def add(a: float, b: float) -> float:
    """两数相加"""
    return a + b

@tool
def get_current_time() -> str:
    """获取当前系统时间。"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def calculate_itinerary_slots(
        items: List[ItineraryItem],
        start_time: str = "09:00"
) -> str:
    """智能计算分时段行程建议。"""
    from datetime import datetime, timedelta
    current_time = datetime.strptime(start_time, "%H:%M")
    timeline = []
    for item in items:
        d_min = item.duration_min
        end_time = current_time + timedelta(minutes=d_min)
        slot = f"{current_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')} : {item.name} ({'游玩' if item.type == 'visit' else '路程'})"
        timeline.append(slot)
        current_time = end_time + timedelta(minutes=15)
    return "\n".join(timeline)

# ========== 2. MCP工具加载函数 ==========
async def load_mcp_tools():
# def load_mcp_tools():
    """加载高德地图MCP工具"""
    server_config = {
        "amap": {
            "transport": "stdio",
            "command": "node",
            "args": [
                r"D:\MCP\node_modules\@amap\amap-maps-mcp-server\build\index.js"
            ],
            "env": {
                **os.environ,
                "AMAP_MAPS_API_KEY": os.getenv("AMAP_API_KEY")
            },
        }
    }
    client = MultiServerMCPClient(server_config)
    mcp_tools = await client.get_tools()
    # mcp_tools = client.get_tools()

    # # 同步获取工具
    # import asyncio
    # mcp_tools = asyncio.run(client.get_tools())

    return mcp_tools



# ========== 3. 工具注册表 ==========
async def get_all_tools():
# def get_all_tools():
    """获取所有工具（自定义+MCP）"""
    mcp_tools = await load_mcp_tools()
    # mcp_tools = load_mcp_tools()
    # custom_tools = [add, get_current_time, calculate_itinerary_slots]
    # return custom_tools + mcp_tools
    return mcp_tools
