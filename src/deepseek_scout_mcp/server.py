"""
DeepSeek Scout MCP Server
将 DeepSeek 的 /v1/tools/search 和 /v1/tools/fetch 封装为 MCP 工具。
API Key 由每个调用者在调用时通过 api_key 参数传入，服务端不保存 Key。
"""

import os
import httpx
from fastmcp import FastMCP
from typing import Optional, Any

mcp = FastMCP(name="DeepSeek Scout")

DEEPSEEK_BASE_URL = "https://api.deepseek.com"


def _build_headers(api_key: str) -> dict[str, str]:
    """校验并构造请求头。"""
    if not api_key or not api_key.strip():
        raise ValueError("api_key 不能为空，请填写你自己的 DeepSeek API Key")
    return {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
    }


@mcp.tool(
    name="deepseek_search",
    description=(
        "使用 DeepSeek 搜索引擎搜索网页，返回结构化结果列表。"
        "支持 site:、-site:、引号等搜索语法。"
        "调用时必须传入 api_key（调用者自己的 DeepSeek API Key），服务端不保存 Key。"
    ),
)
async def deepseek_search(
    query: str,
    api_key: str,
    count: int = 10,
    ori_question: Optional[str] = None,
    localization: str = "",
    need_content: bool = False,
) -> dict[str, Any]:
    """
    按 query 搜索网页，返回结构化结果列表。

    Args:
        query: 搜索词，1~128 个 Unicode 字符，不能全为空白。支持 site:、-site:、引号等语法。
        api_key: 调用者自己的 DeepSeek API Key（必填），仅用于本次请求，服务端不存储。
        count: 返回条数，1~50，默认 10。
        ori_question: 触发搜索的用户原始问题，1~128 字符，有助于理解搜索意图。
        localization: 用于优先返回本地化搜索结果的 IP 地址，默认为空字符串。
        need_content: 是否在 content 中返回网页正文，默认为 false。
    """
    try:
        headers = _build_headers(api_key)
    except ValueError as e:
        return {"error": "Invalid api_key", "detail": str(e)}

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
        "调用时必须传入 api_key（调用者自己的 DeepSeek API Key），服务端不保存 Key。"
    ),
)
async def deepseek_fetch(url: str, api_key: str) -> dict[str, Any]:
    """
    抓取网页，返回页面标题与 Markdown 格式的内容。

    Args:
        url: 要抓取的网页地址，必须为含 host 的 HTTP/HTTPS URL，长度不超过 8192。
        api_key: 调用者自己的 DeepSeek API Key（必填），仅用于本次请求，服务端不存储。
    """
    if not url.startswith(("http://", "https://")):
        return {
            "error": "Invalid URL",
            "detail": "URL 必须以 http:// 或 https:// 开头",
        }

    try:
        headers = _build_headers(api_key)
    except ValueError as e:
        return {"error": "Invalid api_key", "detail": str(e)}

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
    """托管平台入口：以 streamable-http 启动，监听平台注入的 PORT。"""
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    mcp.run(transport="streamable-http", host=host, port=port)