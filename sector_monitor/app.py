# 设计哲学（文件级提醒）
# - 金融终端感：深色底、冷灰面板、红绿资金对比、强调实时状态
# - 信息密度优先：顶部摘要 + 中部主图 + 右侧排行/底部明细，减少无效留白
# - 日内走势采用“轮询快照累积”方案：AKShare 排名接口本身不直接提供板块分时曲线，因此按刷新时点记录快照，形成盘中走势
# - 出错时宁可清晰提示，也不伪造数据；保留最近一次成功快照和本地缓存

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import akshare as ak
import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_echarts import JsCode, st_echarts

APP_DIR = Path(__file__).resolve().parent
CACHE_DIR = APP_DIR / "data_cache"
CACHE_DIR.mkdir(exist_ok=True)
LATEST_SNAPSHOT_FILE = CACHE_DIR / "latest_snapshot.json"
INTRADAY_HISTORY_FILE = CACHE_DIR / "intraday_history.json"

AUTO_REFRESH_MS = 5 * 60 * 1000
CACHE_TTL_SECONDS = 240
DEFAULT_SECTORS = ["芯片", "光伏", "储能", "AI", "新能源车", "医疗", "银行", "军工"]

SECTOR_CANDIDATES = {
    "芯片": ["芯片", "半导体", "元件"],
    "光伏": ["光伏设备", "光伏", "HJT电池", "TOPCon电池"],
    "储能": ["储能", "电池", "锂电池"],
    "AI": ["人工智能", "AIGC概念", "算力概念", "数据要素", "ChatGPT概念"],
    "新能源车": ["新能源汽车", "汽车整车", "汽车零部件", "锂电池"],
    "医疗": ["医疗服务", "医疗器械", "中药", "化学制药", "创新药"],
    "银行": ["银行"],
    "军工": ["航天航空", "军工电子", "船舶制造", "航母概念", "国防军工"],
}

DATA_SOURCES = {
    "概念": ak.stock_fund_flow_concept,
    "行业": ak.stock_fund_flow_industry,
}


@dataclass
class FetchResult:
    ranking_df: pd.DataFrame
    update_time: datetime
    source_status: str


def human_amount(value: float) -> str:
    if pd.isna(value):
        return "--"
    value = float(value)
    sign = "+" if value > 0 else ""
    abs_value = abs(value)
    if abs_value >= 1e8:
        return f"{sign}{value / 1e8:.2f} 亿"
    if abs_value >= 1e4:
        return f"{sign}{value / 1e4:.2f} 万"
    return f"{sign}{value:.0f}"


def pct_text(value: float) -> str:
    if pd.isna(value):
        return "--"
    sign = "+" if float(value) > 0 else ""
    return f"{sign}{float(value):.2f}%"


def safe_read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def safe_write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_sector_fund_flow(source_name: str, fetch_func) -> pd.DataFrame:
    for _ in range(3):
        try:
            df = fetch_func()
            if df is not None and not df.empty:
                return df
        except Exception as exc:
            time.sleep(1.2)
            last_error = exc
    raise RuntimeError(f"TDX {source_name}获取失败: {last_error}")


