# DeepSeek Scout MCP

FastMCP 服务器，封装 DeepSeek 的 Search 与 Fetch 能力。

**API Key 由调用方通过 HTTP 请求头传入，服务端不保存、不需要配置 Key。**

```
Authorization: Bearer <你的 DeepSeek API Key>
```

备选：`X-DeepSeek-Api-Key: <key>`。工具参数中**没有** `api_key`，缺失请求头时会返回 `Missing API key header`。

## 工具

- `deepseek_search(query, count=10, ori_question=None, localization="", need_content=False)`
- `deepseek_fetch(url)`

## 客户端配置示例

```json
{
  "mcpServers": {
    "deepseek-scout": {
      "type": "http",
      "url": "http://localhost:8000/mcp",
      "headers": { "Authorization": "Bearer sk-你的Key" }
    }
  }
}
```

## 本地运行

```bash
pip install -e .
python -m deepseek_scout_mcp
# 或
uvx deepseek-scout-mcp
```