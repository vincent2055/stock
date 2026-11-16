# -*- coding: utf-8 -*-
"""妙想选股器：板块排名采集（降级方案，绕过被反爬的东财 clist）"""
import subprocess, csv, os, json, sys, glob, time

SKILL_DIR = r"C:\Users\15899\.workbuddy\skills\mx-stocks-screener"
OUT = os.path.join(SKILL_DIR, "miaoxiang", "mx_stocks_screener")

def run_query(query, select_type="板块"):
    r = subprocess.run([sys.executable, "scripts/get_data.py", "--query", query, "--select-type", select_type],
                       cwd=SKILL_DIR, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    out = r.stdout
    csv_path = None
    for line in out.splitlines():
        if line.startswith("CSV:"):
            csv_path = line.split("CSV:")[1].strip()
            break
    if not csv_path or not os.path.exists(csv_path):
        return None, out.strip()[-150:]
    with open(csv_path, encoding="utf-8-sig", errors="ignore") as f:
        rd = list(csv.reader(f))
    header = rd[0]
    rows = rd[1:]
    return (header, rows), None

def parse_board(header, rows):
    """板块 CSV：返回 [{code,name,today,period}]"""
    # 列名定位
    def col(*keys):
        for i, h in enumerate(header):
            for k in keys:
                if h.startswith(k):
                    return i
        return None
    i_code = col("代码")
    i_name = col("名称")
    i_today = col("涨跌幅")
    i_period = col("区间涨跌幅")
    res = []
    for r in rows:
        if len(r) <= max(x for x in [i_code, i_name, i_today, i_period] if x is not None):
            continue
        name = r[i_name].replace("(申万)", "").replace("Ⅱ", "") if i_name is not None else ""
        res.append({
            "code": r[i_code] if i_code is not None else "",
            "name": name,
            "today": float(r[i_today]) if i_today is not None and r[i_today] else None,
            "period": float(r[i_period]) if i_period is not None and r[i_period] else None,
        })
    return res

def main():
    queries = [
        ("today_top", "申万二级行业板块今天涨幅最大的12个板块"),
        ("today_bottom", "申万二级行业板块今天跌幅最大的12个板块"),
        ("w1", "申万二级行业板块近1周涨幅最大的8个板块"),
        ("m1", "申万二级行业板块近1个月涨幅最大的8个板块"),
        ("m3", "申万二级行业板块近3个月涨幅最大的8个板块"),
        ("m6", "申万二级行业板块近6个月涨幅最大的8个板块"),
    ]
    result = {}
    for key, q in queries:
        (header, rows), err = run_query(q)
        if header is None:
            print(f"[{key}] FAIL: {err}")
            result[key] = []
            continue
        data = parse_board(header, rows)
        result[key] = data
        print(f"[{key}] {q} -> {len(data)} 条")
        for d in data:
            print(f"   {d['name']:14s} today={d['today']} period={d['period']}")
        time.sleep(0.5)
    json.dump(result, open("mx_boards.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n已保存 mx_boards.json")

if __name__ == "__main__":
    main()
