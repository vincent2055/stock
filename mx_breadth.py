# -*- coding: utf-8 -*-
"""妙想选股器：涨跌家数 + 涨跌分布 采集（返回行数即计数）"""
import subprocess, os, sys, json

SKILL_DIR = os.path.join(os.path.expanduser("~"), ".workbuddy", "skills", "mx-stocks-screener")

def run_count(query):
    r = subprocess.run([sys.executable, "scripts/get_data.py", "--query", query, "--select-type", "A股"],
                       cwd=SKILL_DIR, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    out = r.stdout
    for line in out.splitlines():
        if line.startswith("行数:"):
            try:
                return int(line.split("行数:")[1].strip())
            except:
                return None
    return None

QUERIES = [
    ("up", "今天上涨的A股"),
    ("down", "今天下跌的A股"),
    ("flat", "今天平盘的A股"),
    ("gt7", "今天涨幅超过7%的A股"),
    ("r5_7", "今天涨幅5%到7%的A股"),
    ("r2_5", "今天涨幅2%到5%的A股"),
    ("r0_2", "今天涨幅大于0且小于2%的A股"),
    ("d0_2", "今天跌幅大于0且小于2%的A股"),
    ("d2_5", "今天跌幅2%到5%的A股"),
    ("d5_7", "今天跌幅5%到7%的A股"),
    ("lt7", "今天跌幅超过7%的A股"),
]

def main():
    result = {}
    for key, q in QUERIES:
        n = run_count(q)
        result[key] = n
        print(f"{key:6s} '{q}' -> {n}")
    json.dump(result, open("breadth_mx.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n已保存 breadth_mx.json")

if __name__ == "__main__":
    main()
