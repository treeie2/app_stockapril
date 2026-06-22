#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch WeChat article content via mobile User-Agent (requests).

Uses mobile UA to get the simplified mobile page, then extracts article text.
Much simpler than Playwright approach, works for most non-protected articles.

Usage:
  python scripts/fetch_wechat_mobile.py \
    --url "https://mp.weixin.qq.com/s/..." \
    --out_text "tmp_article.txt"

  # Multiple URLs at once:
  python scripts/fetch_wechat_mobile.py \
    --url "url1" --url "url2" --url "url3" \
    --out_dir "raw_material/"

Output:
  - Single URL: plain text file with title + date + content
  - Multiple URLs: one file per URL in --out_dir, named by article title
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs

try:
    import requests
except ImportError:
    print("ERROR: requests not installed. Run: pip install requests")
    sys.exit(1)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
}

# Timeout for each request (seconds)
REQUEST_TIMEOUT = 15


def extract_var_from_html(html: str, var_name: str) -> str:
    """Extract a JS variable value from WeChat HTML page.

    WeChat pages contain vars like:
      var msg_title = "文章标题";
      var publish_time = "1718908800";
      var content = "<p>...</p>";
    """
    # Try single-quoted
    pattern_sq = re.compile(rf'var\s+{var_name}\s*=\s*\'([^\']*)\'', re.DOTALL)
    m = pattern_sq.search(html)
    if m:
        return m.group(1)

    # Try double-quoted
    pattern_dq = re.compile(rf'var\s+{var_name}\s*=\s*"([^"]*)"', re.DOTALL)
    m = pattern_dq.search(html)
    if m:
        return m.group(1)

    return ""


def clean_html(html_content: str) -> str:
    """Remove HTML tags and clean up whitespace."""
    # Replace common block elements with newlines
    text = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)
    text = re.sub(r'</(p|div|h[1-6]|li|tr|section|article)>', '\n', text, flags=re.IGNORECASE)
    # Remove all remaining tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&amp;', '&').replace('&quot;', '"').replace('&#39;', "'")
    # Collapse whitespace
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()


def fetch_article(url: str) -> dict:
    """Fetch a single WeChat article and return structured data.

    Returns:
        {
            "title": str,
            "date": str (YYYY-MM-DD),
            "author": str,
            "content": str (plain text),
            "url": str,
            "success": bool,
            "error": str or None
        }
    """
    result = {
        "title": "",
        "date": "",
        "author": "",
        "content": "",
        "url": url,
        "success": False,
        "error": None,
    }

    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        resp.encoding = "utf-8"

        if resp.status_code != 200:
            result["error"] = f"HTTP {resp.status_code}"
            return result

        html = resp.text

        # Check if we got a verification/captcha page
        if "环境异常" in html or "wappoc_appmsgcaptcha" in html:
            result["error"] = "CAPTCHA/verification page detected. Use Playwright approach or manual paste."
            return result

        # Check if we got actual article content
        if "js_content" not in html and "rich_media_content" not in html:
            result["error"] = "No article content found in HTML. May be blocked."
            return result

        # Extract title
        title = extract_var_from_html(html, "msg_title")
        if not title:
            # Fallback: <h1 id="activity-name">
            m = re.search(r'<h1[^>]*id="activity-name"[^>]*>([^<]+)</h1>', html)
            title = m.group(1).strip() if m else ""
        if not title:
            # Fallback: og:title
            m = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', html)
            title = m.group(1).strip() if m else ""
        result["title"] = title

        # Extract publish time
        pub_time_str = extract_var_from_html(html, "publish_time") or extract_var_from_html(html, "ct")
        if pub_time_str and pub_time_str.isdigit():
            try:
                ts = int(pub_time_str)
                from datetime import datetime, timezone
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                # Convert to Asia/Shanghai (UTC+8)
                from datetime import timedelta
                dt_cn = dt + timedelta(hours=8)
                result["date"] = dt_cn.strftime("%Y-%m-%d")
            except Exception:
                pass

        # Fallback: extract date from page text
        if not result["date"]:
            m = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', html)
            if m:
                result["date"] = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"

        # Extract author/account name
        author = extract_var_from_html(html, "nickname")
        if not author:
            m = re.search(r'<a[^>]*id="js_name"[^>]*>([^<]+)</a>', html)
            author = m.group(1).strip() if m else ""
        result["author"] = author

        # Extract article body content
        # Method 1: var content = "..."
        content_html = extract_var_from_html(html, "content")
        if content_html:
            result["content"] = clean_html(content_html)
        else:
            # Method 2: extract from #js_content div
            m = re.search(r'<div[^>]*id="js_content"[^>]*>(.*?)</div>\s*<script', html, re.DOTALL)
            if m:
                result["content"] = clean_html(m.group(1))
            else:
                # Method 3: rich_media_content
                m = re.search(r'<div[^>]*class="rich_media_content"[^>]*>(.*?)</div>', html, re.DOTALL)
                if m:
                    result["content"] = clean_html(m.group(1))
                else:
                    result["error"] = "Could not extract article body content"
                    return result

        result["success"] = True
        return result

    except requests.exceptions.Timeout:
        result["error"] = f"Request timeout after {REQUEST_TIMEOUT}s"
        return result
    except Exception as e:
        result["error"] = str(e)
        return result


