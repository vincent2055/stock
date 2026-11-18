# -*- coding: utf-8 -*-
"""汇总 2026-11-16 收盘数据，生成 final_data.json（供 generate_html.py 使用）"""
import json, os

BASE = r"D:\workbuddy"

def load(name, default):
    p = os.path.join(BASE, name)
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding='utf-8'))
        except Exception as e:
            print('加载失败', name, e)
            return default
    return default

sector_data = load("sector_data.json", [])
intl_pools = load("intl_pools.json", {})
lead_result = load("lead_result.json", [])
today_leads = load("today_leads.json", [])

def norm(name):
    return name.replace('Ⅱ', '')

# ---------- 板块多周期数据 ----------
# name -> {today,w1,m1,m3,m6}
sm = {}
for s in sector_data:
    sm[s['name']] = {
        'today': s.get('today'), 'w1': s.get('w1'), 'm1': s.get('m1'),
        'm3': s.get('m3'), 'm6': s.get('m6'),
    }

def top_sectors(key, n):
    valid = [s for s in sector_data if s.get(key) is not None]
    valid.sort(key=lambda x: -x[key])
    return valid[:n]

def bottom_sectors(key, n):
    valid = [s for s in sector_data if s.get(key) is not None]
    valid.sort(key=lambda x: x[key])
    return valid[:n]

# ---------- 龙头/领跌股 ----------
# lead_map: (period_key, norm_sector) -> (name, chg)
lead_map = {}
period_key = {"近1周": "w1", "近1个月": "m1", "近3个月": "m3", "近6个月": "m6"}
for r in lead_result:
    if not r.get('ok') or not r.get('name'):
        continue
    sec = norm(r['sector'])
    if r['dir'] == 'down':
        key = ('down', sec)
    else:
        key = (period_key.get(r['period'], ''), sec)
    try:
        chg = float(r['chg']) if r.get('chg') not in (None, '') else None
    except (ValueError, TypeError):
        chg = None
    lead_map[key] = (r['name'], chg)

today_lead_map = {}
for r in today_leads:
    if not r.get('ok') or not r.get('name'):
        continue
    try:
        chg = float(r['chg']) if r.get('chg') not in (None, '') else None
    except (ValueError, TypeError):
        chg = None
    today_lead_map[norm(r['sector'])] = (r['name'], chg)

# ---------- 龙头板块（多周期，各 top6） ----------
def build_leaders():
    out = {}
    for key in ["w1", "m1", "m3", "m6"]:
        rows = []
        for b in top_sectors(key, 6):
            n = b['name']
            ld = lead_map.get((key, norm(n)))
            rows.append({
                "name": n, "v": b[key],
                "ld": ld[0] if ld else "", "lc": ld[1] if ld else None,
            })
        out[key] = rows
    return out

LEADERS = build_leaders()

# ---------- 当天热点 / 跌幅榜 ----------
def build_today(up=True):
    src = top_sectors('today', 10) if up else bottom_sectors('today', 10)
    rows = []
    for b in src:
        n = b['name']
        if up:
            ld = today_lead_map.get(norm(n))
        else:
            ld = lead_map.get(('down', norm(n)))
        rows.append({
            "name": n,
            "today": b['today'], "w1": b['w1'], "m1": b['m1'], "m3": b['m3'], "m6": b['m6'],
            "ld": ld[0] if ld else "", "lc": ld[1] if ld else None,
        })
    return rows

TODAY_SECTORS = build_today(True)
SECTOR_DOWN = build_today(False)

# ---------- 国际指数 ----------
def build_intl():
    raw = intl_pools.get('intl', [])
    m = {it['name']: it for it in raw}
    def grp(name):
        return m.get(name)
    out = []
    def fmt(x):
        if not x:
            return None
        return {"name": x['name'], "price": "{:,.2f}".format(x['price']), "chg": x['chg']}
    us = [grp("道琼斯"), grp("标普500"), grp("纳斯达克")]
    hk = [grp("恒生指数"), grp("恒生科技指数"), grp("国企指数")]
    jp = [grp("日经225")]
    kr = [grp("韩国KOSPI")]
    out.append({"market": "美股", "items": [fmt(x) for x in us if fmt(x)]})
    out.append({"market": "港股", "items": [fmt(x) for x in hk if fmt(x)]})
    out.append({"market": "日股", "items": [fmt(x) for x in jp if fmt(x)]})
    out.append({"market": "韩股", "items": [fmt(x) for x in kr if fmt(x)]})
    return out

