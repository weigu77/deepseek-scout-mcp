# DeepSeek Scout MCP

FastMCP 服务器，封装 DeepSeek 的 Search 与 Fetch 能力。

**API Key 由每个调用者在调用工具时通过 `api_key` 参数传入，服务端不保存、不需要配置 Key。**

## 工具

- `deepseek_search(query, api_key, count=10, ori_question=None, localization="", need_content=False)`
- `deepseek_fetch(url, api_key)`

## 本地运行

```bash
pip install -e .
python -m deepseek_scout_mcp
# 或
uvx deepseek-scout-mcp
```