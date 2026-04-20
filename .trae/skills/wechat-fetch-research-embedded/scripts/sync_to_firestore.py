#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sync stocks_master JSON to Firebase Firestore.

This script writes:
1) Per-article full payload to subcollection: `stocks/{code}/articles/{article_id}`
2) Per-stock parent doc also keeps an `articles` ARRAY of article summaries (for fast UI listing)

Article summary format (as requested):
{
  "title": "文章标题",
  "date": "2026-04-05",
  "source": "https://...",
  "accidents": ["催化剂1", "催化剂2"],
  "insights": ["洞察1"],
  "key_metrics": ["指标1"]
}

on_exists behavior (when article_id already exists in subcollection)
- skip: do nothing
- update: set(merge=True) with NEW payload
- merge: smart merge existing + new

⚠️ About parent `articles` array updates
Firestore ArrayUnion cannot "update" an existing array element (it only adds if the exact element is absent).
Because you require **"保留原有字段，补充新的字段，更新冲突字段"**, this script updates the parent
`articles` array by reading it inside the same transaction and replacing the element matched by `source`.

Usage
  python scripts/sync_to_firestore.py \
    --credentials "/path/firebase-credentials.json" \
    --json "data/stocks_master_YYYY-MM-DD.json" \
    --collection "stocks" \
    --article_subcollection "articles" \
    --on_exists merge
