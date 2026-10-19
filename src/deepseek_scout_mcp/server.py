"""DeepSeek Scout MCP Server

将 DeepSeek 的 /v1/tools/search 与 /v1/tools/fetch 封装为 MCP 工具。
以 stdio 方式本地运行，API Key 通过环境变量 DEEPSEEK_API_KEY 提供。
"""

import os
from typing import Annotated

import requests
from fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP(name="DeepSeek Scout")

DEEPSEEK_BASE_URL = "https://api.deepseek.com"


def _headers() -> dict[str, str]:
    """构造请求 DeepSeek API 的请求头，Key 取自环境变量 DEEPSEEK_API_KEY。"""
    return {
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
        "Content-Type": "application/json",
    }


@mcp.tool(
    name="deepseek_search",
    description=(
        "使用 DeepSeek 搜索引擎搜索网页，返回结构化结果列表。"
        "支持 site:、-site:、引号等搜索语法。"
        "API Key 由服务端通过环境变量 DEEPSEEK_API_KEY 提供，"
        "无需也不能在工具参数中提供。"
    ),
)
def deepseek_search(
    query: Annotated[
        str,
        Field(
            description=(
                "搜索词，1～128 个字符，不能全为空白。"
                '支持 site:、-site:、"精确短语"、lang:、after:、before: 等搜索语法'
            )
        ),
    ],
    count: Annotated[
        int, Field(description="返回结果条数，1～50，默认 10", ge=1, le=50)
    ] = 10,
    ori_question: Annotated[
        str | None,
        Field(description="触发本次搜索的用户原始问题，有助于理解搜索意图"),
    ] = None,
    localization: Annotated[
        str,
        Field(description="用于优先返回本地化搜索结果的 IP 地址，默认为空字符串"),
    ] = "",
    need_content: Annotated[
        bool, Field(description="是否在结果中返回网页正文 content")
    ] = False,
) -> dict:
    """按关键词搜索网页，返回结构化结果列表。"""
    payload = {
        "query": query,
        "count": count,
        "need_content": need_content,
    }
    if ori_question:
        payload["ori_question"] = ori_question
    if localization:
        payload["localization"] = localization

    response = requests.post(
        f"{DEEPSEEK_BASE_URL}/v1/tools/search",
        headers=_headers(),
        json=payload,
    )
    return response.json()


@mcp.tool(
    name="deepseek_fetch",
    description=(
        "抓取指定网页，并以 Markdown 文本返回正文内容。"
        "API Key 由服务端通过环境变量 DEEPSEEK_API_KEY 提供，"
        "无需也不能在工具参数中提供。"
    ),
)
def deepseek_fetch(
    url: Annotated[
        str,
        Field(description="要抓取的网页地址，必须为含 host 的 HTTP/HTTPS URL"),
    ],
) -> dict:
    """抓取单个网页，返回页面标题与 Markdown 格式的正文。"""
    response = requests.post(
        f"{DEEPSEEK_BASE_URL}/v1/tools/fetch",
        headers=_headers(),
        json={"url": url},
    )
    return response.json()


def run():
    """本地运行入口：以 stdio 方式启动 MCP 服务。"""
    mcp.run(transport="stdio")
