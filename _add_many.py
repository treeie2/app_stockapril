import json, urllib.request, time

K = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZjbnp3aGpwemZvamVzenpseWVvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE5Mzc0MTUsImV4cCI6MjA5NzUxMzQxNX0.X44fD4gto39L4Wv6S4y05iukKqxuKudnTZS1PASyj1I"
U = "https://fcnzwhjpzfojeszzlyeo.supabase.co"
now = time.strftime("%Y-%m-%d")

new_groups = [
    ("陶瓷零部件", "珂玛科技、先锋精科。", "#f97316", "🔩", ["珂玛科技","先锋精科"]),
    ("光刻胶", "彤程新材、鼎龙股份、上海新阳。", "#8b5cf6", "🧪", ["彤程新材","鼎龙股份","上海新阳"]),
    ("石英件", "凯德石英。", "#06b6d4", "💎", ["凯德石英"]),
    ("测试机", "长川科技、华峰测控、精智达。", "#6366f1", "🔬", ["长川科技","华峰测控","精智达"]),
    ("靶材", "江丰电子、欧莱新材、阿石创。", "#ef4444", "🎯", ["江丰电子","欧莱新材","阿石创"]),
    ("掩膜版", "路维光电、清溢光电。", "#14b8a6", "🖼️", ["路维光电","清溢光电"]),
    ("划片机", "光力科技。", "#a855f7", "⚙️", ["光力科技"]),
    ("硅零部件/硅材料", "神工股份。", "#3b82f6", "🪨", ["神工股份"]),
    ("先进封装材料", "联瑞新材、华海诚科。", "#ec4899", "📦", ["联瑞新材","华海诚科"]),
    ("CMP抛光材料", "鼎龙股份国内CMP抛光垫绝对龙头，全球少数批量供应。安集科技CMP抛光液和光刻胶去除剂龙头，配方定制化高粘性。", "#0891b2", "✨", ["鼎龙股份","安集科技"]),
    ("鸿蒙7.0", "润和软件(OpenHarmony创始/HiHope发行版)、诚迈科技(核心ISV/望龙电脑)、软通动力(ISV+同方PC/昇腾鲲鹏)、智微智能(昇腾金牌/AIPC代工)、法本信息(鸿蒙应用开发迁移)、瑞芯微(端侧AI SoC/NPU)、广和通(端侧AI模组)、恒玄科技(AIoT音频芯片)、乐鑫科技(WiFi MCU全球第一)、晶晨股份(多媒体SoC)、常山北明。", "#10b981", "📱", ["润和软件","诚迈科技","软通动力","智微智能","法本信息","瑞芯微","广和通","恒玄科技","乐鑫科技","晶晨股份","常山北明"]),
    ("物理仿真与虚拟训练", "索辰科技(工业仿真/天工开物)、霍莱沃(电磁仿真/低空环境)、凡拓数创(三维数字孪生)。", "#d946ef", "🖥️", ["索辰科技","霍莱沃","凡拓数创"]),
    ("空间感知与数据要素", "奥比中光(三维视觉硬件)、天娱数科(Behavision空间智能大模型)、智微智能(边缘算力硬件)。", "#f59e0b", "👁️", ["奥比中光","天娱数科","智微智能"]),
    ("工业智能与具身控制", "中控技术(流程工业/巡检机器人)、能科科技(工业数字孪生/机器狗大脑)、科大讯飞(机器人超脑平台)。", "#2563eb", "🤖", ["中控技术","能科科技","科大讯飞"]),
    ("运动控制与底层硬件", "鸣志电器(无框电机/无铁芯电机)、光启技术(超材料/隐身)、东方精工(嘉腾机器人/若愚科技)。", "#dc2626", "🦾", ["鸣志电器","光启技术","东方精工"]),
    ("折叠屏转轴与铰链", "科森科技(转轴组装龙头/苹果)、宜安科技(液态金属)、精研科技(MIM结构件龙头)、东睦股份(MIM粉末冶金)、统联精密(MIM微型结构件)、大富科技、宇环数控(磨削设备)、联得装备。", "#eab308", "📱", ["科森科技","宜安科技","精研科技","东睦股份","统联精密","大富科技","宇环数控","联得装备"]),
    ("折叠屏显示与保护盖板", "凯盛科技(UTG玻璃龙头)、长信科技(UTG减薄强化)、沃格光电(CPI薄膜)、日久光电(3A光学膜)、京东方A(柔性OLED面板)、维信诺、深天马A、TCL科技。", "#7c3aed", "🖥️", ["凯盛科技","长信科技","沃格光电","日久光电","京东方A","维信诺","深天马A","TCL科技"]),
    ("折叠屏摄像头与光学", "水晶光电(滤光片/棱镜核心)、蓝特光学(棱镜)、五方光电(滤光片)、欧菲光(摄像头模组)。", "#f43f5e", "📷", ["水晶光电","蓝特光学","五方光电","欧菲光"]),
]

with open("data/groups/groups.json", "r", encoding="utf-8") as f:
    data = json.load(f)
existing = data.get("groups", [])

for name, desc, color, icon, stocks in new_groups:
    gid = f"group_{int(time.time()*1000)}_{name}"
    existing.append({"id":gid,"name":name,"description":desc,"color":color,"icon":icon,"stocks":stocks,"created_at":now,"updated_at":now})
    time.sleep(0.001)

data["groups"] = existing
json.dump(data, open("data/groups/groups.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"Groups: {len(existing)}")

# Sync to Supabase
records = []
for g in existing[-len(new_groups):]:
    records.append({"id":g["id"],"name":g["name"],"description":g["description"],"color":g["color"],"icon":g["icon"],"stocks":json.dumps(g["stocks"],ensure_ascii=False),"created_at":g["created_at"],"updated_at":g["updated_at"]})

d = json.dumps(records, ensure_ascii=False).encode()
urllib.request.urlopen(urllib.request.Request(f"{U}/rest/v1/groups_data", data=d, method='POST',
    headers={"apikey":K,"Authorization":f"Bearer {K}","Content-Type":"application/json"}), timeout=30)
print(f"Synced {len(records)} groups to Supabase")
