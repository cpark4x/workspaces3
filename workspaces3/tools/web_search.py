"""Web search tool using Tavily API."""

import os
from typing import Any

from tavily import AsyncTavilyClient

from workspaces3.tools.base import Tool, ToolResult


class WebSearchTool(Tool):
    """Web search tool powered by Tavily API."""

    def __init__(self, api_key: str | None = None) -> None:
        """
        Initialize web search tool.

        Args:
            api_key: Tavily API key (defaults to TAVILY_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not set. Get one from https://tavily.com/")
        self.client = AsyncTavilyClient(api_key=self.api_key)

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web for information using Tavily API"

    async def execute(self, **kwargs: Any) -> ToolResult:
        """
        Execute web search.

        Args:
            query: Search query string
            max_results: Maximum number of results (default: 5)

        Returns:
            ToolResult with search results
        """
        query = kwargs.get("query")
        if not query:
            return ToolResult(success=False, output="", error="No query provided for web search")

        max_results = kwargs.get("max_results", 5)

        try:
            response = await self.client.search(query=query, max_results=max_results, include_answer=True)

            results = []
            for result in response.get("results", []):
                results.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "score": result.get("score", 0.0),
                    }
                )

            answer = response.get("answer", "")

            output_lines = []
            if answer:
                output_lines.append(f"Answer: {answer}\n")

            output_lines.append(f"Found {len(results)} results:\n")
            for i, r in enumerate(results, 1):
                output_lines.append(f"{i}. {r['title']}")
                output_lines.append(f"   URL: {r['url']}")
                output_lines.append(f"   {r['content'][:200]}...")
                output_lines.append("")

            return ToolResult(
                success=True,
                output="\n".join(output_lines),
                metadata={"query": query, "results": results, "answer": answer},
            )

        except Exception as e:
            return ToolResult(success=False, output="", error=f"Web search failed: {str(e)}")
