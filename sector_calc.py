# -*- coding: utf-8 -*-
import json

BASE = r"C:\Users\15899\.workbuddy\projects\d-workbuddy\96872b34-9ade-4684-b467-07eaf70c38e0\tool-results"
TODAY = BASE + r"\mcp-westock-mcp-data_quote-1794109241161-00376f.txt"
HALFYEAR = BASE + r"\mcp-westock-mcp-data_quote-1794109241469-ad61bb.txt"

today = json.load(open(TODAY, encoding="utf-8"))["data"]
half = json.load(open(HALFYEAR, encoding="utf-8"))["data"]

sectors = []
for code, t in today.items():
    name = t.get("name", code)
    today_pct = t.get("change_percent", 0)
    chg_5d = t.get("chg_5d", 0)
    chg_20d = t.get("chg_20d", 0)
    chg_60d = t.get("chg_60d", 0)
    chg_ytd = t.get("chg_ytd", 0)
    price_now = t.get("price", 0)
    # 6月基准价
    h = half.get(code, {})
    price_6m = h.get("price", 0)
    chg_6m = round((price_now / price_6m - 1) * 100, 2) if price_6m else None
    sectors.append({
        "code": code, "name": name,
        "today": round(today_pct, 2),
        "w1": round(chg_5d, 2),
        "m1": round(chg_20d, 2),
        "m3": round(chg_60d, 2),
        "m6": chg_6m,
        "ytd": round(chg_ytd, 2),
    })

print("总板块数:", len(sectors))
print("6月数据缺失的板块数:", sum(1 for s in sectors if s["m6"] is None))

def top(key, n=8, label=""):
    valid = [s for s in sectors if s[key] is not None]
    valid.sort(key=lambda x: -x[key])
    print(f"\n==== {label} 龙头板块 TOP{n} ====")
    for s in valid[:n]:
        print(f'  {s["name"]:12s} {s[key]:>7}%')

def bottom(key, n=5, label=""):
    valid = [s for s in sectors if s[key] is not None]
    valid.sort(key=lambda x: x[key])
    print(f"\n==== {label} 跌幅榜 TOP{n} ====")
    for s in valid[:n]:
        print(f'  {s["name"]:12s} {s[key]:>7}%')

top("w1", 8, "1周")
top("m1", 8, "1月")
top("m3", 8, "3月")
top("m6", 8, "6月")

# 当天热点板块 + 多周期表现
today_sorted = sorted(sectors, key=lambda x: -x["today"])
print("\n==== 当天热点板块(涨幅榜TOP10) 及其多周期表现 ====")
print(f'{"板块":12s} {"当天":>7} {"1周":>7} {"1月":>7} {"3月":>7} {"6月":>8}')
for s in today_sorted[:10]:
    m6 = f'{s["m6"]}%' if s["m6"] is not None else '--'
    print(f'{s["name"]:12s} {s["today"]:>6}% {s["w1"]:>6}% {s["m1"]:>6}% {s["m3"]:>6}% {m6:>8}')

# 输出JSON供HTML使用
with open("sector_data.json", "w", encoding="utf-8") as f:
    json.dump(sectors, f, ensure_ascii=False, indent=0)
print("\n已写入 sector_data.json")