INTL = build_intl()

# ---------- 涨跌分布（data_changedist） ----------
up = 1136
down = 4344
flat = 99
total = up + down + flat  # 5579
zt = 33
dt = 68
susp = 7
up_ratio = round(up / total * 100, 1)  # 20.4

DIST = [
    {"tag": "涨停", "n": zt, "c": "up"},
    {"tag": "上涨", "n": up - zt, "c": "up"},
    {"tag": "平盘", "n": flat, "c": "flat"},
    {"tag": "下跌", "n": down - dt, "c": "down"},
    {"tag": "跌停", "n": dt, "c": "down"},
]

# ---------- 炸板 ----------
ZB = [x.get('name') for x in intl_pools.get('zb', {}).get('list', [])]
zb_count = intl_pools.get('zb', {}).get('count', 0)

# ---------- 封板率 ----------
feng_rate = round(zt / (zt + zb_count) * 100, 1) if (zt + zb_count) else 0

# ---------- 个股评分 ----------
WATCHLIST = [
    ("sh513100", "纳指ETF国泰", True, "美股科技", 2.189, -1.84, 0.64,
     [2.189,2.230,2.218,2.233,2.210,2.142,2.158,2.229,2.242,2.197,2.244,2.239,2.290,2.315,2.249,2.236,2.243,2.262,2.311,2.334,2.345,2.356,2.321,2.399,2.375]),
    ("sh513180", "恒生科技ETF华夏", True, "恒生科技", 0.478, 0.00, 1.37,
     [0.478,0.478,0.491,0.505,0.510,0.508,0.510,0.517,0.491,0.481,0.479,0.468,0.470,0.480,0.475,0.482,0.487,0.475,0.501,0.509,0.513,0.514,0.510,0.526,0.518]),
    ("sh600293", "三峡新材", False, "玻璃玻纤", 3.64, -7.14, 0.64,
     [3.64,3.92,4.23,4.31,3.92,3.83,3.68,3.90,3.93,4.00,3.64,3.31,3.47,3.85,4.27,4.42,4.91,5.23,4.75,4.32,3.93,3.78,3.70,3.36,3.47]),
    ("sz159227", "航空航天ETF华夏", True, "航空航天", 0.893, -4.49, 1.63,
     [0.893,0.935,0.956,0.958,0.961,0.966,0.956,0.969,0.958,0.929,0.929,0.911,0.946,0.948,0.935,0.979,0.983,0.962,0.986,0.988,0.993,0.975,0.937,0.971,0.972]),
    ("sh512070", "证券保险ETF易方达", True, "证券保险", 0.756, 1.34, 1.28,
     [0.756,0.746,0.743,0.752,0.761,0.762,0.763,0.770,0.767,0.770,0.753,0.731,0.736,0.739,0.746,0.757,0.747,0.733,0.739,0.744,0.756,0.754,0.758,0.753,0.758]),
    ("sz002415", "海康威视", False, "计算机设备", 35.30, 2.47, 2.07,
     [35.30,34.45,33.88,34.25,34.83,34.67,35.25,35.63,35.17,35.30,34.91,34.55,34.79,34.15,34.25,34.99,33.78,32.42,32.34,32.82,33.19,33.66,33.86,34.06,33.62]),
    ("sh603259", "药明康德", False, "医疗服务", 144.41, -1.29, 0.76,
     [144.41,146.30,150.34,148.70,150.30,150.29,147.00,154.46,148.81,135.28,138.65,142.01,142.89,142.40,141.48,146.00,144.72,141.31,147.35,147.66,146.50,144.30,154.50,154.18,157.35]),
    ("sh600276", "恒瑞医药", False, "化学制药", 48.02, -0.10, 0.84,
     [48.02,48.07,47.93,48.22,48.55,49.23,50.43,50.19,49.05,49.31,48.69,48.46,48.62,48.36,45.55,47.00,47.02,46.00,47.38,47.45,46.08,46.63,46.60,45.49,45.51]),
    ("sh601888", "中国中免", False, "一般零售", 51.81, 0.02, 1.01,
     [51.81,51.80,51.53,52.10,53.21,53.39,54.22,54.47,53.13,53.90,52.50,50.30,49.52,50.00,50.18,50.80,50.01,48.92,48.92,49.48,49.24,49.20,48.56,49.42,50.27]),
    ("sh600298", "安琪酵母", False, "调味发酵品", 37.98, 3.49, 1.32,
     [37.98,36.70,36.62,36.83,37.47,38.02,38.20,38.65,37.80,37.28,37.08,35.56,35.95,37.00,36.94,37.76,37.19,36.64,37.05,36.86,36.90,38.36,38.24,39.01,38.60]),
    ("sz300059", "东方财富", False, "证券", 18.33, 0.22, 1.08,
     [18.33,18.29,18.23,18.56,18.78,18.78,18.78,18.98,19.20,18.86,18.71,17.60,17.96,18.01,18.11,18.55,18.55,17.78,17.90,17.96,18.08,18.11,18.32,17.98,18.06]),
    ("sz002627", "三峡旅游", False, "旅游景区", 6.43, -0.16, 0.83,
     [6.43,6.44,6.38,6.50,6.47,6.31,6.46,6.59,6.46,6.58,6.49,6.49,6.16,6.04,6.13,6.29,6.87,6.80,6.68,6.56,6.42,6.47,6.39,6.50,6.55]),
    ("sz000001", "平安银行", False, "股份制银行", 12.30, 1.91, 1.73,
     [12.30,12.07,11.79,11.71,11.86,11.89,11.81,11.64,11.74,11.77,11.54,11.64,11.54,11.31,11.47,11.30,11.20,11.30,11.41,11.44,11.65,11.50,11.41,11.50,11.57]),
    ("sh688981", "中芯国际", False, "半导体", 106.44, -3.67, 1.06,
     [106.44,110.50,111.72,109.31,107.75,109.02,110.90,110.69,111.30,102.11,100.00,96.79,101.00,102.00,100.00,102.77,104.10,100.09,100.24,101.98,99.70,102.66,104.44,102.55,106.00]),
    ("sh600584", "长电科技", False, "半导体", 50.50, -4.17, 0.78,
     [50.50,52.70,54.45,54.40,52.78,52.03,52.51,53.63,51.74,47.04,50.30,49.00,51.87,55.41,53.29,55.10,59.78,59.00,57.23,57.25,56.34,56.96,57.50,58.65,60.16]),
]

