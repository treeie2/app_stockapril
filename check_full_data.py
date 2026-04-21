#!/usr/bin/env python3
import json

with open('data/master/stocks_master.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

stock = data.get('002046', {})
print("=== 002046 国机精工 完整数据 ===\n")
print(f"Name: {stock.get('name')}")
print(f"Code: {stock.get('code')}")
print(f"Board: {stock.get('board')}")
print(f"Industry: '{stock.get('industry', 'EMPTY')}'")
print(f"Concepts: {stock.get('concepts', [])}")
print(f"Products: {stock.get('products', [])}")
print(f"Core Business: {stock.get('core_business', [])}")
print(f"Industry Position: {stock.get('industry_position', [])}")
print(f"Chain: {stock.get('chain', [])}")
print(f"Partners: {stock.get('partners', [])}")
print(f"Mention Count: {stock.get('mention_count')}")
print(f"\nArticles ({len(stock.get('articles', []))}):")
for i, article in enumerate(stock.get('articles', []), 1):
    print(f"  {i}. Title: '{article.get('title', 'EMPTY')}'")
    print(f"     Date: {article.get('date')}")
    print(f"     Source: '{article.get('source', 'EMPTY')}'")
    print(f"     Target Valuation: {article.get('target_valuation', [])}")
    print()
