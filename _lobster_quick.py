#!/usr/bin/env python3
"""
龙虾终端快速同步工具 - 绕过 playwright，使用 AI 抓取+抽取公众号文章

用法:
  python _lobster_quick.py "https://mp.weixin.qq.com/s/..."

流程:
  1. 用 requests 尝试抓取（如果反爬，手动粘贴正文到 tmp.txt）
  2. 保存到 raw_material
  3. 调用 LLM（DeepSeek）抽取个股
  4. 合并到 stocks_master.json
  5. git push

前提: pip install openai requests pandas
"""
import json, os, re, sys
from datetime import date
from pathlib import Path
from openai import OpenAI

SKILL_DIR = Path(__file__).parent / ".trae" / "skills" / "wechat-fetch-research-embedded"
PROJECT = Path(__file__).parent

def load_config():
    with open(SKILL_DIR / "config.json") as f:
        return json.load(f)["api"]

def save_raw_material(url, content, title=""):
    today = date.today().isoformat()
    raw_path = SKILL_DIR / "raw_material" / f"raw_material_{today}.md"
    raw_path.parent.mkdir(exist_ok=True)
    with open(raw_path, "a", encoding="utf-8") as f:
        f.write(f"## Article\nsource: {url}\nfetched_at: {today}\ntitle: {title}\ndate: {today}\n\n{content}\n\n---\n")
    print(f"[OK] raw_material saved to {raw_path}")
    return str(raw_path)

def main():
    if len(sys.argv) < 2:
        print("用法: python _lobster_quick.py '文章URL' [可选: 手动粘贴文本文件]")
        sys.exit(1)
    
    url = sys.argv[1]
    manual_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # 1. 获取文章内容
    content = ""
    if manual_file and os.path.exists(manual_file):
        with open(manual_file, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"[OK] 从 {manual_file} 读取文章")
    else:
        try:
            import requests
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            # 简单提取正文（从 rich_media_content 或 js_content）
            text = r.text
            m = re.search(r'var msg_title\s*=\s*"([^"]+)"', text)
            title = m.group(1) if m else ""
            m = re.search(r'var msg_cdn_url\s*=\s*"([^"]+)"', text)
            print(f"[INFO] 标题: {title}")
            # 尝试提取正文 - 微信公众号正文在 #js_content 或 .rich_media_content
            m = re.search(r'id="js_content"[^>]*>(.*?)</div>\s*<script', text, re.DOTALL)
            if not m:
                m = re.search(r'class="rich_media_content[^"]*"[^>]*>(.*?)</div>', text, re.DOTALL)
            if m:
                content = re.sub(r'<[^>]+>', '', m.group(1))  # strip HTML
                content = re.sub(r'\s+', ' ', content).strip()
                print(f"[OK] 抓取到 {len(content)} 字")
            else:
                print("[WARN] 未找到正文，请手动粘贴内容到 tmp.txt 然后: python _lobster_quick.py URL tmp.txt")
                sys.exit(1)
        except Exception as e:
            print(f"[ERR] 抓取失败: {e}")
            print("请手动粘贴文章内容到 tmp.txt 然后: python _lobster_quick.py URL tmp.txt")
            sys.exit(1)
    
    # 2. 保存 raw_material
    raw_path = save_raw_material(url, content)
    
    # 3. LLM 抽取
    config = load_config()
    client = OpenAI(api_key=config["api_key"], base_url=config["base_url"])
    
    # 读取股票列表
    import pandas as pd
    xls_path = SKILL_DIR / "assets" / "全部个股.xls"
    stocks_df = pd.read_excel(xls_path)
    stock_names = set(stocks_df["股票简称"].dropna().tolist())
    
    # 先从文本中找到提到的个股
    mentioned = [n for n in stock_names if n in content and len(n) >= 2]
    print(f"\n[INFO] 发现 {len(mentioned)} 只个股: {mentioned}")
    
    if not mentioned:
        print("[WARN] 未发现已知个股，跳过")
        return
    
    # 调用 LLM 抽取
    prompt = f"""从以下文章提取个股投研信息，返回 JSON。只提取以下提到的个股: {", ".join(mentioned)}

文章内容:
{content[:8000]}

对每只个股，提取（如无则填空数组）:
- accidents: 客观事件/进展（≤60字/条）
- insights: 投资逻辑/竞争优势
- key_metrics: 量化数据（每条必须包含数字）
- target_valuation: 估值/目标价（含具体数值）
- core_business: 核心业务
- industry_position: 行业地位
- chain: 产业链位置
- partners: 合作伙伴
- products: 产品

返回严格 JSON:
{{"stocks": [{{"code": "股票代码", "name": "股票名", "articles": [{{"source": "{url}", "title": "文章标题", "accidents": [], "insights": [], "key_metrics": [], "target_valuation": [], "core_business": [], "industry_position": [], "chain": [], "partners": [], "products": [], "concepts": []}}]}}]}}
"""
    
    print("\n[INFO] 调用 DeepSeek 抽取...")
    resp = client.chat.completions.create(
        model=config["model"],
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    result = json.loads(resp.choices[0].message.content)
    
    # 补全股票代码
    name_to_code = dict(zip(stocks_df["股票简称"], stocks_df["股票代码"].astype(str)))
    for s in result.get("stocks", []):
        if s.get("name") in name_to_code:
            s["code"] = name_to_code[s["name"]]
    
    # 4. 保存结果
    today = date.today().isoformat()
    out_path = PROJECT / "data" / f"stocks_master_{today}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[OK] 抽取结果保存到 {out_path}")
    
    # 5. 合并到主数据
    print("\n[INFO] 合并到 stocks_master.json...")
    sys.path.insert(0, str(SKILL_DIR / "scripts"))
    from merge_new_stocks import merge_new_stocks
    merge_new_stocks(today)
    
    # 6. Git push
    print("\n[INFO] 推送 GitHub...")
    os.chdir(PROJECT)
    os.system("git add data/stocks/")
    os.system(f'git commit -m "feat: add {len(mentioned)} stocks from wechat article"')
    os.system("git push origin main")
    print("\n[DONE] 完成！")

if __name__ == "__main__":
    main()