def ma(c, n):
    return sum(c[:n]) / n

def compute_stocks():
    # 板块当日涨幅 map（用 clean name 兜底）
    sect_today = {}
    for s in sector_data:
        sect_today[norm(s['name'])] = s.get('today')
    results = []
    for code, name, is_etf, sector, price, chg, vr, closes in WATCHLIST:
        above5 = price > ma(closes, 5)
        above10 = price > ma(closes, 10)
        above20 = price > ma(closes, 20)
        if above5 and above10 and above20:
            pos = "5/10/20上方"; trend65 = 65
        elif above5 and above10 and not above20:
            pos = "5/10上方"; trend65 = 55
        elif above20 and not (above5 and above10):
            pos = "20日线上"; trend65 = 45
        else:
            pos = "全线下方"; trend65 = 30
        low20 = min(closes[:20])
        if not above20:
            stop = round(low20, 2)
        elif above5 and above10:
            stop = round(ma(closes, 10), 2)
        else:
            stop = round(ma(closes, 20), 2)
        trend30 = {65: 30, 55: 24, 45: 18, 30: 12}[trend65]
        upflag = chg > 0
        if upflag and vr >= 1: vol = 20
        elif upflag and vr < 1: vol = 15
        elif (not upflag) and vr < 1: vol = 12
        else: vol = 8
        if chg > 5: st = 20
        elif chg > 2: st = 15
        elif chg > 0: st = 10
        else: st = 5
        sc = sect_today.get(norm(sector))
        if is_etf: sec = 10
        elif sc is None: sec = 10
        elif sc > 0.5: sec = 15
        elif sc > -1.0: sec = 10
        else: sec = 5
        dist = (price - stop) / stop * 100
        if dist > 5: risk = 15
        elif dist > 2: risk = 10
        else: risk = 5
        total_score = trend30 + vol + st + sec + risk
        if chg > 2 and (above5 and above10 and above20):
            grade = "A"
        elif (above5 and above10 and above20) or (above20 and -2 <= chg <= 2):
            grade = "B"
        elif (not above20) and chg >= -2:
            grade = "C"
        else:
            grade = "D"
        results.append({
            "code": code, "name": name, "etf": is_etf,
            "price": price, "chg": chg,
            "ma5": round(ma(closes, 5), 3), "ma10": round(ma(closes, 10), 3), "ma20": round(ma(closes, 20), 3),
            "pos": pos, "stop": stop, "dist": round(dist, 1),
            "dims": {"trend": trend30, "vol": vol, "strength": st, "sector": sec, "risk": risk},
            "total": total_score, "grade": grade,
            "sector": sector, "sect_chg": sc, "vr": vr,
        })
    results.sort(key=lambda x: -x['total'])
    return results

