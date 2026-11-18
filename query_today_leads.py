# -*- coding: utf-8 -*-
"""查询当天热点板块的领涨股（当天涨幅最大个股），东方财富妙想选股器"""
import subprocess, csv, os, json, sys

SKILL_DIR = r"C:\Users\15899\.workbuddy\skills\mx-stocks-screener"

# 当天热点板块 TOP10（today 涨幅榜，去 Ⅱ 后缀）
QUERIES = [
    "小家电", "城商行", "铁路公路", "国有大型银行", "煤炭开采",
    "白色家电", "电视广播", "房屋建设", "调味发酵品", "股份制银行",
]

def run_query(sector):
    q = "%s板块当天涨幅最大的1只股票" % sector
    r = subprocess.run([sys.executable, "scripts/get_data.py", "--query", q, "--select-type", "A股"],
                       cwd=SKILL_DIR, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    out = r.stdout
    csv_path = None
    for line in out.splitlines():
        if line.startswith("CSV:"):
            csv_path = line.split("CSV:")[1].strip()
            break
    if not csv_path or not os.path.exists(csv_path):
        return {"sector": sector, "ok": False, "msg": out.strip()[-160:]}
    with open(csv_path, encoding="utf-8-sig", errors="ignore") as f:
        rd = csv.reader(f)
        header = next(rd)
        row = next(rd, None)
        if not row:
            return {"sector": sector, "ok": False, "msg": "空结果"}
    name = row[2] if len(row) > 2 else ""
    code = row[1] if len(row) > 1 else ""
    chg = None
    for i, h in enumerate(header):
        if h.startswith("涨跌幅"):
            chg = row[i] if i < len(row) else None
    return {"sector": sector, "ok": True, "name": name, "code": code, "chg": chg}

results = []
for sector in QUERIES:
    r = run_query(sector)
    results.append(r)
    if r["ok"]:
        print("%-14s -> %s %s%%" % (sector, r["name"], r["chg"]))
    else:
        print("%-14s -> FAIL %s" % (sector, r["msg"]))

json.dump(results, open("today_leads.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n已写入 today_leads.json，共", len(results), "条")
