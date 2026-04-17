## 环境配置说明

下载并配置相关路径，如下：

`..\helloagents-trip-planner\backend\app\agents\tool_module.py`

```python
server_config = {
    "amap": {
        "transport": "stdio",
        "command": "node",
        "args": [
            r"D:\MCP\node_modules\@amap\amap-maps-mcp-server\build\index.js"
        ],
        "env": {
            **os.environ,
            # "AMAP_MAPS_API_KEY": os.getenv("AMAP_API_KEY")
            "AMAP_MAPS_API_KEY": "3ad5f4937427a68c41209953b6e34932"
        },
    }
}
