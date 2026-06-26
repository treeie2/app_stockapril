#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch a WeChat article and append it into a raw_material markdown file.

Primary path: call an MCP tool (e.g., linkreaderplugin) via anygen-mcp-cli.
Because MCP server/tool names and schemas differ across environments, this script is designed
for *adaptive* extraction:
- It calls the specified MCP tool with JSON input containing the URL.
- It then tries to locate the main text/markdown/html in the response.

If MCP call fails, you can still use --manual_text_file to append a manually saved article.

Output format (append):

## Article
source: <url>
fetched_at: <iso>
(title and date optional)

<content>

---
"""

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nSTDERR:\n{p.stderr}\nSTDOUT:\n{p.stdout}")
    return p.stdout


def _extract_text_from_mcp_response(obj) -> tuple[str, dict]:
    """Return (content_text, meta). Meta may include title/date if discoverable."""

    meta = {}

    # Common shapes:
    # {success: true, data: {...}}
    if isinstance(obj, dict) and "data" in obj and obj.get("success") is True:
        obj = obj["data"]

    # If direct string
    if isinstance(obj, str):
        return obj.strip(), meta

    # Heuristic search in nested dict/list
    candidates = []

    def walk(x, path=""):
        if isinstance(x, dict):
            for k, v in x.items():
                p2 = f"{path}.{k}" if path else str(k)
                if k.lower() in {"title", "article_title"} and isinstance(v, str) and v.strip():
                    meta.setdefault("title", v.strip())
                if k.lower() in {"date", "publish_date", "published_at"} and isinstance(v, str) and v.strip():
                    meta.setdefault("date", v.strip())
                walk(v, p2)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                walk(v, f"{path}[{i}]")
        else:
            if isinstance(x, str):
                s = x.strip()
                if len(s) >= 200:  # avoid tiny strings like ids
                    candidates.append((len(s), path, s))

    walk(obj)

    # Prefer markdown/text keys if present
    if isinstance(obj, dict):
        for key in ["markdown", "text", "content", "article", "body", "html"]:
            v = obj.get(key)
            if isinstance(v, str) and len(v.strip()) >= 50:
                return v.strip(), meta

    if candidates:
        candidates.sort(reverse=True)
        return candidates[0][2], meta

    return "", meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="WeChat URL: https://mp.weixin.qq.com/s/... or /s?__biz=...")
    ap.add_argument("--out", required=True, help="Output raw_material markdown file")
    ap.add_argument("--mcp_server", default="", help="MCP server name that hosts linkreaderplugin")
    ap.add_argument("--mcp_tool", default="", help="MCP tool name to call")
    ap.add_argument(
        "--mcp_input_key",
        default="url",
        help="Key name for URL in MCP tool input JSON (default: url)",
    )
    ap.add_argument(
        "--manual_text_file",
        default="",
        help="If provided, skip MCP and append this file's content as article body",
    )
    args = ap.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fetched_at = dt.datetime.now().astimezone().isoformat(timespec="seconds")

    content = ""
    meta = {}

    if args.manual_text_file:
        content = Path(args.manual_text_file).read_text(encoding="utf-8").strip()
    else:
        if not args.mcp_server or not args.mcp_tool:
            raise SystemExit(
                "MCP server/tool not provided. Provide --mcp_server and --mcp_tool, or use --manual_text_file."
            )

        payload = {args.mcp_input_key: args.url}
        stdout = _run(
            [
                "anygen-mcp-cli",
                "tool",
                "call",
                args.mcp_tool,
                "--server",
                args.mcp_server,
                "--input",
                json.dumps(payload, ensure_ascii=False),
            ]
        )
        try:
            resp = json.loads(stdout)
        except Exception as e:
            raise RuntimeError(f"Failed to parse MCP response as JSON: {e}\nRAW:\n{stdout[:2000]}")

        content, meta = _extract_text_from_mcp_response(resp)

        if not content:
            raise RuntimeError(
                "MCP call succeeded but no usable text found in response. "
                "Inspect the tool schema with `anygen-mcp-cli tool get ...` and adjust --mcp_input_key, "
                "or use --manual_text_file."
            )

    # Normalize content a bit
    content = content.replace("\r\n", "\n").strip()

    lines = []
    lines.append("## Article")
    lines.append(f"source: {args.url}")
    lines.append(f"fetched_at: {fetched_at}")
    if meta.get("title"):
        lines.append(f"title: {meta['title']}")
    if meta.get("date"):
        lines.append(f"date: {meta['date']}")
    lines.append("")
    lines.append(content)
    lines.append("")
    lines.append("---")
    lines.append("")

    with out_path.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(str(out_path))


if __name__ == "__main__":
    main()
