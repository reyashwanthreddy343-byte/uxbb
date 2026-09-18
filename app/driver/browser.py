import os
import io
import base64
from typing import Dict, Any, Optional
from PIL import Image
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from app.core.logger import logger

class BlackBoxBrowserDriver:
    """
    STRICT ENFORCEMENT: Black-Box Browser Driver.
    This driver has NO methods accepting CSS selectors, XPaths, or DOM IDs.
    All interactions MUST be dispatched via raw viewport pixel coordinates.
    """
    
    def __init__(self, viewport_width: int = 1280, viewport_height: int = 800):
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    async def start(self, platform: str = "chrome"):
        logger.info(f"Starting black-box browser driver for platform: {platform}")
        self._playwright = await async_playwright().start()
        # Headless black-box execution
        self._browser = await self._playwright.chromium.launch(headless=True)
        self._context = await self._browser.new_context(
            viewport={"width": self.viewport_width, "height": self.viewport_height}
        )
        self._page = await self._context.new_page()

    async def navigate(self, url: str):
        if not self._page:
            raise RuntimeError("Browser not initialized. Call start() first.")
        logger.info(f"Navigating black-box driver to target: {url}")
        await self._page.goto(url, wait_until="networkidle")
        await self._page.wait_for_timeout(500)

    async def capture_screenshot_bytes(self) -> bytes:
        if not self._page:
            raise RuntimeError("Browser not initialized.")
        return await self._page.screenshot(type="png")

    async def capture_screenshot_base64(self) -> str:
        png_bytes = await self.capture_screenshot_bytes()
        return base64.b64encode(png_bytes).decode("utf-8")

    async def capture_screenshot_image(self) -> Image.Image:
        png_bytes = await self.capture_screenshot_bytes()
        return Image.open(io.BytesIO(png_bytes)).convert("RGB")

    async def click_at_coordinate(self, x: int, y: int):
        """Dispatches a mouse click purely at pixel coordinate (x, y)."""
        if not self._page:
            raise RuntimeError("Browser not initialized.")
        logger.info(f"Black-Box Action: Mouse Click at coordinate ({x}, {y})")
        # Visual movement + click
        await self._page.mouse.move(x, y)
        await self._page.mouse.click(x, y)
        await self._page.wait_for_timeout(600)

    async def type_at_coordinate(self, x: int, y: int, text: str):
        """Clicks coordinate (x, y) to focus, then types text keystrokes."""
        if not self._page:
            raise RuntimeError("Browser not initialized.")
        logger.info(f"Black-Box Action: Focus ({x}, {y}) and Type text (len={len(text)})")
        await self._page.mouse.click(x, y)
        await self._page.keyboard.type(text, delay=50)
        await self._page.wait_for_timeout(400)

    async def scroll_at_coordinate(self, x: int, y: int, delta_y: int = 300):
        """Scrolls at coordinate (x, y) by delta_y pixels."""
        if not self._page:
            raise RuntimeError("Browser not initialized.")
        logger.info(f"Black-Box Action: Scroll at ({x}, {y}) by delta_y={delta_y}")
        await self._page.mouse.move(x, y)
        await self._page.mouse.wheel(0, delta_y)
        await self._page.wait_for_timeout(400)

    async def get_raw_accessibility_tree(self) -> Dict[str, Any]:
        """Captures standard browser accessibility tree snapshot (zero proprietary hooks)."""
        if not self._page:
            raise RuntimeError("Browser not initialized.")
        snapshot = await self._page.accessibility.snapshot()
        return snapshot or {}

    async def close(self):
        logger.info("Closing black-box browser session.")
        if self._page:
            await self._page.close()
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