def save_article(article: dict, out_path: Path):
    """Save article to a text file."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    if article.get("title"):
        lines.append(f"title: {article['title']}")
    if article.get("date"):
        lines.append(f"date: {article['date']}")
    if article.get("author"):
        lines.append(f"author: {article['author']}")
    if article.get("url"):
        lines.append(f"source: {article['url']}")
    lines.append("")
    if article.get("content"):
        lines.append(article["content"])
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Saved: {out_path}")


def sanitize_filename(name: str, max_len: int = 60) -> str:
    """Convert article title to a safe filename."""
    name = re.sub(r'[\\/:*?"<>|\s]+', '_', name)
    name = re.sub(r'_+', '_', name).strip('_')
    return name[:max_len] if name else "untitled"


def main():
    ap = argparse.ArgumentParser(description="Fetch WeChat article via mobile UA")
    ap.add_argument("--url", action="append", required=True, help="WeChat article URL (can specify multiple)")
    ap.add_argument("--out_text", help="Output file path (single URL mode)")
    ap.add_argument("--out_dir", help="Output directory (multi URL mode)")
    ap.add_argument("--delay", type=float, default=1.5, help="Delay between requests in seconds (default: 1.5)")
    ap.add_argument("--timeout", type=int, default=15, help="Request timeout in seconds (default: 15)")
    args = ap.parse_args()

    global REQUEST_TIMEOUT
    REQUEST_TIMEOUT = args.timeout

    urls = args.url
    print(f"Fetching {len(urls)} article(s)...")

    results = []
    for i, url in enumerate(urls):
        if i > 0:
            time.sleep(args.delay)
        print(f"\n[{i+1}/{len(urls)}] {url}")
        article = fetch_article(url)
        results.append(article)

        if article["success"]:
            print(f"  Title: {article['title']}")
            print(f"  Date: {article['date']}")
            print(f"  Author: {article['author']}")
            print(f"  Content length: {len(article['content'])} chars")
        else:
            print(f"  ERROR: {article['error']}")

    # Save results
    if len(urls) == 1 and args.out_text:
        # Single URL mode
        article = results[0]
        if article["success"]:
            save_article(article, Path(args.out_text))
            print(f"\nDone! Saved to {args.out_text}")
        else:
            print(f"\nFailed: {article['error']}")
            sys.exit(1)
    else:
        # Multi URL mode
        out_dir = Path(args.out_dir) if args.out_dir else Path(".")
        success_count = 0
        for article in results:
            if article["success"]:
                fname = sanitize_filename(article["title"] or "untitled")
                # Add date prefix if available
                if article["date"]:
                    fname = f"{article['date']}_{fname}"
                out_path = out_dir / f"{fname}.txt"
                save_article(article, out_path)
                success_count += 1
            else:
                print(f"  Skipped (error): {article['error']}")

        print(f"\nDone! {success_count}/{len(urls)} articles saved to {out_dir}/")

    # Print summary
    print("\n--- Summary ---")
    for i, r in enumerate(results):
        status = "OK" if r["success"] else "FAIL"
        title = r.get("title", "")[:40]
        print(f"  [{status}] {title}")


if __name__ == "__main__":
    main()