STOCKS = compute_stocks()

# ---------- 市场环境评分 ----------
zt_dt_ratio = round(zt / dt, 2) if dt else 0
market_score = 20  # 弱势/冰点

final = {
    "leaders": LEADERS,
    "today_sectors": TODAY_SECTORS,
    "sector_down": SECTOR_DOWN,
    "intl": INTL,
    "dist": DIST,
    "zb": ZB,
    "stocks": STOCKS,
    "breadth": {"up": up, "down": down, "flat": flat, "total": total, "up_ratio": up_ratio},
    "pools": {"zt": zt, "dt": dt, "zb": zb_count, "feng_rate": feng_rate},
    "market_score": market_score,
    "index": [
        ("上证指数", "000001", "3602.57", -0.87),
        ("深证成指", "399001", "10690.78", -2.53),
        ("创业板指", "399006", "2320.02", -4.37),
        ("科创50", "000688", "1213.68", -5.16),
        ("北证50", "899050", "836.57", -4.54),
    ],
    "date_label": "2026-11-16 周一 收盘快照",
    "amount": "1.48",
    "zt_dt_ratio": zt_dt_ratio,
}

json.dump(final, open(os.path.join(BASE, "final_data.json"), "w", encoding='utf-8'), ensure_ascii=False, indent=1)

print("=== 个股评分 ===")
for r in STOCKS:
    print(f'{r["name"]:14s} {r["price"]:>8} {r["chg"]:>6}% {r["pos"]:12s} 止损={r["stop"]:>7} 总分={r["total"]} {r["grade"]}级 板块={r["sector"]}({r["sect_chg"]})')
print("\n=== 龙头板块 ===")
for k in ["w1","m1","m3","m6"]:
    print(k, [(r['name'], r['v'], r['ld'], r['lc']) for r in LEADERS[k]])
print("\n=== 当天热点 ===")
for r in TODAY_SECTORS:
    print(r['name'], r['today'], r['ld'], r['lc'])
print("\n=== 板块跌幅榜 ===")
for r in SECTOR_DOWN:
    print(r['name'], r['today'], r['ld'], r['lc'])
print("\n=== 涨跌 ===", up, down, flat, '涨占比', up_ratio, '% 涨停', zt, '跌停', dt, '炸板', zb_count, '封板率', feng_rate, '%')
print("已保存 final_data.json")
