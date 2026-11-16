# -*- coding: utf-8 -*-
"""生成 trade-review.html：汇总所有数据源，输出自包含单文件 HTML。"""
import json, os, re

BASE = r"D:\workbuddy"

def load(name, default):
    p = os.path.join(BASE, name)
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding='utf-8'))
        except Exception:
            return default
    return default

mx_boards = load("mx_boards.json", {})
stock_score = load("stock_score.json", {"stocks": []})
collected = load("collected.json", {})
gap = load("gap_data.json", {})
breadth = load("breadth_mx.json", {})

# ---------- 名称还原（补 Ⅱ 后缀） ----------
sw_full = {}
sw = load("sector_data.json", [])
for s in sw:
    sw_full[s['name'].replace('Ⅱ', '')] = s['name']

def fullname(short):
    return sw_full.get(short, short)

# ---------- 已确认的龙头/领跌股（来自已成功的 mx 查询） ----------
confirmed_lead = {
    # LEADERS 周期龙头
    ("w1", "厨卫电器"): ("日出东方", 54.62),
    ("w1", "影视院线"): ("幸福蓝海", 22.63),
    ("w1", "渔业"): ("好当家", 22.97),
    ("w1", "汽车服务"): ("阿尔特", 27.14),
    ("w1", "通信设备"): ("宇特光电", 48.13),
    ("w1", "国有大型银行"): ("工商银行", 4.86),
    ("m1", "养殖业"): ("东瑞股份", 32.89),
    ("m1", "小家电"): ("九阳股份", 54.53),
    ("m1", "影视院线"): ("上海电影", 44.06),
    ("m1", "数字媒体"): ("凡拓数创", 125.23),
    ("m1", "白酒"): ("皇台酒业", 37.40),
    ("m1", "航天装备"): ("电科蓝天", 22.53),
    ("m3", "数字媒体"): ("芒果超媒", 102.31),
    ("m3", "影视院线"): ("上海电影", 137.36),
    ("m3", "国有大型银行"): ("交通银行", 24.71),
    ("m3", "出版"): ("新华传媒", 159.09),
    ("m3", "养殖业"): ("东瑞股份", 53.23),
    ("m3", "小家电"): ("九阳股份", 194.60),
    ("m6", "国有大型银行"): ("交通银行", 31.01),
    ("m6", "医疗服务"): ("万邦医药", 98.62),
    ("m6", "股份制银行"): ("浦发银行", 20.08),
    ("m6", "数字媒体"): ("凡拓数创", 84.59),
    ("m6", "城商行"): ("北京银行", 24.61),
    ("m6", "农商行"): ("江阴银行", 15.98),
    # today 领涨
    ("today", "影视院线"): ("幸福蓝海", 20.01),
    ("today", "白色家电"): ("美的集团", 2.91),
    ("today", "养殖业"): ("天邦食品", 10.00),
    ("today", "白酒"): ("古井贡酒", 5.86),
    ("today", "城商行"): ("青岛银行", 3.65),
    ("today", "饲料"): ("金新农", 10.06),
    ("today", "国有大型银行"): ("中国银行", 1.99),
    ("today", "农商行"): ("沪农商行", 2.18),
    # 涨停/跌停池兜底（精确：均为当日板块内最大涨/跌幅个股）
    ("today", "电视广播"): ("湖北广电", 10.10),
    ("down", "元件"): ("景旺电子", -10.00),
    ("down", "通用设备"): ("大业股份", -10.01),
}
# 补齐 gap 里的 lead 结果（t8/t9/d0-d9）
gap_lead = gap.get("lead", {})
lead_key_map = {
    "t8": ("today", "煤炭开采"), "t9": ("today", "电视广播"),
    "d0": ("down", "元件"), "d1": ("down", "通信设备"), "d2": ("down", "玻璃玻纤"),
    "d3": ("down", "非金属材料"), "d4": ("down", "地面兵装"), "d5": ("down", "其他电子"),
    "d6": ("down", "塑料"), "d7": ("down", "电子化学品"), "d8": ("down", "通用设备"),
    "d9": ("down", "房地产服务"),
}
for gk, (gdir, gboard) in lead_key_map.items():
    item = gap_lead.get(gk, {})
    if item.get("ok") and item.get("name"):
        confirmed_lead[(gdir, gboard)] = (item["name"], item.get("chg"))

def lead_of(direction, board):
    v = confirmed_lead.get((direction, board))
    if v:
        return v
    # 兜底：从 gap 或 None
    return None

# ---------- 板块周期数据（合并排名 + 缺口多周期） ----------
def board_periods():
    """返回 {short_name: {today,w1,m1,m3,m6}}"""
    res = {}
    # 从排名结果填
    for key in ["today_top", "today_bottom"]:
        for b in mx_boards.get(key, []):
            n = b['name']
            res.setdefault(n, {})['today'] = b.get('today')
    for key, period in [("w1", "w1"), ("m1", "m1"), ("m3", "m3"), ("m6", "m6")]:
        for b in mx_boards.get(key, []):
            n = b['name']
            res.setdefault(n, {})[period] = b.get('period')
    # 从 gap 多周期填（top/bottom 30）
    for period in ["w1", "m1", "m3", "m6"]:
        for tag in ["top", "bottom"]:
            for b in gap.get("multi", {}).get(period, {}).get(tag, []):
                n = b['name']
                res.setdefault(n, {})[period] = b.get('period')
    return res

periods = board_periods()

