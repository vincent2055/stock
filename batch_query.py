# -*- coding: utf-8 -*-
import subprocess, csv, os, json, sys

SKILL_DIR = r"C:\Users\15899\.workbuddy\skills\mx-stocks-screener"
OUT = os.path.join(SKILL_DIR, "miaoxiang", "mx_stocks_screener")

# 查询列表：(板块名, 方向, 周期)
# 方向: down=当天跌幅最大(领跌股), up=周期涨幅最大(周期龙头)
QUERIES = [
    # 领跌股（当天跌幅最大）
    ("元件", "down", ""),
    ("通信设备", "down", ""),
    ("玻璃玻纤", "down", ""),
    ("医疗服务", "down", ""),
    ("电子化学品", "down", ""),
    ("自动化设备", "down", ""),
    ("消费电子", "down", ""),
    ("工业金属", "down", ""),
    ("通用设备", "down", ""),
    # 1周龙头
    ("影视院线", "up", "近1周"),
    ("光伏设备", "up", "近1周"),
    ("游戏", "up", "近1周"),
    ("广告营销", "up", "近1周"),
    ("小家电", "up", "近1周"),
    # 1月龙头
    ("数字媒体", "up", "近1个月"),
    ("白酒", "up", "近1个月"),
    ("小家电", "up", "近1个月"),
    ("影视院线", "up", "近1个月"),
    ("酒店餐饮", "up", "近1个月"),
    ("养殖业", "up", "近1个月"),
    # 3月龙头
    ("数字媒体", "up", "近3个月"),
    ("影视院线", "up", "近3个月"),
    ("国有大型银行", "up", "近3个月"),
    ("出版", "up", "近3个月"),
    ("养殖业", "up", "近3个月"),
    ("小家电", "up", "近3个月"),
    # 6月龙头
    ("医疗服务", "up", "近6个月"),
    ("国有大型银行", "up", "近6个月"),
    ("股份制银行", "up", "近6个月"),
    ("数字媒体", "up", "近6个月"),
    ("城商行", "up", "近6个月"),
    ("白色家电", "up", "近6个月"),
]

def run_query(sector, direction, period):
    if direction == "down":
        q = "%s板块当天跌幅最大的1只股票" % sector
    else:
        q = "%s板块%s涨幅最大的1只股票" % (sector, period)
    r = subprocess.run([sys.executable, "scripts/get_data.py", "--query", q, "--select-type", "A股"],
                       cwd=SKILL_DIR, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    out = r.stdout
    # 找 CSV 路径
    csv_path = None
    for line in out.splitlines():
        if line.startswith("CSV:"):
            csv_path = line.split("CSV:")[1].strip()
            break
    if not csv_path or not os.path.exists(csv_path):
        return {"sector": sector, "period": period, "dir": direction, "ok": False, "msg": out.strip()[-200:]}
    # 解析 CSV 第一行
    with open(csv_path, encoding="utf-8-sig", errors="ignore") as f:
        rd = csv.reader(f)
        header = next(rd)
        row = next(rd, None)
        if not row:
            return {"sector": sector, "period": period, "dir": direction, "ok": False, "msg": "空结果"}
    # 列：序号,代码,名称,最新价,涨跌幅(%),申万行业分类,[区间涨跌幅(%)],...
    name = row[2]
    code = row[1]
    # 涨跌幅列：领跌股查"涨跌幅(%)"，周期龙头查"区间涨跌幅(%)"
    chg = None
    for i, h in enumerate(header):
        if direction == "down" and h.startswith("涨跌幅"):
            chg = row[i]
        elif direction == "up" and "区间涨跌幅" in h:
            chg = row[i]
    return {"sector": sector, "period": period, "dir": direction, "ok": True, "name": name, "code": code, "chg": chg}

results = []
for sector, direction, period in QUERIES:
    r = run_query(sector, direction, period)
    results.append(r)
    status = "OK" if r["ok"] else "FAIL"
    if r["ok"]:
        print("%s %s %-10s -> %s %s%%" % (r["dir"], r["period"], r["sector"], r["name"], r["chg"]))
    else:
        print("%s %s %-10s -> FAIL %s" % (r["dir"], r["period"], r["sector"], r["msg"]))

json.dump(results, open("lead_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n已写入 lead_result.json，共", len(results), "条")
