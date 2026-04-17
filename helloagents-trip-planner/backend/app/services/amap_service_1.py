"""高德地图 MCP 服务封装 (基于标准 langchain-mcp-adapters)"""

import os
import json
import asyncio
import re
from typing import List, Dict, Any, Optional
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv

load_dotenv()

class AmapService:
    """高德地图服务封装类 (标准 MCP 异步版)"""

    def __init__(self):
        """初始化服务配置"""
        self.client: Optional[MultiServerMCPClient] = None
        # 使用您提供的标准 Node 路径配置
        self.server_config = {
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

    async def _ensure_client(self) -> MultiServerMCPClient:
        """确保 MCP 客户端已初始化 (延迟加载单例)"""
        if self.client is None:
            if not os.getenv("AMAP_API_KEY"):
                raise ValueError("未配置 AMAP_API_KEY，请检查环境变量")

            # 初始化标准 MCP 客户端
            self.client = MultiServerMCPClient(self.server_config)
            # 预热：获取一次工具列表以确保进程启动成功
            await self.client.get_tools()
            print("✅ 高德地图 MCP 服务已连接 (基于 Stdio 管道)")
        return self.client

    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        内部通用工具调用方法
        处理：Session管理、工具执行、JSON解析与清洗
        """
        client = await self._ensure_client()

        # 使用适配器标准的 session 模式调用
        async with client.session("amap") as session:
            result = await session.call_tool(tool_name, arguments)

            if not result.content or len(result.content) == 0:
                return None

            raw_text = result.content[0].text

            # 1. 尝试直接解析 JSON
            try:
                return json.loads(raw_text)
            except json.JSONDecodeError:
                # 2. 如果返回包含调试信息，使用正则提取 JSON 部分
                json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group())
                    except json.JSONDecodeError:
                        pass
                return raw_text

    async def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> List[Dict[str, Any]]:
        """搜索兴趣点 (POI)"""
        try:
            result = await self._call_tool("maps_text_search", {
                "keywords": keywords,
                "city": city,
                "citylimit": str(citylimit).lower()
            })
            if isinstance(result, dict) and "pois" in result:
                return result["pois"]
            return []
        except Exception as e:
            print(f"❌ POI 搜索失败: {e}")
            return []

    async def get_weather(self, city: str) -> Dict[str, Any]:
        """查询天气信息"""
        try:
            return await self._call_tool("maps_weather", {"city": city})
        except Exception as e:
            print(f"❌ 天气查询失败: {e}")
            return {}

    async def plan_route(
        self,
        origin_address: str,
        destination_address: str,
        origin_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        route_type: str = "walking"
    ) -> Dict[str, Any]:
        """
        规划路线 (支持 walking/driving/transit)
        注意：此 MCP Server 通常提供按地址规划的变体工具
        """
        tool_map = {
            "walking": "maps_direction_walking_by_address",
            "driving": "maps_direction_driving_by_address",
            "transit": "maps_direction_transit_integrated_by_address"
        }
        tool_name = tool_map.get(route_type, "maps_direction_walking_by_address")

        args = {
            "origin_address": origin_address,
            "destination_address": destination_address
        }
        if origin_city: args["origin_city"] = origin_city
        if destination_city: args["destination_city"] = destination_city

        try:
            return await self._call_tool(tool_name, args)
        except Exception as e:
            print(f"❌ 路线规划失败: {e}")
            return {}

    async def geocode(self, address: str, city: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """地理编码 (地址转坐标)"""
        try:
            args = {"address": address}
            if city: args["city"] = city

            result = await self._call_tool("maps_geo", args)
            if isinstance(result, dict) and "geocodes" in result and result["geocodes"]:
                return result["geocodes"][0]
            return None
        except Exception as e:
            print(f"❌ 地理编码失败: {e}")
            return None

    async def get_poi_detail(self, poi_id: str) -> Dict[str, Any]:
        """获取 POI 详细信息"""
        try:
            return await self._call_tool("maps_search_detail", {"id": poi_id})
        except Exception as e:
            print(f"❌ 获取 POI 详情失败: {e}")
            return {}

    async def close(self):
        """显式关闭客户端以释放子进程资源"""
        # MultiServerMCPClient 随程序退出通常会自动释放，
        # 但在长连接应用中建议手动管理
        pass


# ==================== 单例模式封装 ====================

_amap_service = None

def get_amap_service_1() -> AmapService:
    """获取单例实例"""
    global _amap_service
    if _amap_service is None:
        _amap_service = AmapService()
    return _amap_service


# ==================== 测试示例 ====================
if __name__ == "__main__":
    async def main():
        service = get_amap_service_1()

        print("\n--- 正在查询天气 ---")
        weather = await service.get_weather("苏州")
        print(json.dumps(weather, indent=2, ensure_ascii=False))

        print("\n--- 正在地理编码 ---")
        geo = await service.geocode("苏州中心", "苏州")
        if geo:
            print(f"名称: {geo.get('formatted_address')} 坐标: {geo.get('location')}")

    asyncio.run(main())