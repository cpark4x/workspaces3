"""Browser automation tool using Playwright."""

from typing import Any

from playwright.async_api import async_playwright

from workspaces3.tools.base import Tool, ToolResult


class BrowserTool(Tool):
    """
    Browser automation tool powered by Playwright.

    Enables web scraping, form filling, navigation, and data extraction.
    """

    def __init__(self, headless: bool = True) -> None:
        """
        Initialize browser tool.

        Args:
            headless: Run browser in headless mode (default: True)
        """
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    @property
    def name(self) -> str:
        return "browser"

    @property
    def description(self) -> str:
        return "Automate browser actions - navigate, scrape, fill forms, extract data"

    async def execute(self, **kwargs: Any) -> ToolResult:
        """
        Execute browser operation.

        Supported operations:
        - navigate: Go to URL
        - click: Click element
        - type: Type text into field
        - extract: Extract text/data from page
        - screenshot: Take screenshot
        - close: Close browser

        Args:
            operation: Operation to perform
            **kwargs: Operation-specific parameters

        Returns:
            ToolResult with operation outcome
        """
        operation = kwargs.get("operation")
        if not operation:
            return ToolResult(
                success=False,
                output="",
                error="No operation specified. Use: navigate, click, type, extract, screenshot, close",
            )

        try:
            if operation == "navigate":
                return await self._navigate(kwargs.get("url", ""))
            elif operation == "extract":
                return await self._extract(kwargs.get("selector", "body"))
            elif operation == "screenshot":
                return await self._screenshot(kwargs.get("path", "screenshot.png"))
            elif operation == "close":
                return await self._close()
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Unknown operation: {operation}. Use: navigate, extract, screenshot, close",
                )

        except Exception as e:
            return ToolResult(success=False, output="", error=f"Browser operation failed: {str(e)}")

    async def _ensure_browser(self) -> None:
        """Ensure browser is initialized."""
        if self.page is None:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()

    async def _navigate(self, url: str) -> ToolResult:
        """Navigate to URL."""
        if not url:
            return ToolResult(success=False, output="", error="No URL provided")

        await self._ensure_browser()

        if self.page is None:
            return ToolResult(success=False, output="", error="Failed to initialize browser")

        await self.page.goto(url)
        title = await self.page.title()

        return ToolResult(
            success=True, output=f"Navigated to {url}\nPage title: {title}", metadata={"url": url, "title": title}
        )

    async def _extract(self, selector: str) -> ToolResult:
        """Extract text from page using CSS selector."""
        if self.page is None:
            return ToolResult(success=False, output="", error="No page loaded. Navigate first.")

        element = await self.page.query_selector(selector)
        if element is None:
            return ToolResult(success=False, output="", error=f"Element not found: {selector}")

        text = await element.inner_text()

        return ToolResult(success=True, output=text, metadata={"selector": selector, "length": len(text)})

    async def _screenshot(self, path: str) -> ToolResult:
        """Take screenshot of current page."""
        if self.page is None:
            return ToolResult(success=False, output="", error="No page loaded. Navigate first.")

        await self.page.screenshot(path=path)

        return ToolResult(success=True, output=f"Screenshot saved to {path}", metadata={"path": path})

    async def _close(self) -> ToolResult:
        """Close browser."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None

        return ToolResult(success=True, output="Browser closed", metadata={})

    async def __aenter__(self):
        """Context manager entry."""
        await self._ensure_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self._close()
