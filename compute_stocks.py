# -*- coding: utf-8 -*-
"""从 collected.json 计算个股均线/五维评分/持仓分级/止损价（复用 compute.py 逻辑）"""
import json

data = json.load(open('collected.json', encoding='utf-8'))

# 板块当日涨幅（已采集到的；缺失的稍后补齐，先给 None）
sector_chg = {
    "玻璃玻纤": -6.07,
    "医疗服务": -3.01,
    "股份制银行": 1.21,
    "半导体": -2.92,
}

def ma(c, n):
    return sum(c[:n]) / n

results = []
for s in data['stocks']:
    code = s['code']; name = s['name']; is_etf = s['etf']; sector = s['sector']
    price = s['price']; chg = s['chg']; vr = s['vr']
    # closes: 旧->新，反转为 新->旧
    closes = list(reversed(s['closes']))
    if price is None or chg is None:
        print('跳过（缺行情）:', name)
        continue
    if len(closes) < 20:
        print('跳过（K线不足）:', name, len(closes))
        continue
    ma5 = ma(closes, 5); ma10 = ma(closes, 10); ma20 = ma(closes, 20)
    above5 = price > ma5; above10 = price > ma10; above20 = price > ma20
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
        stop = round(ma10, 2)
    else:
        stop = round(ma20, 2)
    trend30 = {65: 30, 55: 24, 45: 18, 30: 12}[trend65]
    up = chg > 0
    if up and vr >= 1: vol = 20
    elif up and vr < 1: vol = 15
    elif (not up) and vr < 1: vol = 12
    else: vol = 8
    if chg > 5: st = 20
    elif chg > 2: st = 15
    elif chg > 0: st = 10
    else: st = 5
    sc = sector_chg.get(sector)
    if is_etf: sec = 10
    elif sc is None: sec = 10  # 未知板块，中性给10
    elif sc > 0.5: sec = 15
    elif sc > -1.0: sec = 10
    else: sec = 5
    dist = (price - stop) / stop * 100
    if dist > 5: risk = 15
    elif dist > 2: risk = 10
    else: risk = 5
    total = trend30 + vol + st + sec + risk
    if chg > 2 and (above5 and above10 and above20):
        grade = "A"
    elif (above5 and above10 and above20) or (above20 and -2 <= chg <= 2):
        grade = "B"
    elif (not above20) and chg >= -2:
        grade = "C"
    else:
        grade = "D"
    results.append({
        "code": code, "name": name, "etf": is_etf, "price": price, "chg": chg,
        "ma5": round(ma5, 3), "ma10": round(ma10, 3), "ma20": round(ma20, 3),
        "pos": pos, "stop": round(stop, 2), "dist": round(dist, 1),
        "dims": {"trend": trend30, "vol": vol, "strength": st, "sector": sec, "risk": risk},
        "total": total, "grade": grade, "sector": sector,
        "sect_chg": sc if sc is not None else None, "vr": vr,
    })

results.sort(key=lambda x: -x['total'])
print("=== 个股评分（按总分降序） ===")
for r in results:
    print(f'{r["name"]:12s} {r["price"]:>7} {r["chg"]:>6}% {r["pos"]:10s} 止损={r["stop"]} 总分={r["total"]} {r["grade"]}级 板块={r["sector"]}')

json.dump({"stocks": results}, open('stock_score.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n已保存 stock_score.json，共', len(results), '只')
