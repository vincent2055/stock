# -*- coding: utf-8 -*-
"""缺口补齐：多周期板块、龙头/领跌股、涨跌分布、个股板块涨幅。含重试与延迟。"""
import subprocess, csv, os, json, sys, time

SKILL_DIR = r"C:\Users\15899\.workbuddy\skills\mx-stocks-screener"

def run_query(query, select_type, retries=2):
    for attempt in range(retries + 1):
        r = subprocess.run([sys.executable, "scripts/get_data.py", "--query", query, "--select-type", select_type],
                           cwd=SKILL_DIR, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        out = r.stdout
        csv_path = None
        for line in out.splitlines():
            if line.startswith("CSV:"):
                csv_path = line.split("CSV:")[1].strip()
                break
        if csv_path and os.path.exists(csv_path):
            with open(csv_path, encoding="utf-8-sig", errors="ignore") as f:
                rd = list(csv.reader(f))
            return (rd[0], rd[1:] if len(rd) > 1 else []), None
        if attempt < retries:
            time.sleep(3)
    return None, out.strip()[-120:] if 'out' in dir() else ""

def col_idx(header, *keys):
    for i, h in enumerate(header):
        for k in keys:
            if h.startswith(k):
                return i
    return None

def parse_board_rows(header, rows):
    i_code = col_idx(header, "代码"); i_name = col_idx(header, "名称")
    i_today = col_idx(header, "涨跌幅"); i_period = col_idx(header, "区间涨跌幅")
    res = []
    for r in rows:
        if i_name is None:
            continue
        name = r[i_name].replace("(申万)", "")
        res.append({
            "name": name,
            "today": float(r[i_today]) if i_today is not None and i_today < len(r) and r[i_today] else None,
            "period": float(r[i_period]) if i_period is not None and i_period < len(r) and r[i_period] else None,
        })
    return res

def parse_stock_row(header, rows):
    i_code = col_idx(header, "代码"); i_name = col_idx(header, "名称"); i_chg = col_idx(header, "涨跌幅")
    if not rows:
        return None
    r = rows[0]
    chg = r[i_chg] if i_chg is not None and i_chg < len(r) and r[i_chg] else None
    return {"name": r[i_name] if i_name is not None else "", "code": r[i_code] if i_code is not None else "",
            "chg": float(chg) if chg not in (None, "", "-") else None}

result = {}

# 1) 多周期排名（top/bottom 30 per period）
multi_periods = ["近1周", "近1个月", "近3个月", "近6个月"]
multi_keys = {"近1周": "w1", "近1个月": "m1", "近3个月": "m3", "近6个月": "m6"}
result["multi"] = {}
for p in multi_periods:
    k = multi_keys[p]
    for direction in ["涨幅最大", "跌幅最大"]:
        q = "申万二级行业板块%s%s的30个板块" % (p, direction)
        (header, rows), err = run_query(q, "板块")
        tag = "top" if direction == "涨幅最大" else "bottom"
        if header is None:
            print(f"[multi {k} {tag}] FAIL: {err}")
            result["multi"].setdefault(k, {})[tag] = []
            continue
        data = parse_board_rows(header, rows)
        result["multi"].setdefault(k, {})[tag] = data
        print(f"[multi {k} {tag}] {len(data)} 条")
        time.sleep(2)

# 2) 龙头/领跌股
lead_queries = [
    ("t8", "煤炭开采", "今天涨幅最大的1只股票"),
    ("t9", "电视广播", "今天涨幅最大的1只股票"),
    ("d0", "元件", "今天跌幅最大的1只股票"),
    ("d1", "通信设备", "今天跌幅最大的1只股票"),
    ("d2", "玻璃玻纤", "今天跌幅最大的1只股票"),
    ("d3", "非金属材料", "今天跌幅最大的1只股票"),
    ("d4", "地面兵装", "今天跌幅最大的1只股票"),
    ("d5", "其他电子", "今天跌幅最大的1只股票"),
    ("d6", "塑料", "今天跌幅最大的1只股票"),
    ("d7", "电子化学品", "今天跌幅最大的1只股票"),
    ("d8", "通用设备", "今天跌幅最大的1只股票"),
    ("d9", "房地产服务", "今天跌幅最大的1只股票"),
]
result["lead"] = {}
for key, board, action in lead_queries:
    q = "%s板块%s" % (board, action)
    (header, rows), err = run_query(q, "A股")
    if header is None:
        print(f"[lead {key}] {board} FAIL: {err}")
        result["lead"][key] = {"board": board, "ok": False}
        time.sleep(2)
        continue
    s = parse_stock_row(header, rows)
    result["lead"][key] = {"board": board, "ok": True, **(s or {})}
    print(f"[lead {key}] {board} -> {s['name'] if s else 'None'} {s['chg'] if s else ''}")
    time.sleep(2)

# 3) 涨跌分布 buckets
bucket_queries = [
    ("gt7", "今天涨幅大于7%的A股"),
    ("r5_7", "今天涨幅在5%到7%之间的A股"),
    ("r2_5", "今天涨幅在2%到5%之间的A股"),
    ("r0_2", "今天涨幅在0到2%之间的A股"),
    ("d0_2", "今天跌幅在0到2%之间的A股"),
    ("d2_5", "今天跌幅在2%到5%之间的A股"),
    ("d5_7", "今天跌幅在5%到7%之间的A股"),
    ("lt7", "今天跌幅大于7%的A股"),
]
result["buckets"] = {}
for key, q in bucket_queries:
    (header, rows), err = run_query(q, "A股")
    if header is None:
        print(f"[bucket {key}] FAIL: {err}")
        result["buckets"][key] = None
        time.sleep(2)
        continue
    result["buckets"][key] = len(rows)
    print(f"[bucket {key}] -> {len(rows)}")
    time.sleep(2)

# 4) 个股所属板块当日涨幅
sector_queries = [
    ("计算机设备", "计算机设备"),
    ("化学制药", "化学制药"),
    ("一般零售", "一般零售"),
    ("调味发酵品", "调味发酵品"),
    ("证券", "证券"),
    ("旅游景区", "旅游景区"),
]
result["sectors"] = {}
for key, board in sector_queries:
    q = "%s板块今天的涨幅" % board
    (header, rows), err = run_query(q, "板块")
    if header is None:
        print(f"[sector {key}] FAIL: {err}")
        result["sectors"][key] = None
        time.sleep(2)
        continue
    i_chg = col_idx(header, "涨跌幅")
    chg = float(rows[0][i_chg]) if rows and i_chg is not None and i_chg < len(rows[0]) and rows[0][i_chg] else None
    result["sectors"][key] = chg
    print(f"[sector {key}] -> {chg}")
    time.sleep(2)

json.dump(result, open("gap_data.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n已保存 gap_data.json")
