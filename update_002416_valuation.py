#!/usr/bin/env python3
"""
为爱施德 (002416) 添加 valuation 字段到 Firebase
"""
import requests
import json

FIREBASE_PROJECT_ID = "webstock-724"
FIREBASE_BASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"

def update_aishaide_valuation():
    print("为爱施德 (002416) 添加估值信息...\n")
    
    # 爱施德的估值数据（根据沸点文章中的信息）
    valuation_data = {
        "target_market_cap": "800 亿",  # 根据文章中的目标市值
        "target_market_cap_billion": 800.0
    }
    
    doc_url = f"{FIREBASE_BASE_URL}/stocks/002416"
    
    firestore_data = {
        "fields": {
            "valuation": {
                "mapValue": {
                    "fields": {
                        "target_market_cap": {
                            "stringValue": valuation_data["target_market_cap"]
                        },
                        "target_market_cap_billion": {
                            "doubleValue": valuation_data["target_market_cap_billion"]
                        }
                    }
                }
            }
        }
    }
    
    print(f"更新数据：{json.dumps(firestore_data, indent=2, ensure_ascii=False)}\n")
    
    try:
        resp = requests.patch(doc_url, json=firestore_data, timeout=10)
        
        if resp.status_code in [200, 201]:
            print("✅ 更新成功！")
            print(f"   HTTP 状态码：{resp.status_code}")
        else:
            print(f"❌ 更新失败：HTTP {resp.status_code}")
            print(f"   响应：{resp.text}")
    except Exception as e:
        print(f"❌ 请求失败：{e}")

if __name__ == "__main__":
    update_aishaide_valuation()