"""

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List

import firebase_admin
from firebase_admin import credentials, firestore


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_url(url: str) -> str:
    return str(url or "").replace("\\_", "_").strip()


def is_code(code: str) -> bool:
    return bool(re.fullmatch(r"\d{6}", str(code or "").strip()))


def sha1_hex(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def normalize_article(a: Dict[str, Any]) -> Dict[str, Any]:
    a = dict(a or {})
    a["source"] = normalize_url(a.get("source"))
    a["title"] = str(a.get("title") or "").strip()
    a["date"] = str(a.get("date") or "").strip()

    for k in ["accidents", "insights", "key_metrics", "target_valuation"]:
        v = a.get(k, [])
        if not isinstance(v, list):
            v = []
        a[k] = [str(x).strip() for x in v if str(x).strip()]

    return a


def article_summary(a2: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": a2.get("title", ""),
        "date": a2.get("date", ""),
        "source": a2.get("source", ""),
        "accidents": a2.get("accidents", []) or [],
        "insights": a2.get("insights", []) or [],
        "key_metrics": a2.get("key_metrics", []) or [],
    }


def stock_meta_payload(s: Dict[str, Any]) -> Dict[str, Any]:
    """Write minimal stock fields; does not include articles."""
    payload = {}
    for k in [
        "name",
        "code",
        "board",
        "industry",
        "concepts",
        "products",
        "core_business",
        "industry_position",
        "chain",
        "partners",
    ]:
        if k in s:
            payload[k] = s[k]

    # ensure arrays
    for k in ["concepts", "products", "core_business", "industry_position", "chain", "partners"]:
        v = payload.get(k, [])
        payload[k] = v if isinstance(v, list) else []

    return payload


def _is_empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        return v.strip() == ""
    if isinstance(v, (list, dict)):
        return len(v) == 0
    return False


def _dedup_list(lst: List[Any]) -> List[Any]:
    out = []
    seen = set()
    for x in lst:
        key = json.dumps(x, ensure_ascii=False, sort_keys=True) if isinstance(x, (dict, list)) else str(x)
        if key in seen:
            continue
        seen.add(key)
        out.append(x)
    return out


def smart_merge(old: Any, new: Any) -> Any:
    """Recursively merge two JSON-like objects with 'prefer new when non-empty' semantics."""
    if isinstance(old, dict) and isinstance(new, dict):
        merged = dict(old)
        for k, nv in new.items():
            if k not in merged:
                merged[k] = nv
                continue
            ov = merged[k]
            merged[k] = smart_merge(ov, nv)
        return merged

    if isinstance(old, list) and isinstance(new, list):
        # union, keep order: old first, then new
        return _dedup_list(list(old) + list(new))

    # scalar or type mismatch: prefer new if non-empty
    if _is_empty(new):
        return old
    return new


def merge_article_array(existing: Any, new_item: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Merge/Upsert one article summary into the parent's articles array by matching source."""
    arr: List[Dict[str, Any]] = []
    if isinstance(existing, list):
        for x in existing:
            if isinstance(x, dict):
                arr.append(dict(x))

    src = str(new_item.get("source") or "")
    if not src:
        return arr

    found = False
    for i, it in enumerate(arr):
        if str(it.get("source") or "") == src:
            arr[i] = smart_merge(it, new_item)
            found = True
            break

    if not found:
        arr.append(new_item)

    return arr


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--credentials", required=True, help="Firebase service account JSON path")
    ap.add_argument("--json", required=True, help="stocks_master JSON file path")
    ap.add_argument("--collection", default="stocks", help="Top-level collection name")
    ap.add_argument("--article_subcollection", default="articles")
    ap.add_argument("--on_exists", choices=["skip", "update", "merge"], default="skip")
    ap.add_argument("--dry_run", action="store_true")
    args = ap.parse_args()

    cred = credentials.Certificate(args.credentials)
    app = firebase_admin.initialize_app(cred)
    db = firestore.client(app)

    data = load_json(args.json)
    stocks = data.get("stocks", []) if isinstance(data, dict) else []
    if not isinstance(stocks, list):
        raise SystemExit("Invalid JSON: expect {stocks:[...]} ")

    total_stocks = 0
    total_articles = 0
    created_articles = 0
    updated_articles = 0
    merged_articles = 0
    parent_articles_upserts = 0

    for s in stocks:
        if not isinstance(s, dict):
            continue
        code = str(s.get("code", "")).strip()
        name = str(s.get("name", "")).strip()
        if not is_code(code):
            continue

        total_stocks += 1
        stock_ref = db.collection(args.collection).document(code)

        # Upsert stock metadata (merge only touches provided fields).
        meta = stock_meta_payload(s)
        if args.dry_run:
            print(f"DRY_RUN stock {code} {name} meta_keys={list(meta.keys())}")
        else:
            stock_ref.set(meta, merge=True)

        articles = s.get("articles", []) or []
        if not isinstance(articles, list):
            continue

        for a in articles:
            if not isinstance(a, dict):
                continue
            a2 = normalize_article(a)
            src = a2.get("source", "")
            if not src:
                continue

            total_articles += 1
            article_id = sha1_hex(src)
            art_ref = stock_ref.collection(args.article_subcollection).document(article_id)
            summary = article_summary(a2)

            if args.dry_run:
                print(f"DRY_RUN article {code}/{article_id} source={src[:80]}")
                continue

            @firestore.transactional
            def tx_write(tx: firestore.Transaction):
                # Read both docs in the same transaction
                art_snap = art_ref.get(transaction=tx)
                stock_snap = stock_ref.get(transaction=tx)

                # 1) write subcollection doc
                if art_snap.exists:
                    if args.on_exists == "update":
                        tx.set(art_ref, a2, merge=True)
                        art_res = "updated"
                    elif args.on_exists == "merge":
                        old = art_snap.to_dict() or {}
                        merged = smart_merge(old, a2)
                        tx.set(art_ref, merged, merge=False)
                        art_res = "merged"
                    else:
                        art_res = "skipped"
                else:
                    tx.set(art_ref, a2, merge=False)
                    # increment counters only when new article created
                    tx.set(
                        stock_ref,
                        {
                            "article_count": firestore.Increment(1),
                            "mention_count": firestore.Increment(1),
                        },
                        merge=True,
                    )
                    art_res = "created"

                # 2) update parent doc's `articles` array (smart upsert by source)
                stock_old = stock_snap.to_dict() or {}
                new_arr = merge_article_array(stock_old.get("articles"), summary)
                tx.set(stock_ref, {"articles": new_arr}, merge=True)

                return art_res

            res = tx_write(db.transaction())
            parent_articles_upserts += 1

            if res == "created":
                created_articles += 1
            elif res == "updated":
                updated_articles += 1
            elif res == "merged":
                merged_articles += 1

    print(
        json.dumps(
            {
                "collection": args.collection,
                "article_subcollection": args.article_subcollection,
                "stocks": total_stocks,
                "articles_total": total_articles,
                "articles_created": created_articles,
                "articles_updated": updated_articles,
                "articles_merged": merged_articles,
                "parent_articles_upserts": parent_articles_upserts,
                "on_exists": args.on_exists,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
