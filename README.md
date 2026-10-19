# DeepSeek Scout MCP

FastMCP 服务器，封装 DeepSeek 的 Search 与 Fetch 能力，以 stdio 方式本地运行。

## 服务配置

```json
{
  "mcpServers": {
    "deepseek-scout": {
      "command": "uvx",
      "args": [
        "deepseek-scout-mcp@latest"
      ],
      "env": {
        "DEEPSEEK_API_KEY": "<YOUR_DEEPSEEK_API_KEY>"
      }
    }
  }
}
```

API Key 通过环境变量 `DEEPSEEK_API_KEY` 提供，工具参数中没有 `api_key`。

## 工具

- `deepseek_search(query, count=10, ori_question=None, localization="", need_content=False)`
- `deepseek_fetch(url)`

## 本地运行

```bash
pip install -e .
python -m deepseek_scout_mcp
# 或
uvx deepseek-scout-mcp
```

以 stdio 方式启动，由 MCP 客户端通过上面的配置拉起进程。
