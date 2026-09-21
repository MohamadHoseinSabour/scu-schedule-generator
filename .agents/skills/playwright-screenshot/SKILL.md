---
name: playwright-screenshot
description: High-DPI headless Chromium screenshot generation rules, element clipping, and offline font rendering strategies.
---

# Playwright Screenshot Skill

This skill explains how to render and screenshot HTML tables into crisp, mobile-ready PNGs using Playwright Chromium in backend tasks.

## 1. High-DPI Device Scale Factor
For crisp mobile display without blurred text:
- Set `device_scale_factor=2` (Retina 2x).
- Set viewport width appropriately (e.g., `width=1800` to `2000`).

```python
page = await browser.new_page(
    viewport={"width": 1800, "height": 1200},
    device_scale_factor=2
)
```

## 2. Waiting for Fonts and Network Idle
Before taking the screenshot:
- Load content: `await page.set_content(html, wait_until="networkidle")`
- Explicit wait for font rendering: `await page.wait_for_timeout(400)`

## 3. Element-Only Screenshot
Never capture the whole window if only the table is required:
```python
element = page.locator("#schedule-table")
png_bytes = await element.screenshot(type="png")
```

## 4. Keeping Server Image and Client HTML Aligned
Ensure that both client-side HTML preview and server-side PNG rendering use the identical canonical data model and color mapping.
