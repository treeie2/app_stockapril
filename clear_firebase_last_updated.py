import json
from pathlib import Path
from firebase_admin import credentials, firestore
import firebase_admin

print("=" * 60)
print("Firebase 数据清空脚本")
print("=" * 60)

# 收集三个文件涉及的股票代码
all_file_codes = set()

# 读取三个文件
for date in ["05-15", "05-16", "05-17"]:
    with open(f"e:/github/stock-research-backup/data/stocks_master_2026-{date}.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    stocks = data.get("stocks", [])
    if isinstance(stocks, list):
        for s in stocks:
            code = s.get("code", "")
            if code:
                all_file_codes.add(code)
    elif isinstance(stocks, dict):
        for code in stocks.keys():
            all_file_codes.add(code)

print(f"\n三个文件涉及: {len(all_file_codes)} 只股票")

# 初始化 Firebase
print("\n初始化 Firebase...")
creds_path = Path("e:/github/stock-research-backup/.trae/rules/firebase-credentials.json")
if not firebase_admin._apps:
    cred = credentials.Certificate(str(creds_path))
    firebase_admin.initialize_app(cred)
    print("✅ Firebase Admin SDK 初始化成功")

db = firestore.client()
print("✅ Firestore 客户端已连接")

# 清空 Firebase 中不在三个文件范围内的股票的 last_updated 字段
print(f"\n开始清空 Firebase 数据...")
print(f"将清空不在 {len(all_file_codes)} 只股票之外的所有股票的 last_updated 字段")

# 使用 batch 操作清空数据
batch = db.batch()
updates_count = 0
batch_size = 0
max_batch_size = 500  # Firestore 限制每个 batch 最多 500 个操作

try:
    # 获取所有股票文档
    stocks_ref = db.collection("stocks")
    
    # 使用 Stream API 遍历所有股票
    print("\n正在处理 Firebase 数据...")
    for doc in stocks_ref.stream():
        code = doc.id
        
        # 如果股票不在三个文件范围内，清空 last_updated
        if code not in all_file_codes:
            # 使用 update 而不是 set，避免覆盖其他字段
            doc_ref = db.collection("stocks").document(code)
            
            # 创建一个包含更新操作的 commit
            batch.update(doc_ref, {
                "last_updated": ""
            })
            
            updates_count += 1
            batch_size += 1
            
            # 当 batch 达到限制时，提交并创建新的 batch
            if batch_size >= max_batch_size:
                batch.commit()
                print(f"  已提交 {updates_count} 个更新...")
                batch = db.batch()
                batch_size = 0
    
    # 提交剩余的更新
    if batch_size > 0:
        batch.commit()
    
    print(f"\n✅ Firebase 数据清空完成！")
    print(f"总共清空了 {updates_count} 只股票的 last_updated 字段")
    
    # 验证
    print("\n验证 Firebase 数据...")
    remaining_with_date = 0
    remaining_empty = 0
    
    for doc in stocks_ref.stream():
        lu = doc.to_dict().get("last_updated", "")
        if lu:
            remaining_with_date += 1
        else:
            remaining_empty += 1
    
    print(f"Firebase 中:")
    print(f"  有 last_updated 值的股票: {remaining_with_date} 只")
    print(f"  last_updated 为空的股票: {remaining_empty} 只")
    
    # 显示还有 last_updated 值的股票
    if remaining_with_date > 0:
        print(f"\n还有 last_updated 值的股票:")
        count = 0
        for doc in stocks_ref.stream():
            lu = doc.to_dict().get("last_updated", "")
            if lu:
                print(f"  {doc.id}: {lu}")
                count += 1
                if count >= 20:
                    print(f"  ... (还有 {remaining_with_date - 20} 只)")
                    break

except Exception as e:
    print(f"\n❌ 操作失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("操作完成")
print("=" * 60)