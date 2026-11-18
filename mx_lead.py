# -*- coding: utf-8 -*-
"""妙想选股器：龙头股/领跌股 采集"""
import subprocess, csv, os, json, sys

SKILL_DIR = os.path.join(os.path.expanduser("~"), ".workbuddy", "skills", "mx-stocks-screener")

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

def parse_stock(header, rows, want_period):
    def col(*keys):
        for i, h in enumerate(header):
            for k in keys:
                if h.startswith(k):
                    return i
        return None
    i_code = col("代码"); i_name = col("名称")
    i_chg = col("涨跌幅")
    i_period = col("区间涨跌幅")
    if not rows:
        return None
    r = rows[0]
    chg = None
    if want_period and i_period is not None and i_period < len(r):
        chg = r[i_period]
    elif i_chg is not None and i_chg < len(r):
        chg = r[i_chg]
    return {
        "name": r[i_name] if i_name is not None else "",
        "code": r[i_code] if i_code is not None else "",
        "chg": float(chg) if chg not in (None, "", "-") else None,
    }

# (key, 板块名, 方向, 周期)  方向: up=周期涨幅最大(周期龙头), today_up=当天涨幅最大, today_down=当天跌幅最大
QUERIES = [
    # LEADERS 周期龙头股
    ("w1_0", "厨卫电器", "up", "近1周"),
    ("w1_1", "影视院线", "up", "近1周"),
    ("w1_2", "渔业", "up", "近1周"),
    ("w1_3", "汽车服务", "up", "近1周"),
    ("w1_4", "通信设备", "up", "近1周"),
    ("w1_5", "国有大型银行", "up", "近1周"),
    ("m1_0", "养殖业", "up", "近1个月"),
    ("m1_1", "小家电", "up", "近1个月"),
    ("m1_2", "影视院线", "up", "近1个月"),
    ("m1_3", "数字媒体", "up", "近1个月"),
    ("m1_4", "白酒", "up", "近1个月"),
    ("m1_5", "航天装备", "up", "近1个月"),
    ("m3_0", "数字媒体", "up", "近3个月"),
    ("m3_1", "影视院线", "up", "近3个月"),
    ("m3_2", "国有大型银行", "up", "近3个月"),
    ("m3_3", "出版", "up", "近3个月"),
    ("m3_4", "养殖业", "up", "近3个月"),
    ("m3_5", "小家电", "up", "近3个月"),
    ("m6_0", "国有大型银行", "up", "近6个月"),
    ("m6_1", "医疗服务", "up", "近6个月"),
    ("m6_2", "股份制银行", "up", "近6个月"),
    ("m6_3", "数字媒体", "up", "近6个月"),
    ("m6_4", "城商行", "up", "近6个月"),
    ("m6_5", "农商行", "up", "近6个月"),
    # today_top 当天领涨股
    ("t0", "影视院线", "today_up", ""),
    ("t1", "白色家电", "today_up", ""),
    ("t2", "养殖业", "today_up", ""),
    ("t3", "白酒", "today_up", ""),
    ("t4", "城商行", "today_up", ""),
    ("t5", "饲料", "today_up", ""),
    ("t6", "国有大型银行", "today_up", ""),
    ("t7", "农商行", "today_up", ""),
    ("t8", "煤炭开采", "today_up", ""),
    ("t9", "电视广播", "today_up", ""),
    # today_bottom 当天领跌股
    ("d0", "元件", "today_down", ""),
    ("d1", "通信设备", "today_down", ""),
    ("d2", "玻璃玻纤", "today_down", ""),
    ("d3", "非金属材料", "today_down", ""),
    ("d4", "地面兵装", "today_down", ""),
    ("d5", "其他电子", "today_down", ""),
    ("d6", "塑料", "today_down", ""),
    ("d7", "电子化学品", "today_down", ""),
    ("d8", "通用设备", "today_down", ""),
    ("d9", "房地产服务", "today_down", ""),
]

def build_q(board, direction, period):
    if direction == "up":
        return "%s板块%s涨幅最大的1只股票" % (board, period)
    elif direction == "today_up":
        return "%s板块今天涨幅最大的1只股票" % board
    else:
        return "%s板块今天跌幅最大的1只股票" % board

def main():
    result = {}
    for key, board, direction, period in QUERIES:
        q = build_q(board, direction, period)
        (header, rows), err = run_query(q)
        if header is None:
            print(f"[{key}] {board} {direction} FAIL: {err}")
            result[key] = {"board": board, "dir": direction, "period": period, "ok": False}
            continue
        want_period = (direction == "up")
        s = parse_stock(header, rows, want_period)
        if s is None:
            print(f"[{key}] {board} {direction} 空结果")
            result[key] = {"board": board, "dir": direction, "period": period, "ok": False}
            continue
        result[key] = {"board": board, "dir": direction, "period": period, "ok": True, **s}
        print(f"[{key}] {board:12s} {direction:10s} {period:8s} -> {s['name']} {s['code']} {s['chg']}%")
    json.dump(result, open("lead_stock.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n已保存 lead_stock.json，共", len(result), "条")

if __name__ == "__main__":
    main()
