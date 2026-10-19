# DeepSeek Scout MCP

![PyPI](https://img.shields.io/pypi/v/deepseek-scout-mcp)
![Python](https://img.shields.io/pypi/pyversions/deepseek-scout-mcp)
![License](https://img.shields.io/badge/license-MIT-green)
![MCP](https://img.shields.io/badge/MCP-stdio-2f6feb)

把 [DeepSeek 的网页搜索与网页抓取接口](https://api-docs.deepseek.com/zh-cn/guides/search) 封装成 MCP 工具，让任何支持 MCP 的客户端（Claude Desktop、Cursor、魔搭社区等）直接获得**联网搜索**与**网页抓取**能力。

底层是 DeepSeek 自研搜索引擎 —— 长期为 DeepSeek 网页端与 API 端提供搜索能力，每天稳定处理全球数亿次搜索请求。

**为什么值得用**

- **覆盖广**：AI 原生通用搜索引擎，索引全球千亿级网页，支持多语言搜索
- **质量高**：实时返回高相关、高权威、高时效的结果；每条结果自带 `rerank_score`（0～3）、`authority`（0～4）和发布时间，便于二次筛选
- **抗污染**：对 SEO 作弊、GEO 操纵与低质 AIGC 有专门的识别过滤机制，更倾向权威可信来源
- **接入成本低**：以 stdio 方式运行，进程由客户端拉起、不占端口；API Key 走环境变量 `DEEPSEEK_API_KEY`，不写进代码；两个工具直连 DeepSeek，无中间状态与缓存，Search 与 Fetch 均为只读请求

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

把这段 JSON 放进客户端的 MCP 配置即可，`uvx` 会自动拉取并运行最新发布版。API Key 在 [platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys) 创建。

## 安装

```bash
# 无需安装，uvx 直接运行（推荐）
uvx deepseek-scout-mcp

# 或安装为命令
pip install deepseek-scout-mcp

# 或从源码
git clone https://github.com/weigu77/deepseek-scout-mcp
cd deepseek-scout-mcp && pip install -e .
```

## 工具

### `deepseek_search`

按关键词搜索网页，返回结构化结果列表。

| 参数 | 类型 | 必填 | 默认 | 说明 |
| --- | --- | --- | --- | --- |
| `query` | string | 是 | — | 搜索词，1～128 个字符，不能全为空白，支持下方[搜索语法](#搜索语法) |
| `count` | integer | 否 | `10` | 返回结果条数，1～50 |
| `ori_question` | string | 否 | `null` | 触发本次搜索的用户原始问题，有助于理解搜索意图 |
| `localization` | string | 否 | `""` | 用于优先返回本地化搜索结果的 IP 地址 |
| `need_content` | boolean | 否 | `false` | 是否在 `content` 中返回网页正文 |

返回 `results` 数组，每项字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `rerank_score` | number | 排序分数，0～3，≥1.5 为优质结果 |
| `title` | string | 标题 |
| `url` | string | 结果链接 |
| `snippet` | string | 短摘要（约 100～200 字符），适合前端展示 |
| `summary` | string | 长摘要（约 600～800 字符），适合喂给模型 |
| `content` | string | 网页正文，`need_content` 为 `false` 时为空字符串 |
| `site_name` | string \| null | 站点名称 |
| `site_icon` | string \| null | 站点图标 URL |
| `date` | string \| null | 发布时间，UTC 的 RFC 3339 格式 |
| `authority` | integer | 网页权威性，0～4（`-1` 表示未知），≥3 为极权威结果 |

搜索正常结束但没有匹配结果时返回空数组。

### `deepseek_fetch`

抓取单个网页，以 Markdown 文本返回正文。

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `url` | string | 是 | 网页地址，长度 ≤ 8192，必须为含 host 的 HTTP/HTTPS URL，且不携带用户名或密码 |

返回 `title`（缺失时为空字符串）与 `content`（Markdown 正文）。抓取结果受目标站点可用性与访问策略影响。

## 搜索语法

`query` 中的操作符会原样传给 DeepSeek 搜索引擎，可在一条 query 中组合使用。

| 操作符 | 示例 | 说明 |
| --- | --- | --- |
| `site:` | `DeepSeek site:github.com` | 限定站点；多个站点用空格分隔并以 `OR` 连接，如 `DeepSeek site:github.com OR site:huggingface.co` |
| `-site:` | `DeepSeek -site:example.com` | 排除站点，多个用空格分隔 |
| `-` | `DeepSeek -广告` | 排除含指定关键词的网页，多个用空格分隔 |
| `-"..."` | `DeepSeek -"release notes"` | 排除含指定短语的网页，短语可含空格 |
| `"..."` | `DeepSeek "精确短语"` | 精确匹配短语，多个用空格分隔 |
| `lang:` | `DeepSeek lang:zh,en` | 限定语言，多个用逗号分隔 |
| `after:` | `DeepSeek after:2025` / `after:2025-01-01` | 限定发布日期之后 |
| `before:` | `DeepSeek before:2026` / `before:2026-06-01` | 限定发布日期之前 |

例如：

```json
{
  "query": "DeepSeek 模型 site:github.com OR site:huggingface.co lang:zh after:2025",
  "count": 10
}
```

## 错误处理

接口错误以 DeepSeek 原始错误 JSON（OpenAI 兼容格式）返回，例如：

```json
{
  "error": {
    "message": "'count' must be between 1 and 50",
    "type": "invalid_request_error",
    "param": null,
    "code": "invalid_request_error"
  }
}
```

| 状态码 | 含义 |
| --- | --- |
| 400 | 请求头或请求体不合法（JSON 格式错误、字段值无效等） |
| 401 | API Key 缺失或无效 —— 检查 `DEEPSEEK_API_KEY` 是否注入 |
| 402 | 账号余额不足 |
| 403 | Fetch 请求被安全策略拒绝 |
| 404 | Fetch 未获取到可用正文（URL 不可用、被拦截、内容类型不支持等） |
| 408 / 429 / 5xx | 读取超时、超出 QPS、服务端错误 —— **等待后重试** |

## 限速与计费

- Search 与 Fetch **分别独立限速**，各 **5 QPS**（账号粒度，与使用哪个 Key 无关）；Fetch 还对目标域名另有 QPS 限制。
- 按**成功请求次数**计费，不按 token 或结果条数：两者均为 **5 元 / 1000 次**。仅 HTTP 200 且有结果（Search 的 `results` 非空、Fetch 返回正文）的请求才计费，失败、无结果、超时不计费。`count` 不影响价格。
- 详见 [官方文档](https://api-docs.deepseek.com/zh-cn/guides/search)。

## 本地运行

```bash
pip install -e .
python -m deepseek_scout_mcp
# 或
uvx deepseek-scout-mcp
```

以 stdio 方式启动，由 MCP 客户端通过上面的配置拉起进程。调试时可手工喂 JSON-RPC 消息，或直接用：

```bash
DEEPSEEK_API_KEY=sk-xxxx uvx deepseek-scout-mcp
```

## 已知问题

### 走魔搭托管地址 + fastmcp 系客户端时报 `handshake protocol era`

现象：

```text
mcp.shared.exceptions.MCPError: this connection serves the handshake protocol era;
requests carrying the 2026-07-28 envelope are not accepted on it
```

原因：这条错误由**魔搭网关**返回，与本包无关（本包代码里没有这段字符串）。魔搭托管地址 `https://mcp.api-inference.modelscope.net/<id>/mcp` 只服务握手时代协议（`2025-06-18`），而 fastmcp 的客户端默认 `mode="auto"`，连接时会先探测 `server/discover` 并切到 `2026-07-28` 协议，之后每个请求都被网关拒绝。

影响范围：

- **本地 stdio 方式（本 README 推荐的配置）不受影响** —— 不经过任何网关
- 只讲握手时代协议的客户端（Claude Desktop、Cursor 等）也不受影响
- 会中招的是**代码里**用了 fastmcp 系客户端、又没有指定协议模式的情况，典型是 LangChain 的 `MCPAdapter`

绕过方法：显式用 `mode="legacy"` 预构建客户端，再交给 `MCPAdapter`：

```python
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from langchain.mcp import MCPAdapter

client = Client(
    StreamableHttpTransport("https://mcp.api-inference.modelscope.net/<id>/mcp"),
    mode="legacy",
)
async with MCPAdapter(target=client) as adapter:
    tools = await adapter.list_tools()
```

该规避属于客户端侧设置，**没法写进 MCP 客户端的 JSON 配置**，只能在代码里改；若魔搭网关后续支持新版协议，此问题会自动消失。

## 相关链接

- [DeepSeek 网页搜索与抓取指南](https://api-docs.deepseek.com/zh-cn/guides/search)
- [Search API Reference](https://api-docs.deepseek.com/zh-cn/api/search) · [Fetch API Reference](https://api-docs.deepseek.com/zh-cn/api/fetch)
- [GitHub 仓库](https://github.com/weigu77/deepseek-scout-mcp) · [PyPI](https://pypi.org/project/deepseek-scout-mcp/) · [问题反馈](https://github.com/weigu77/deepseek-scout-mcp/issues)
- [MCP 协议](https://modelcontextprotocol.io) · [FastMCP](https://github.com/jlowin/fastmcp)