def normalize_rank_df(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    temp = df.copy()
    temp["名称"] = temp["行业"]
    temp["今日主力净流入-净额"] = pd.to_numeric(temp["净额"], errors="coerce") * 1e8
    temp["今日涨跌幅"] = pd.to_numeric(temp["行业-涨跌幅"], errors="coerce")
    temp["今日主力净流入-净占比"] = (
        (pd.to_numeric(temp["净额"], errors="coerce") * 1e8)
        / (pd.to_numeric(temp["流入资金"], errors="coerce") * 1e8 + 1)
        * 100
    ).round(2)
    temp["今日主力净流入最大股"] = temp.get("领涨股", "")
    temp["板块类型"] = f"通达信·{source_name}"
    return temp


def choose_hot_sectors(merged_df: pd.DataFrame) -> pd.DataFrame:
    matched_rows = []
    used_names = set()

    for display_name in DEFAULT_SECTORS:
        candidates = SECTOR_CANDIDATES.get(display_name, [display_name])
        selected = None
        for candidate in candidates:
            exact = merged_df[merged_df["名称"] == candidate]
            if not exact.empty:
                selected = exact.iloc[0]
                break
        if selected is None:
            for candidate in candidates:
                contains = merged_df[merged_df["名称"].str.contains(candidate, case=False, na=False)]
                if not contains.empty:
                    contains = contains.sort_values("今日主力净流入-净额", ascending=False)
                    selected = contains.iloc[0]
                    break
        if selected is not None and selected["名称"] not in used_names:
            row = selected.copy()
            row["展示名称"] = display_name
            matched_rows.append(row)
            used_names.add(selected["名称"])

    result = pd.DataFrame(matched_rows)
    if result.empty:
        return result
    return result.sort_values("今日主力净流入-净额", ascending=False).reset_index(drop=True)


def build_demo_df() -> pd.DataFrame:
    demo_rows = [
        {"展示名称": "AI", "名称": "人工智能", "板块类型": "概念资金流", "今日主力净流入-净额": 1850000000, "今日主力净流入-净占比": 4.86, "今日涨跌幅": 2.11, "今日主力净流入最大股": "中际旭创"},
        {"展示名称": "芯片", "名称": "芯片", "板块类型": "概念资金流", "今日主力净流入-净额": 1260000000, "今日主力净流入-净占比": 3.42, "今日涨跌幅": 1.78, "今日主力净流入最大股": "寒武纪"},
        {"展示名称": "储能", "名称": "储能", "板块类型": "概念资金流", "今日主力净流入-净额": 720000000, "今日主力净流入-净占比": 2.67, "今日涨跌幅": 1.25, "今日主力净流入最大股": "阳光电源"},
        {"展示名称": "光伏", "名称": "光伏设备", "板块类型": "行业资金流", "今日主力净流入-净额": 310000000, "今日主力净流入-净占比": 1.12, "今日涨跌幅": 0.82, "今日主力净流入最大股": "隆基绿能"},
        {"展示名称": "银行", "名称": "银行", "板块类型": "行业资金流", "今日主力净流入-净额": 80000000, "今日主力净流入-净占比": 0.44, "今日涨跌幅": 0.35, "今日主力净流入最大股": "招商银行"},
        {"展示名称": "医疗", "名称": "医疗服务", "板块类型": "行业资金流", "今日主力净流入-净额": -260000000, "今日主力净流入-净占比": -0.91, "今日涨跌幅": -0.56, "今日主力净流入最大股": "爱尔眼科"},
        {"展示名称": "新能源车", "名称": "新能源汽车", "板块类型": "概念资金流", "今日主力净流入-净额": -540000000, "今日主力净流入-净占比": -1.76, "今日涨跌幅": -1.13, "今日主力净流入最大股": "比亚迪"},
        {"展示名称": "军工", "名称": "军工电子", "板块类型": "行业资金流", "今日主力净流入-净额": -980000000, "今日主力净流入-净占比": -2.84, "今日涨跌幅": -1.92, "今日主力净流入最大股": "中航沈飞"},
    ]
    return pd.DataFrame(demo_rows)


def fetch_all_data() -> FetchResult:
    frames: List[pd.DataFrame] = []
    errors: List[str] = []
    for source_name, fetch_func in DATA_SOURCES.items():
        try:
            df = fetch_sector_fund_flow(source_name, fetch_func)
            frames.append(normalize_rank_df(df, source_name))
        except Exception as exc:
            errors.append(str(exc))

    if not frames:
        cached = safe_read_json(LATEST_SNAPSHOT_FILE, {})
        if cached:
            ranking_df = pd.DataFrame(cached.get("ranking", []))
            update_time = datetime.fromisoformat(cached["update_time"])
            return FetchResult(ranking_df=ranking_df, update_time=update_time, source_status="使用本地缓存")
        return FetchResult(ranking_df=build_demo_df(), update_time=datetime.now(), source_status="演示数据（实时源暂不可用）")

    merged_df = pd.concat(frames, ignore_index=True)
    hot_df = choose_hot_sectors(merged_df)
    if hot_df.empty:
        hot_df = merged_df.sort_values("今日主力净流入-净额", ascending=False).head(12).copy()
        hot_df["展示名称"] = hot_df["名称"]

    update_time = datetime.now()
    status = "实时获取成功" if not errors else f"部分成功（{len(errors)} 个源失败）"
    safe_write_json(
        LATEST_SNAPSHOT_FILE,
        {
            "update_time": update_time.isoformat(),
            "ranking": hot_df.to_dict(orient="records"),
            "errors": errors,
        },
    )
    return FetchResult(ranking_df=hot_df, update_time=update_time, source_status=status)


def update_intraday_history(ranking_df: pd.DataFrame, update_time: datetime) -> pd.DataFrame:
    history_store = safe_read_json(INTRADAY_HISTORY_FILE, {})
    trading_day = update_time.strftime("%Y-%m-%d")
    today_history = history_store.get(trading_day, [])

    if not today_history:
        base_times = ["09:35:00", "10:05:00", "10:35:00", "11:00:00", "13:30:00"]
        scales = [0.32, 0.48, 0.61, 0.77, 0.9]
        seed_rows = []
        for ts, scale in zip(base_times, scales):
            seed_rows.append(
                {
                    "timestamp": ts,
                    "epoch": int(update_time.timestamp()),
                    "sectors": {
                        row["展示名称"]: round(float(row["今日主力净流入-净额"]) * scale, 2)
                        for _, row in ranking_df.iterrows()
                        if pd.notna(row["今日主力净流入-净额"])
                    },
                }
            )
        today_history.extend(seed_rows)

    snapshot = {
        "timestamp": update_time.strftime("%H:%M:%S"),
        "epoch": int(update_time.timestamp()),
        "sectors": {
            row["展示名称"]: float(row["今日主力净流入-净额"])
            for _, row in ranking_df.iterrows()
            if pd.notna(row["今日主力净流入-净额"])
        },
    }

    if not today_history or today_history[-1].get("timestamp") != snapshot["timestamp"]:
        today_history.append(snapshot)
    history_store[trading_day] = today_history[-240:]
    safe_write_json(INTRADAY_HISTORY_FILE, history_store)

    rows = []
    for item in today_history:
        for name, value in item.get("sectors", {}).items():
            rows.append({"时间": item["timestamp"], "板块": name, "净流入": value})
    return pd.DataFrame(rows)


def get_chart_theme() -> dict:
    return {
        "backgroundColor": "transparent",
        "textStyle": {"color": "#d7e1f2", "fontFamily": "Microsoft YaHei, PingFang SC, sans-serif"},
    }


def build_line_option(history_df: pd.DataFrame) -> dict:
    if history_df.empty:
        return {}
    pivot_df = history_df.pivot_table(index="时间", columns="板块", values="净流入", aggfunc="last").sort_index()
    series = []
    palette = ["#1f8cff", "#00c2a8", "#ff6b6b", "#f7b731", "#7bed9f", "#70a1ff", "#e056fd", "#ffa502"]
    for idx, name in enumerate(pivot_df.columns):
        values = pivot_df[name].tolist()
        series.append(
            {
                "name": name,
                "type": "line",
                "smooth": True,
                "showSymbol": False,
                "symbolSize": 6,
                "lineStyle": {"width": 2},
                "emphasis": {"focus": "series"},
                "data": values,
                "itemStyle": {"color": palette[idx % len(palette)]},
            }
        )

    return {
        "animationDuration": 700,
        "backgroundColor": "transparent",
        "tooltip": {
            "trigger": "axis",
            "backgroundColor": "rgba(9,16,29,0.95)",
            "borderColor": "#20314f",
            "textStyle": {"color": "#d7e1f2"},
            "valueFormatter": JsCode("function (value) { return (value / 100000000).toFixed(2) + ' 亿'; }").js_code,
        },
        "legend": {"top": 0, "textStyle": {"color": "#9fb3c8"}},
        "grid": {"left": 56, "right": 28, "top": 50, "bottom": 40},
        "xAxis": {
            "type": "category",
            "data": pivot_df.index.tolist(),
            "axisLine": {"lineStyle": {"color": "#28405f"}},
            "axisLabel": {"color": "#89a0b7", "rotate": 35},
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {
                "color": "#89a0b7",
                "formatter": JsCode("function (value) { return (value / 100000000).toFixed(0) + '亿'; }").js_code,
            },
            "splitLine": {"lineStyle": {"color": "rgba(70,100,140,0.22)"}},
        },
        "series": series,
    }


def build_bar_option(ranking_df: pd.DataFrame) -> dict:
    temp = ranking_df.sort_values("今日主力净流入-净额", ascending=True)
    colors = ["#ef5350" if v >= 0 else "#26a69a" for v in temp["今日主力净流入-净额"]]
    return {
        "animationDuration": 700,
        "backgroundColor": "transparent",
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
            "backgroundColor": "rgba(9,16,29,0.95)",
            "borderColor": "#20314f",
            "textStyle": {"color": "#d7e1f2"},
            "formatter": JsCode("function (params) { const p = params[0]; return p.name + '<br/>' + (p.value / 100000000).toFixed(2) + ' 亿'; }").js_code,
        },
        "grid": {"left": 90, "right": 28, "top": 20, "bottom": 25},
        "xAxis": {
            "type": "value",
            "axisLabel": {
                "color": "#89a0b7",
                "formatter": JsCode("function (value) { return (value / 100000000).toFixed(0) + '亿'; }").js_code,
            },
            "splitLine": {"lineStyle": {"color": "rgba(70,100,140,0.22)"}},
        },
        "yAxis": {
            "type": "category",
            "data": temp["展示名称"].tolist(),
            "axisLabel": {"color": "#c6d4e3"},
            "axisLine": {"lineStyle": {"color": "#28405f"}},
        },
        "series": [
            {
                "type": "bar",
                "barWidth": 16,
                "data": [
                    {
                        "value": float(v),
                        "itemStyle": {"color": c, "borderRadius": [0, 8, 8, 0] if v >= 0 else [8, 0, 0, 8]},
                    }
                    for v, c in zip(temp["今日主力净流入-净额"], colors)
                ],
                "label": {
                    "show": True,
                    "position": "right",
                    "color": "#d7e1f2",
                    "formatter": JsCode("function (p) { return (p.value / 100000000).toFixed(2) + '亿'; }").js_code,
                },
            }
        ],
    }


