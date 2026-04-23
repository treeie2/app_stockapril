#!/usr/bin/env python3
"""
同步今天更新的股票到 Firebase
"""
import json
import requests
from pathlib import Path
from datetime import datetime

# Firebase 配置
FIREBASE_PROJECT_ID = "webstock-724"
FIREBASE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"

# 文件路径
BASE_DIR = Path(__file__).parent
TODAY_FILE = BASE_DIR / 'data' / 'master' / 'stocks' / '2026-04-23.json'

def load_json(file_path):
    """加载 JSON 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载 {file_path} 失败：{e}")
        return None

def sync_to_firebase(stocks_dict):
    """同步股票数据到 Firebase"""
    print(f"\n🚀 开始同步到 Firebase...\n")
    
    base_url = f"{FIREBASE_BASE_URL}/stocks"
    sync_count = 0
    errors = []
    
    for code, stock in stocks_dict.items():
        try:
            # 构建文档路径
            doc_url = f"{base_url}/{code}"
            
            # 转换数据为 Firestore 格式
            firestore_data = {
                "fields": {
                    "name": {"stringValue": stock.get("name", "")},
                    "code": {"stringValue": code},
                    "board": {"stringValue": stock.get("board", "")},
                    "industry": {"stringValue": stock.get("industry", "")},
                    "mention_count": {"integerValue": str(stock.get("mention_count", 0))},
                    "last_updated": {"stringValue": stock.get("last_updated", "")},
                    "updated_at": {"timestampValue": datetime.now().isoformat() + "Z"}
                }
            }
            
            # 添加估值信息
            valuation = stock.get("valuation", {})
            if valuation:
                if valuation.get("target_market_cap"):
                    firestore_data["fields"]["target_market_cap"] = {
                        "stringValue": valuation.get("target_market_cap", "")
                    }
                if valuation.get("target_market_cap_billion"):
                    firestore_data["fields"]["target_market_cap_billion"] = {
                        "doubleValue": float(valuation.get("target_market_cap_billion", 0))
                    }
            
            # 添加概念数组
            concepts = stock.get("concepts", [])
            if concepts:
                firestore_data["fields"]["concepts"] = {
                    "arrayValue": {
                        "values": [{"stringValue": c} for c in concepts]
                    }
                }
            
            # 添加文章数组
            articles = stock.get("articles", [])
            if articles:
                article_values = []
                for article in articles:
                    article_fields = {
                        "title": {"stringValue": article.get("title", "")},
                        "date": {"stringValue": article.get("date", "")},
                        "source": {"stringValue": article.get("source", "")}
                    }
                    
                    # 添加洞察
                    insights = article.get("insights", [])
                    if insights:
                        article_fields["insights"] = {
                            "arrayValue": {
                                "values": [{"stringValue": i} for i in insights]
                            }
                        }
                    
                    # 添加事故
                    accidents = article.get("accidents", [])
                    if accidents:
                        article_fields["accidents"] = {
                            "arrayValue": {
                                "values": [{"stringValue": a} for a in accidents]
                            }
                        }
                    
                    # 添加关键指标
                    key_metrics = article.get("key_metrics", [])
                    if key_metrics:
                        article_fields["key_metrics"] = {
                            "arrayValue": {
                                "values": [{"stringValue": m} for m in key_metrics]
                            }
                        }
                    
                    article_values.append({
                        "mapValue": {
                            "fields": article_fields
                        }
                    })
                
                firestore_data["fields"]["articles"] = {
                    "arrayValue": {"values": article_values}
                }
            
            # 发送到 Firestore
            resp = requests.patch(doc_url, json=firestore_data, timeout=10)
            if resp.status_code in [200, 201]:
                sync_count += 1
                print(f"  ✅ {code} - {stock.get('name', '')}")
            else:
                errors.append(f"{code}: HTTP {resp.status_code}")
                print(f"  ❌ {code} - HTTP {resp.status_code}")
                
        except Exception as e:
            errors.append(f"{code}: {str(e)}")
            print(f"  ❌ {code} - {str(e)}")
    
    print(f"\n✅ 同步完成！")
    print(f"   - 成功：{sync_count} 只")
    print(f"   - 失败：{len(errors)} 只")
    
    if errors:
        print(f"\n错误详情：")
        for error in errors[:5]:
            print(f"   - {error}")
    
    return {
        'success': True,
        'synced_count': sync_count,
        'total_stocks': len(stocks_dict),
        'errors': errors
    }

def main():
    print("📋 加载今天更新的股票数据...\n")
    
    # 加载今天的数据
    today_data = load_json(TODAY_FILE)
    if not today_data:
        print("❌ 未找到今天的数据文件")
        return
    
    stocks = today_data.get('stocks', {})
    print(f"找到 {len(stocks)} 只股票\n")
    
    # 同步到 Firebase
    sync_to_firebase(stocks)
    
    print(f"\n💡 下一步：提交并推送到 GitHub")
    print(f"   git add -A")
    print(f"   git commit -m '更新 2026-04-23 个股数据（磷化铟、TGV 等）'")
    print(f"   git push origin main")

if __name__ == '__main__':
    main()
