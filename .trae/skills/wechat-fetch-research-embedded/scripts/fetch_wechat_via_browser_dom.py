#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch WeChat article content via a real browser (Playwright) and extract DOM text.

Why this exists:
- WeChat public articles often use anti-bot / verification pages.
- Pure HTTP scraping is frequently blocked or returns incomplete content.

This script does NOT try to bypass WeChat protections. Instead it uses a *real browser*
with a persistent profile (cookies), and optionally waits for the user to complete
verification/login when required.

Workflow:
1) First run: it opens Chromium with a persistent profile directory.
   - You may need to login / click "去验证" manually.
2) The script waits until the page contains #js_content, then extracts innerText.
3) Saves extracted text to --out_text (UTF-8).

Usage:
  python scripts/fetch_wechat_via_browser_dom.py \
    --url "https://mp.weixin.qq.com/s/..." \
    --out_text "tmp_article.txt" \
    --user_data_dir ".browser_profile" \
    --timeout 300

Then pipe it into raw_material appender:
  python scripts/fetch_wechat_to_raw_material.py --url "..." --out "raw_material/raw_material_YYYY-MM-DD.md" --manual_text_file "tmp_article.txt"
"""

import argparse
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


async def main_async(url: str, out_text: str, user_data_dir: str, timeout: int, headless: bool):
    out_path = Path(out_text)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            viewport={"width": 1200, "height": 900},
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto(url, wait_until="domcontentloaded")

        # Wait for article content container. If verification is needed, user can complete it.
        try:
            await page.wait_for_selector("#js_content", timeout=timeout * 1000)
        except Exception:
            # Provide a clearer message
            raise RuntimeError(
                f"Timeout waiting for #js_content after {timeout}s. "
                "If you see a verification/login page, please complete it in the opened browser, "
                "then re-run with a larger --timeout, or keep the browser open and retry."
            )

        # Extract title/date if possible (optional)
        title = await page.evaluate(
            """() => {
              const t = document.querySelector('#activity-name');
              return t ? t.innerText.trim() : (document.title || '');
            }"""
        )
        date = await page.evaluate(
            """() => {
              const txt = document.body.innerText || '';
              const m = txt.match(/(20\\d{2})年(\\d{1,2})月(\\d{1,2})日/);
              if (!m) return '';
              const mm = String(m[2]).padStart(2,'0');
              const dd = String(m[3]).padStart(2,'0');
              return `${m[1]}-${mm}-${dd}`;
            }"""
        )

        content = await page.evaluate(
            """() => {
              const el = document.querySelector('#js_content');
              return el ? el.innerText.trim() : '';
            }"""
        )

        # Compose plain text output
        final_text = ""
        if title:
            final_text += f"title: {title}\n"
        if date:
            final_text += f"date: {date}\n"
        if final_text:
            final_text += "\n"
        final_text += content

        out_path.write_text(final_text, encoding="utf-8")
        await context.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--out_text", required=True)
    ap.add_argument("--user_data_dir", default=".browser_profile", help="Persistent browser profile for cookies")
    ap.add_argument("--timeout", type=int, default=300, help="Seconds to wait for article content")
    ap.add_argument("--headless", type=lambda x: x.lower() in ('true', '1', 'yes'), default=True, help="Run browser in headless mode (default: True)")
    args = ap.parse_args()

    asyncio.run(main_async(args.url, args.out_text, args.user_data_dir, args.timeout, args.headless))
    print(args.out_text)


if __name__ == "__main__":
    main()
