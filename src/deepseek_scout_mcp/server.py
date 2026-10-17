"""
DeepSeek Scout MCP Server
将 DeepSeek 的 /v1/tools/search 和 /v1/tools/fetch 封装为 MCP 工具。
API Key 由调用方通过 HTTP 请求头 Authorization: Bearer <key> 传入，服务端不保存 Key。
"""

import os
import httpx
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from typing import Optional, Any

mcp = FastMCP(name="DeepSeek Scout")

DEEPSEEK_BASE_URL = "https://api.deepseek.com"


def _resolve_api_key() -> str:
    """解析 DeepSeek API Key。

    优先从当前 HTTP 请求头读取（Authorization: Bearer <key>，备选 X-DeepSeek-Api-Key），
    其次读取环境变量 DEEPSEEK_API_KEY —— STDIO 托管部署下没有请求头，走这条路径。
    两者都没有时抛 ValueError。
    """
    headers = get_http_headers(include={"authorization"})
    key = headers.get("authorization", "").strip()
    if key.lower().startswith("bearer "):
        key = key[7:].strip()
    if not key:
        key = headers.get("x-deepseek-api-key", "").strip()
    if not key:
        key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not key:
        raise ValueError(
            "缺少 API Key：请通过请求头 Authorization: Bearer <key> 传入，"
            "或设置环境变量 DEEPSEEK_API_KEY"
        )
    return key


def _build_headers(api_key: str) -> dict[str, str]:
    """构造请求 DeepSeek API 的请求头。"""
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


@mcp.tool(
    name="deepseek_search",
    description=(
        "使用 DeepSeek 搜索引擎搜索网页，返回结构化结果列表。"
        "支持 site:、-site:、引号等搜索语法。"
        "API Key 由调用方通过 HTTP 请求头 Authorization: Bearer <key> 传入"
        "（托管 STDIO 部署下由服务端环境变量 DEEPSEEK_API_KEY 提供），"
        "服务端不保存 Key，无需也不能在工具参数中提供。"
    ),
)
async def deepseek_search(
    query: str,
    count: int = 10,
    ori_question: Optional[str] = None,
    localization: str = "",
    need_content: bool = False,
) -> dict[str, Any]:
    """
    按 query 搜索网页，返回结构化结果列表。

    Args:
        query: 搜索词，1~128 个 Unicode 字符，不能全为空白。支持 site:、-site:、引号等语法。
        count: 返回条数，1~50，默认 10。
        ori_question: 触发搜索的用户原始问题，1~128 字符，有助于理解搜索意图。
        localization: 用于优先返回本地化搜索结果的 IP 地址，默认为空字符串。
        need_content: 是否在 content 中返回网页正文，默认为 false。
    """
    try:
        api_key = _resolve_api_key()
    except ValueError as e:
        return {"error": "Missing API key header", "detail": str(e)}
    headers = _build_headers(api_key)

    payload = {
        "query": query,
        "count": count,
        "ori_question": ori_question,
        "localization": localization,
        "need_content": need_content,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(
                f"{DEEPSEEK_BASE_URL}/v1/tools/search",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP {e.response.status_code}",
                "detail": e.response.text,
            }
        except httpx.RequestError as e:
            return {"error": "Request failed", "detail": str(e)}


@mcp.tool(
    name="deepseek_fetch",
    description=(
        "抓取单个网页，以 Markdown 格式返回页面内容。"
        "API Key 由调用方通过 HTTP 请求头 Authorization: Bearer <key> 传入"
        "（托管 STDIO 部署下由服务端环境变量 DEEPSEEK_API_KEY 提供），"
        "服务端不保存 Key，无需也不能在工具参数中提供。"
    ),
)
async def deepseek_fetch(url: str) -> dict[str, Any]:
    """
    抓取网页，返回页面标题与 Markdown 格式的内容。

    Args:
        url: 要抓取的网页地址，必须为含 host 的 HTTP/HTTPS URL，长度不超过 8192。
    """
    if not url.startswith(("http://", "https://")):
        return {
            "error": "Invalid URL",
            "detail": "URL 必须以 http:// 或 https:// 开头",
        }

    try:
        api_key = _resolve_api_key()
    except ValueError as e:
        return {"error": "Missing API key header", "detail": str(e)}
    headers = _build_headers(api_key)

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(
                f"{DEEPSEEK_BASE_URL}/v1/tools/fetch",
                headers=headers,
                json={"url": url},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            return {
                "error": f"HTTP {e.response.status_code}",
                "detail": e.response.text,
            }
        except httpx.RequestError as e:
            return {"error": "Request failed", "detail": str(e)}


def run():
    """入口：按 MCP_TRANSPORT 启动。

    未显式设置 MCP_TRANSPORT 时，检测到平台注入的 PORT 就用 streamable-http，
    否则用 stdio —— 保证裸 `uvx deepseek-scout-mcp` 在托管平台的 list_tools 检测下可用。
    """
    transport = os.environ.get("MCP_TRANSPORT")
    if transport is None:
        transport = "streamable-http" if os.environ.get("PORT") else "stdio"
    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        host = os.environ.get("HOST", "0.0.0.0")
        port = int(os.environ.get("PORT", "8000"))
        mcp.run(transport="streamable-http", host=host, port=port)