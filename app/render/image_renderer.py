"""Image Renderer module.

Uses Playwright + Chromium to render HTML into PNG screenshots.
Captures only the ``#schedule-table`` element for a clean image output.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ImageRenderer:
    """Renders HTML content as high‑resolution PNG images via headless Chromium."""

    def __init__(self, viewport_width: int = 2000, dpr: int = 2) -> None:
        self._viewport_width = viewport_width
        self._dpr = dpr
        self._browser = None
        self._playwright = None

    async def startup(self) -> None:
        """Launch the headless Chromium browser (singleton)."""
        try:
            from playwright.async_api import async_playwright

            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )
            logger.info("Playwright Chromium browser started successfully")
        except Exception:
            logger.exception("Failed to start Playwright browser")
            raise

    async def shutdown(self) -> None:
        """Close the browser and Playwright instance."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None
        logger.info("Playwright browser shut down")

    async def render(self, html_content: str) -> bytes:
        """Render *html_content* and return a PNG screenshot of ``#schedule-table``.

        Parameters
        ----------
        html_content:
            A complete HTML document (the image‑only template).

        Returns
        -------
        bytes
            Raw PNG image data.
        """
        if self._browser is None:
            await self.startup()

        page = await self._browser.new_page(
            viewport={"width": self._viewport_width, "height": 1200},
            device_scale_factor=self._dpr,
        )
        try:
            await page.set_content(html_content, wait_until="networkidle")
            # Wait for fonts to load
            await page.wait_for_timeout(500)

            element = page.locator("#schedule-table")
            screenshot = await element.screenshot(type="png")

            logger.info(
                "Screenshot captured: %d bytes, viewport=%d, dpr=%d",
                len(screenshot),
                self._viewport_width,
                self._dpr,
            )
            return screenshot
        finally:
            await page.close()

    async def render_to_file(
        self, html_content: str, output_path: Path
    ) -> Path:
        """Render HTML and save the PNG to *output_path*.

        Returns the path to the written file.
        """
        png_bytes = await self.render(html_content)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(png_bytes)
        logger.info("Image saved to %s (%d bytes)", output_path, len(png_bytes))
        return output_path
