# -*- coding: utf-8 -*-
"""妙想选股器：龙头/领跌股 补充查询（t8,t9 + d0-d9）"""
import subprocess, csv, os, json, sys

SKILL_DIR = r"C:\Users\15899\.workbuddy\skills\mx-stocks-screener"

def run_query(query, select_type="A股"):
    r = subprocess.run([sys.executable, "scripts/get_data.py", "--query", query, "--select-type", select_type],
                       cwd=SKILL_DIR, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    out = r.stdout
    csv_path = None
    for line in out.splitlines():
        if line.startswith("CSV:"):
            csv_path = line.split("CSV:")[1].strip()
            break
    if not csv_path or not os.path.exists(csv_path):
        return None, out.strip()[-120:]
    with open(csv_path, encoding="utf-8-sig", errors="ignore") as f:
        rd = list(csv.reader(f))
    return (rd[0], rd[1:] if len(rd) > 1 else []), None

def parse_stock(header, rows):
    def col(*keys):
        for i, h in enumerate(header):
            for k in keys:
                if h.startswith(k):
                    return i
        return None
    i_code = col("代码"); i_name = col("名称"); i_chg = col("涨跌幅")
    if not rows:
        return None
    r = rows[0]
    chg = r[i_chg] if i_chg is not None and i_chg < len(r) else None
    return {"name": r[i_name] if i_name is not None else "", "code": r[i_code] if i_code is not None else "",
            "chg": float(chg) if chg not in (None, "", "-") else None}

QUERIES = [
    ("t8", "煤炭开采", "today_up"),
    ("t9", "电视广播", "today_up"),
    ("d0", "元件", "today_down"),
    ("d1", "通信设备", "today_down"),
    ("d2", "玻璃玻纤", "today_down"),
    ("d3", "非金属材料", "today_down"),
    ("d4", "地面兵装", "today_down"),
    ("d5", "其他电子", "today_down"),
    ("d6", "塑料", "today_down"),
    ("d7", "电子化学品", "today_down"),
    ("d8", "通用设备", "today_down"),
    ("d9", "房地产服务", "today_down"),
]

def build_q(board, direction):
    if direction == "today_up":
        return "%s板块今天涨幅最大的1只股票" % board
    return "%s板块今天跌幅最大的1只股票" % board

def main():
    result = {}
    for key, board, direction in QUERIES:
        q = build_q(board, direction)
        r = run_query(q)
        header, rows = r[0], r[1]
        if header is None:
            print(f"[{key}] {board} {direction} FAIL: {rows}")
            result[key] = {"board": board, "dir": direction, "ok": False}
            continue
        s = parse_stock(header, rows)
        if s is None:
            print(f"[{key}] {board} {direction} 空结果")
            result[key] = {"board": board, "dir": direction, "ok": False}
            continue
        result[key] = {"board": board, "dir": direction, "ok": True, **s}
        print(f"[{key}] {board:12s} {direction:10s} -> {s['name']} {s['code']} {s['chg']}%")
    json.dump(result, open("lead_stock2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n已保存 lead_stock2.json，共", len(result), "条")

if __name__ == "__main__":
    main()