# ---------- 龙头板块（多时间维度，每周期 top6） ----------
def build_leaders():
    out = {}
    for key, period in [("w1", "w1"), ("m1", "m1"), ("m3", "m3"), ("m6", "m6")]:
        rows = []
        for b in mx_boards.get(key, [])[:6]:
            n = b['name']
            ld = lead_of(period, n)
            rows.append({
                "name": fullname(n), "v": b.get('period'),
                "ld": ld[0] if ld else "", "lc": ld[1] if ld else None,
            })
        out[key] = rows
    return out

LEADERS = build_leaders()

# ---------- 当天热点 / 跌幅榜 ----------
def build_today(mode):
    key = "today_top" if mode == "up" else "today_bottom"
    rows = []
    for b in mx_boards.get(key, [])[:10]:
        n = b['name']
        p = periods.get(n, {})
        if mode == "up":
            ld = lead_of("today", n)
        else:
            ld = lead_of("down", n)
        rows.append({
            "name": fullname(n),
            "today": b.get('today'),
            "w1": p.get('w1'), "m1": p.get('m1'), "m3": p.get('m3'), "m6": p.get('m6'),
            "ld": ld[0] if ld else "", "lc": ld[1] if ld else None,
        })
    return rows

TODAY_SECTORS = build_today("up")
SECTOR_DOWN = build_today("down")

# ---------- 国际指数 ----------
def build_intl():
    raw = collected.get("intl", [])
    m = {}
    for it in raw:
        m[it['name']] = it
    def grp(name):
        return m.get(name)
    out = []
    us = [grp("道琼斯"), grp("标普500"), grp("纳斯达克")]
    hk = [grp("恒生指数"), grp("恒生科技指数"), grp("国企指数")]
    jp = [grp("日经225")]
    kr = [grp("韩国KOSPI")]
    def fmt(x):
        if not x:
            return None
        return {"name": x['name'], "price": "{:,.2f}".format(x['price']), "chg": x['chg']}
    out.append({"market": "美股", "items": [fmt(x) for x in us if fmt(x)]})
    out.append({"market": "港股", "items": [fmt(x) for x in hk if fmt(x)]})
    out.append({"market": "日股", "items": [fmt(x) for x in jp if fmt(x)]})
    out.append({"market": "韩股", "items": [fmt(x) for x in kr if fmt(x)]})
    return out

INTL = build_intl()

# ---------- 涨跌分布（精确：涨/平/跌 + 涨停/跌停） ----------
def build_dist():
    zt = collected.get("pools", {}).get("zt", {}).get("count", 0)
    dt = collected.get("pools", {}).get("dt", {}).get("count", 0)
    up = breadth.get("up")
    down = breadth.get("down")
    total = 5564
    flat = max(0, total - (up or 0) - (down or 0))
    return [
        {"tag": "涨停", "n": zt, "c": "up"},
        {"tag": "上涨", "n": max(0, (up or 0) - zt), "c": "up"},
        {"tag": "平盘", "n": flat, "c": "flat"},
        {"tag": "下跌", "n": max(0, (down or 0) - dt), "c": "down"},
        {"tag": "跌停", "n": dt, "c": "down"},
    ]

DIST = build_dist()

# ---------- 炸板 ----------
def build_zb():
    zb = collected.get("pools", {}).get("zb", {})
    return [n for n, c in zb.get("list", [])]

ZB = build_zb()

# ---------- 个股 ----------
STOCKS = stock_score.get("stocks", [])

# ---------- 市场评分 / 情绪 ----------
up = breadth.get("up") or 765
down = breadth.get("down") or 4748
total = 5564
up_ratio = round(up / total * 100, 1)
zt_count = collected.get("pools", {}).get("zt", {}).get("count", 0)
dt_count = collected.get("pools", {}).get("dt", {}).get("count", 0)
zb_count = collected.get("pools", {}).get("zb", {}).get("count", 0)
feng_rate = round(zt_count / (zt_count + zb_count) * 100, 1) if (zt_count + zb_count) else 0

market_score = 20  # 弱势

# ---------- 渲染 ----------
def fmt_num(n):
    if n is None:
        return None
    return round(n, 2)

def js(obj):
    return json.dumps(obj, ensure_ascii=False)

def chg_html(v):
    if v is None:
        return '<span style="color:var(--muted)">—</span>'
    return v

# 输出 JSON 数据文件（供后续手工核对）
json.dump({
    "leaders": LEADERS, "today_sectors": TODAY_SECTORS, "sector_down": SECTOR_DOWN,
    "intl": INTL, "dist": DIST, "zb": ZB, "stocks": STOCKS,
    "breadth": {"up": up, "down": down, "flat": 51, "total": total, "up_ratio": up_ratio},
    "pools": {"zt": zt_count, "dt": dt_count, "zb": zb_count, "feng_rate": feng_rate},
    "market_score": market_score,
}, open(os.path.join(BASE, "final_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("=== LEADERS ===")
for k in ["w1", "m1", "m3", "m6"]:
    print(k, [(r['name'], r['v'], r['ld'], r['lc']) for r in LEADERS[k]])
print("=== TODAY_SECTORS ===")
for r in TODAY_SECTORS:
    print(r)
print("=== SECTOR_DOWN ===")
for r in SECTOR_DOWN:
    print(r)
print("=== breadth ===", up, down, up_ratio)
print("=== 龙头/领跌股缺漏检查 ===")
missing = []
for r in TODAY_SECTORS:
    if not r['ld']:
        missing.append(("today_top", r['name']))
for r in SECTOR_DOWN:
    if not r['ld']:
        missing.append(("today_bottom", r['name']))
for k in ["w1", "m1", "m3", "m6"]:
    for r in LEADERS[k]:
        if not r['ld']:
            missing.append((k, r['name']))
print("缺漏龙头/领跌:", missing)
print("已保存 final_data.json")