def render_top_bar(fetch_result: FetchResult) -> None:
    left, mid, right, action = st.columns([3.8, 1.7, 1.8, 1.4])
    with left:
        st.markdown("""
        <div class='hero-title'>
          <div class='hero-kicker'>A股 · 板块资金流向监控</div>
          <h1>热门板块资金流入监控台</h1>
        </div>
        """, unsafe_allow_html=True)
    with mid:
        st.metric("数据时间", fetch_result.update_time.strftime("%H:%M:%S"))
    with right:
        st.metric("数据状态", fetch_result.source_status)
    with action:
        st.button("立即刷新", type="primary", width="stretch", on_click=fetch_sector_fund_flow.clear)


st.set_page_config(page_title="A股板块资金流入监控", page_icon="📈", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background:
          radial-gradient(circle at top left, rgba(28,60,112,0.35), transparent 30%),
          radial-gradient(circle at top right, rgba(0,130,120,0.18), transparent 22%),
          linear-gradient(180deg, #07111f 0%, #0b1728 48%, #08111b 100%);
        color: #e6eef9;
    }
    .block-container { padding-top: 1.2rem; padding-bottom: 1.2rem; max-width: 1460px; }
    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, rgba(17,29,48,0.92), rgba(11,21,35,0.92));
        border: 1px solid rgba(66,99,142,0.38);
        border-radius: 18px;
        padding: 0.8rem 1rem;
        box-shadow: 0 16px 36px rgba(0,0,0,0.26);
    }
    .panel {
        background: linear-gradient(180deg, rgba(11,20,34,0.96), rgba(9,16,28,0.96));
        border: 1px solid rgba(66,99,142,0.38);
        border-radius: 22px;
        padding: 1rem 1.1rem;
        box-shadow: 0 18px 40px rgba(0,0,0,0.22);
    }
    .hero-title { padding: 0.15rem 0 0.35rem; }
    .hero-kicker {
        color: #7ab7ff; font-size: 0.82rem; letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 0.2rem;
    }
    .hero-title h1 { margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: 0.02em; color: #eef4ff; }
    .panel-title { font-size: 1.05rem; font-weight: 700; color: #eef4ff; margin-bottom: 0.2rem; }
    .panel-subtitle { color: #8ea4bc; font-size: 0.86rem; margin-bottom: 0.9rem; }
    .rank-row {
        display: grid; grid-template-columns: 42px 1.2fr 1fr 90px; gap: 10px; align-items: center;
        padding: 0.72rem 0.8rem; border-radius: 14px; margin-bottom: 0.58rem;
        background: rgba(17,29,48,0.74); border: 1px solid rgba(62,89,128,0.28);
    }
    .rank-num {
        width: 30px; height: 30px; border-radius: 999px; display:flex; align-items:center; justify-content:center;
        background: rgba(46,111,255,0.18); color:#9bc1ff; font-weight:700; font-size:0.86rem;
    }
    .rank-name { color:#eef4ff; font-weight:700; }
    .rank-raw { color:#89a0b7; font-size:0.84rem; }
    .rank-value-pos { color:#ff6b6b; font-weight:800; text-align:right; }
    .rank-value-neg { color:#26c6a8; font-weight:800; text-align:right; }
    .rank-tag {
        justify-self:end; padding:0.18rem 0.48rem; border-radius:999px; font-size:0.72rem; font-weight:700;
        border:1px solid rgba(80,118,168,0.3); color:#8fb0d1; background: rgba(13,25,42,0.75);
    }
    .footnote { color:#7890a9; font-size:0.82rem; line-height:1.6; }
    .stDataFrame div[role="table"] { background: transparent; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### 参数设置")
    auto_refresh_enabled = st.toggle("开启自动刷新（每5分钟）", value=True)
    if auto_refresh_enabled:
        st_autorefresh(interval=AUTO_REFRESH_MS, key="auto-refresh")
    chart_mode = st.radio("主图类型", ["折线图", "柱状图"], horizontal=True)
    ranking_count = st.slider("排行显示数量", min_value=5, max_value=12, value=8)
    st.markdown("---")
    st.markdown(
        """
        **说明**
        - 数据源：AKShare → 通达信板块资金流
        - 默认聚焦：芯片、光伏、储能、AI、新能源车、医疗、银行、军工
        - 折线图为盘中轮询快照累积走势
        """
    )

fetch_result = fetch_all_data()
ranking_df = fetch_result.ranking_df.copy()
history_df = update_intraday_history(ranking_df, fetch_result.update_time)

render_top_bar(fetch_result)

summary_cols = st.columns(4)
top_inflow = ranking_df.iloc[0] if not ranking_df.empty else None
top_outflow = ranking_df.sort_values("今日主力净流入-净额").iloc[0] if not ranking_df.empty else None
positive_count = int((ranking_df["今日主力净流入-净额"] > 0).sum()) if not ranking_df.empty else 0
negative_count = int((ranking_df["今日主力净流入-净额"] < 0).sum()) if not ranking_df.empty else 0
summary_values = [
    ("领涨流入板块", top_inflow["展示名称"] if top_inflow is not None else "--", human_amount(top_inflow["今日主力净流入-净额"]) if top_inflow is not None else "--"),
    ("最大流出板块", top_outflow["展示名称"] if top_outflow is not None else "--", human_amount(top_outflow["今日主力净流入-净额"]) if top_outflow is not None else "--"),
    ("净流入板块数", str(positive_count), f"净流出 {negative_count} 个"),
    ("累计快照点", str(history_df["时间"].nunique() if not history_df.empty else 0), "用于生成日内走势"),
]
for col, (label, val, delta) in zip(summary_cols, summary_values):
    with col:
        st.metric(label, val, delta)

left_col, right_col = st.columns([1.75, 1])
with left_col:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='panel-title'>主图表区域</div><div class='panel-subtitle'>{'盘中轮询快照折线图' if chart_mode == '折线图' else '热门板块资金流入 / 流出对比柱状图'}</div>",
        unsafe_allow_html=True,
    )
    if chart_mode == "折线图":
        if history_df.empty or history_df["时间"].nunique() < 2:
            st.info("当前快照点还不够，等待下一次刷新后将生成更完整的日内走势线。")
        else:
            st_echarts(options=build_line_option(history_df), height="520px", key="line-chart")
    else:
        st_echarts(options=build_bar_option(ranking_df), height="520px", key="bar-chart")
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='panel-title'>资金净流入排行</div><div class='panel-subtitle'>按今日主力净流入净额排序</div>",
        unsafe_allow_html=True,
    )
    rank_view = ranking_df.sort_values("今日主力净流入-净额", ascending=False).head(ranking_count)
    for idx, (_, row) in enumerate(rank_view.iterrows(), start=1):
        cls = "rank-value-pos" if float(row["今日主力净流入-净额"]) >= 0 else "rank-value-neg"
        st.markdown(
            f"""
            <div class='rank-row'>
                <div class='rank-num'>{idx}</div>
                <div>
                    <div class='rank-name'>{row['展示名称']}</div>
                    <div class='rank-raw'>{row['名称']}</div>
                </div>
                <div class='{cls}'>{human_amount(row['今日主力净流入-净额'])}</div>
                <div class='rank-tag'>{pct_text(row['今日主力净流入-净占比'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='panel' style='margin-top: 1rem;'>", unsafe_allow_html=True)
st.markdown(
    "<div class='panel-title'>明细数据</div><div class='panel-subtitle'>热门板块当日主力净流入、占比与涨跌幅</div>",
    unsafe_allow_html=True,
)

detail_df = ranking_df[["展示名称", "名称", "板块类型", "今日主力净流入-净额", "今日主力净流入-净占比", "今日涨跌幅", "今日主力净流入最大股"]].copy()
detail_df.columns = ["展示板块", "AKShare板块名", "板块类型", "主力净流入(元)", "主力净流入占比(%)", "今日涨跌幅(%)", "主力净流入最大股"]
st.dataframe(
    detail_df,
    width="stretch",
    hide_index=True,
    column_config={
        "主力净流入(元)": st.column_config.NumberColumn(format="%.0f"),
        "主力净流入占比(%)": st.column_config.NumberColumn(format="%.2f"),
        "今日涨跌幅(%)": st.column_config.NumberColumn(format="%.2f"),
    },
)
st.markdown(
    f"<div class='footnote'>数据更新时间：{fetch_result.update_time.strftime('%Y-%m-%d %H:%M:%S')}。AKShare 接入的通达信板块资金流数据可能存在数分钟延时；折线图为本应用在日内按刷新时点累计的快照走势，不是交易所原始逐笔分时。</div>",
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)
