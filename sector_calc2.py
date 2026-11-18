# -*- coding: utf-8 -*-
"""处理板块周期数据：从两个 data_quote 结果文件提取 124 板块 today/w1/m1/m3/m6
用法: python sector_calc2.py <今日data_quote结果文件> <半年前data_quote结果文件>
"""
import json, sys

if len(sys.argv) >= 3:
    TODAY_FILE, HALF_FILE = sys.argv[1], sys.argv[2]
else:
    print("用法: python sector_calc2.py <今日data_quote结果文件> <半年前data_quote结果文件>")
    sys.exit(1)

today = json.load(open(TODAY_FILE, encoding='utf-8'))['data']
half = json.load(open(HALF_FILE, encoding='utf-8'))['data']

sectors = []
for code, t in today.items():
    name = t.get('name', code)
    today_pct = t.get('change_percent', 0)
    chg_5d = t.get('chg_5d', 0)
    chg_20d = t.get('chg_20d', 0)
    chg_60d = t.get('chg_60d', 0)
    chg_ytd = t.get('chg_ytd', 0)
    price_now = t.get('price', 0)
    h = half.get(code, {})
    price_6m = h.get('price', 0)
    chg_6m = round((price_now / price_6m - 1) * 100, 2) if price_6m else None
    sectors.append({
        'code': code, 'name': name,
        'today': round(today_pct, 2),
        'w1': round(chg_5d, 2),
        'm1': round(chg_20d, 2),
        'm3': round(chg_60d, 2),
        'm6': chg_6m,
        'ytd': round(chg_ytd, 2),
    })

print('总板块数:', len(sectors))
print('6月数据缺失的板块数:', sum(1 for s in sectors if s['m6'] is None))

def top(key, n=8, label=''):
    valid = [s for s in sectors if s[key] is not None]
    valid.sort(key=lambda x: -x[key])
    print(f'\n==== {label} TOP{n} ====')
    for s in valid[:n]:
        print(f'  {s["name"]:14s} {s[key]:>7}%')

def bottom(key, n=8, label=''):
    valid = [s for s in sectors if s[key] is not None]
    valid.sort(key=lambda x: x[key])
    print(f'\n==== {label} BOTTOM{n} ====')
    for s in valid[:n]:
        print(f'  {s["name"]:14s} {s[key]:>7}%')

top('w1', 8, '1周')
top('m1', 8, '1月')
top('m3', 8, '3月')
top('m6', 8, '6月')

today_sorted = sorted(sectors, key=lambda x: -x['today'])
print('\n==== 当天涨幅榜 TOP10 ====')
for s in today_sorted[:10]:
    print(f'  {s["name"]:14s} {s["today"]:>7}%')
print('\n==== 当天跌幅榜 TOP10 ====')
for s in today_sorted[-10:][::-1]:
    print(f'  {s["name"]:14s} {s["today"]:>7}%')

with open('sector_data.json', 'w', encoding='utf-8') as f:
    json.dump(sectors, f, ensure_ascii=False, indent=0)
print('\n已写入 sector_data.json')
