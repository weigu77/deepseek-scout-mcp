# DeepSeek Scout MCP

FastMCP 服务器，封装 DeepSeek 的 Search 与 Fetch 能力。

## 服务配置（STDIO · 平台托管部署）

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

## API Key 传递方式

- **STDIO 托管部署**：平台读取上面配置的 `env.DEEPSEEK_API_KEY` 注入环境变量，服务端从中读取。
- **Streamable HTTP**：调用方通过请求头传入，服务端不保存、不需要配置 Key。

```
Authorization: Bearer <你的 DeepSeek API Key>
```

备选：`X-DeepSeek-Api-Key: <key>`。工具参数中**没有** `api_key`；请求头与环境变量都没有时返回 `Missing API key header`。

优先级：请求头 > 环境变量 `DEEPSEEK_API_KEY`。

## 工具

- `deepseek_search(query, count=10, ori_question=None, localization="", need_content=False)`
- `deepseek_fetch(url)`

## HTTP 客户端配置示例

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

默认以 `streamable-http` 启动，监听 `HOST`/`PORT`（默认 `0.0.0.0:8000`）；设置 `MCP_TRANSPORT=stdio` 切换为 STDIO。

```bash
pip install -e .
python -m deepseek_scout_mcp

MCP_TRANSPORT=stdio python -m deepseek_scout_mcp
# 或
uvx deepseek-scout-mcp
```
