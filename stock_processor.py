#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个股数据处理脚本 - 支持终端标识和新增不覆盖

文件命名规则: yyyy-mm-dd_{terminal}.json
终端标识: tbox / trae

核心逻辑:
1. 生成日期分片文件时添加终端后缀
2. 更新 stocks_master.json 时只新增不覆盖
3. 在规范格式中记录处理终端信息
"""

import json
import os
from datetime import datetime
from pathlib import Path

class StockProcessor:
    def __init__(self, terminal="trae"):
        """
        初始化处理器
        :param terminal: 终端标识，可选值: tbox, trae
        """
        self.terminal = terminal.lower()
        if self.terminal not in ["tbox", "trae"]:
            raise ValueError("terminal must be 'tbox' or 'trae'")
        
        # 路径配置
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data" / "stocks"
        self.master_file = self.data_dir / "stocks_master.json"
        self.index_file = self.data_dir / "stocks_index.json"
        
        # 确保目录存在
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_date_file_name(self, date_str=None):
        """
        生成日期分片文件名
        :param date_str: 日期字符串，格式 yyyy-mm-dd，默认使用今天
        :return: 文件名，格式 yyyy-mm-dd_{terminal}.json
        """
        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")
        return f"{date_str}_{self.terminal}.json"
    
    def load_master(self):
        """加载 stocks_master.json，不存在则返回空结构"""
        if self.master_file.exists():
            with open(self.master_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"version": "2.4", "updated_at": "", "stocks": {}}
    
    def save_master(self, data):
        """保存 stocks_master.json"""
        data["updated_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
        with open(self.master_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_stocks_to_master(self, new_stocks, update_existing=False):
        """
        向 master 文件添加股票（只新增不覆盖）
        
        :param new_stocks: 新股票字典，格式 {code: stock_data}
        :param update_existing: 是否更新已存在的股票，默认 False（只新增）
        :return: 新增数量，更新数量
        """
        master = self.load_master()
        existing_codes = set(master["stocks"].keys())
        
        added_count = 0
        updated_count = 0
        
        for code, stock_data in new_stocks.items():
            # 确保股票代码是字符串
            code = str(code)
            
            if code in existing_codes:
                if update_existing:
                    # 合并更新：保留原有字段，补充新字段，更新冲突字段
                    existing = master["stocks"][code]
                    self._merge_stock_data(existing, stock_data)
                    updated_count += 1
                    print(f"🔄 更新：{code} - {stock_data.get('name', '')}")
                else:
                    # 不覆盖，跳过
                    print(f"⏭️  已存在，跳过：{code} - {stock_data.get('name', '')}")
            else:
                # 新增股票
                # 添加处理终端标识
                stock_data["processed_by"] = self.terminal
                stock_data["processed_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
                master["stocks"][code] = stock_data
                added_count += 1
                print(f"✅ 新增：{code} - {stock_data.get('name', '')}")
        
        self.save_master(master)
        return added_count, updated_count
    
    def _merge_stock_data(self, existing, new):
        """智能合并股票数据"""
        # 合并 articles
        if "articles" in new:
            if "articles" not in existing:
                existing["articles"] = []
            existing_articles = {a.get("source"): a for a in existing["articles"]}
            for article in new["articles"]:
                source = article.get("source")
                if source and source in existing_articles:
                    # 合并文章内容
                    existing_articles[source] = self._merge_article(existing_articles[source], article)
                elif source:
                    existing["articles"].append(article)
        
        # 合并列表字段
        list_fields = ["concepts", "products", "core_business", "industry_position", "chain", "partners"]
        for field in list_fields:
            if field in new and new[field]:
                if field not in existing:
                    existing[field] = []
                existing_set = set(existing[field])
                for item in new[field]:
                    if item not in existing_set:
                        existing[field].append(item)
        
        # 更新标量字段（只更新有值的）
        scalar_fields = ["name", "code", "board", "industry", "mention_count", "last_updated"]
        for field in scalar_fields:
            if field in new and new[field]:
                existing[field] = new[field]
        
        # 更新处理终端信息
        existing["processed_by"] = self.terminal
        existing["processed_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    
    def _merge_article(self, existing, new):
        """合并文章数据"""
        merged = dict(existing)
        for key, value in new.items():
            if isinstance(value, list):
                if key in merged and isinstance(merged[key], list):
                    merged[key] = list(set(merged[key] + value))
                else:
                    merged[key] = value
            elif value:
                merged[key] = value
        return merged
    
    def save_date_file(self, stocks_list, date_str=None):
        """
        保存日期分片文件
        
        :param stocks_list: 股票列表，格式 [{stock_data}, ...]
        :param date_str: 日期字符串
        :return: 保存的文件路径
        """
        filename = self.generate_date_file_name(date_str)
        filepath = self.data_dir / filename
        
        # 添加处理终端标识到文章级别
        for stock in stocks_list:
            if "articles" in stock:
                for article in stock["articles"]:
                    article["processed_by"] = self.terminal
        
        data = {
            "date": date_str or datetime.now().strftime("%Y-%m-%d"),
            "processed_by": self.terminal,
            "processed_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "stocks": stocks_list
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 保存日期文件: {filepath}")
        return filepath
    
    def load_from_date_files(self, terminal_filter=None):
        """
        从日期分片文件加载数据
        
        :param terminal_filter: 可选，只加载特定终端的数据（tbox/trae）
        :return: 股票字典
        """
        stocks = {}
        
        pattern = f"*_{terminal_filter}.json" if terminal_filter else "*.json"
        for filepath in sorted(self.data_dir.glob(pattern)):
            if filepath.name in ["stocks_master.json", "stocks_index.json", "stocks_from_firebase.json"]:
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 检查终端过滤
                if terminal_filter and data.get("processed_by") != terminal_filter:
                    continue
                
                for stock in data.get("stocks", []):
                    code = stock.get("code")
                    if code:
                        stocks[code] = stock
            except Exception as e:
                print(f"⚠️ 读取 {filepath} 失败: {e}")
        
        return stocks
    
    def sync_to_master_from_date_files(self, terminal_filter=None, update_existing=False):
        """
        从日期分片文件同步到 master
        
        :param terminal_filter: 可选，只同步特定终端的数据
        :param update_existing: 是否更新已存在的股票
        :return: 新增数量，更新数量
        """
        stocks = self.load_from_date_files(terminal_filter)
        if not stocks:
            print("📭 没有找到可同步的股票数据")
            return 0, 0
        
        print(f"\n📥 从日期文件加载到 {len(stocks)} 只股票")
        return self.add_stocks_to_master(stocks, update_existing)


# ==================== 使用示例 ====================
def example_usage():
    # 1. 创建处理器（指定终端）
    processor = StockProcessor(terminal="tbox")
    
    # 2. 示例股票数据
    new_stocks = {
        "688307": {
            "code": "688307",
            "name": "中润光学",
            "board": "科创板",
            "industry": "电子 - 光学光电子",
            "mention_count": 1,
            "last_updated": "2026-05-20",
            "articles": [{
                "title": "测试文章",
                "date": "2026-05-20",
                "source": "https://example.com",
                "accidents": ["催化剂1"],
                "insights": ["洞察1"],
                "key_metrics": ["指标1"],
                "target_valuation": []
            }]
        }
    }
    
    # 3. 添加到 master（只新增不覆盖）
    print("\n=== 添加股票到 master（只新增） ===")
    added, updated = processor.add_stocks_to_master(new_stocks)
    print(f"\n📊 结果: 新增 {added} 只, 更新 {updated} 只")
    
    # 4. 保存日期分片文件
    print("\n=== 保存日期文件 ===")
    stocks_list = [new_stocks["688307"]]
    processor.save_date_file(stocks_list)
    
    # 5. 从日期文件同步到 master
    print("\n=== 从日期文件同步到 master ===")
    added, updated = processor.sync_to_master_from_date_files(terminal_filter="tbox")
    print(f"\n📊 同步结果: 新增 {added} 只, 更新 {updated} 只")


if __name__ == "__main__":
    example_usage()