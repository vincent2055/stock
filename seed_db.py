# -*- coding: utf-8 -*-
"""回填 11-16、11-17 两天历史数据到云数据库。生成 SQL 文件供 exec_sql 执行。"""
import json

def s(v):
    if v is None:
        return 'NULL'
    if isinstance(v, bool):
        return 'TRUE' if v else 'FALSE'
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"

def jl(obj):
    """JSON 字面量，用美元引用避免转义，紧凑格式"""
    return "$$" + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + "$$"

# ============ 11-16 数据（final_data.json） ============
d16 = json.load(open("final_data.json", encoding="utf-8"))

# ============ 11-17 数据（硬编码，来自 update_html.py + 数据文件） ============
idx17 = [
    ["上证指数", "000001", "3584.58", -0.50],
    ["深证成指", "399001", "10638.52", -0.49],
    ["创业板指", "399006", "2292.20", -1.20],
    ["科创50", "000688", "1221.19", 0.62],
    ["北证50", "899050", "841.49", 0.59],
]
intl17 = [
    {"market": "美股", "items": [{"name": "道琼斯", "price": "51,608.17", "chg": -1.41}, {"name": "标普500", "price": "7,416.59", "chg": -1.92}, {"name": "纳斯达克", "price": "24,509.76", "chg": -2.49}]},
    {"market": "港股", "items": [{"name": "恒生指数", "price": "23,508.17", "chg": -1.03}, {"name": "恒生科技", "price": "3,758.17", "chg": -1.14}, {"name": "国企指数", "price": "7,904.37", "chg": -0.97}]},
    {"market": "日股", "items": [{"name": "日经225", "price": "58,860.43", "chg": -1.34}]},
    {"market": "韩股", "items": [{"name": "KOSPI", "price": "4,968.48", "chg": -2.59}]},
]
dist17 = [
    {"tag": "涨停", "n": 38, "c": "up"},
    {"tag": "上涨", "n": 1288, "c": "up"},
    {"tag": "平盘", "n": 135, "c": "flat"},
    {"tag": "下跌", "n": 4035, "c": "down"},
    {"tag": "跌停", "n": 84, "c": "down"},
]
zb17 = ["广百股份", "金逸影视", "天虹股份", "综艺股份", "皖通科技", "柏诚股份", "凯撒文化", "百合花", "冰山冷热", "伟测科技",
        "怡达股份", "国风新材", "深华发Ａ", "波长光电", "福晶科技", "高新发展", "国光股份", "意华股份", "北化股份", "仁信新材"]
leaders17 = {
  "w1": [{"name": "白色家电", "v": 4.84, "ld": "长虹美菱", "lc": 17.04}, {"name": "城商行Ⅱ", "v": 4.38, "ld": "齐鲁银行", "lc": 6.36}, {"name": "国有大型银行Ⅱ", "v": 4.13, "ld": "中国银行", "lc": 5.29}, {"name": "小家电", "v": 3.17, "ld": "北鼎股份", "lc": 39.00}, {"name": "渔业", "v": 2.40, "ld": "好当家", "lc": 24.43}, {"name": "农商行Ⅱ", "v": 2.40, "ld": "沪农商行", "lc": 6.83}],
  "m1": [{"name": "小家电", "v": 14.33, "ld": "九阳股份", "lc": 77.18}, {"name": "养殖业", "v": 9.91, "ld": "东瑞股份", "lc": 28.10}, {"name": "酒店餐饮", "v": 9.66, "ld": "首旅酒店", "lc": 21.72}, {"name": "饮料乳品", "v": 8.67, "ld": "新乳业", "lc": 20.55}, {"name": "白酒Ⅱ", "v": 8.37, "ld": "古井贡酒", "lc": 31.10}, {"name": "白色家电", "v": 8.23, "ld": "长虹美菱", "lc": 12.86}],
  "m3": [{"name": "国有大型银行Ⅱ", "v": 21.23, "ld": "交通银行", "lc": 26.52}, {"name": "小家电", "v": 13.83, "ld": "九阳股份", "lc": 239.29}, {"name": "养殖业", "v": 13.36, "ld": "东瑞股份", "lc": 52.10}, {"name": "股份制银行Ⅱ", "v": 12.51, "ld": "中信银行", "lc": 23.41}, {"name": "城商行Ⅱ", "v": 12.45, "ld": "北京银行", "lc": 27.47}, {"name": "数字媒体", "v": 12.19, "ld": "芒果超媒", "lc": 88.46}],
  "m6": [{"name": "国有大型银行Ⅱ", "v": 23.13, "ld": "交通银行", "lc": 34.50}, {"name": "医疗服务", "v": 17.87, "ld": "万邦医药", "lc": 74.54}, {"name": "股份制银行Ⅱ", "v": 13.31, "ld": "浦发银行", "lc": 25.25}, {"name": "城商行Ⅱ", "v": 13.21, "ld": "北京银行", "lc": 29.13}, {"name": "白色家电", "v": 9.86, "ld": "美的集团", "lc": 18.28}, {"name": "养殖业", "v": 7.20, "ld": "东瑞股份", "lc": 42.86}],
}
today17 = [
  {"name": "小家电", "today": 3.94, "w1": 3.17, "m1": 14.33, "m3": 13.83, "m6": -2.90, "ld": "北鼎股份", "lc": 16.05},
  {"name": "贵金属", "today": 2.09, "w1": -10.03, "m1": -11.80, "m3": -21.12, "m6": -18.01, "ld": "山金国际", "lc": 3.40},
  {"name": "电子化学品Ⅱ", "today": 1.93, "w1": -6.30, "m1": -10.43, "m3": -36.02, "m6": -32.47, "ld": "西陇科学", "lc": 10.01},
  {"name": "黑色家电", "today": 1.51, "w1": -1.73, "m1": -5.97, "m3": -12.16, "m6": -28.14, "ld": "海信视像", "lc": 4.86},
  {"name": "酒店餐饮", "today": 1.38, "w1": -0.18, "m1": 9.66, "m3": 2.36, "m6": -8.15, "ld": "首旅酒店", "lc": 3.51},
  {"name": "渔业", "today": 1.14, "w1": 2.40, "m1": 0.80, "m3": -1.40, "m6": -7.03, "ld": "好当家", "lc": 10.00},
  {"name": "白色家电", "today": 1.08, "w1": 4.84, "m1": 8.23, "m3": 8.29, "m6": 9.86, "ld": "长虹美菱", "lc": 9.98},
  {"name": "非白酒", "today": 0.97, "w1": 0.46, "m1": -1.98, "m3": -3.31, "m6": -12.43, "ld": "重庆啤酒", "lc": 3.77},
  {"name": "调味发酵品Ⅱ", "today": 0.94, "w1": 0.58, "m1": 1.92, "m3": -5.34, "m6": -4.94, "ld": "宝立食品", "lc": 6.47},
  {"name": "农化制品", "today": 0.84, "w1": -2.89, "m1": -7.16, "m3": -18.03, "m6": -25.73, "ld": "国光股份", "lc": 9.24},
]
down17 = [
  {"name": "影视院线", "today": -8.59, "w1": -11.52, "m1": -0.48, "m3": 10.44, "m6": -8.74, "ld": "华策影视", "lc": -13.34},
  {"name": "电视广播Ⅱ", "today": -7.01, "w1": -5.73, "m1": -2.44, "m3": -2.86, "m6": -20.97, "ld": "流金科技", "lc": -11.78},
  {"name": "数字媒体", "today": -6.20, "w1": -14.05, "m1": -0.75, "m3": 12.19, "m6": -4.98, "ld": "凡拓数创", "lc": -13.88},
  {"name": "出版", "today": -5.12, "w1": -9.29, "m1": -4.11, "m3": 7.82, "m6": -6.35, "ld": "新华传媒", "lc": -10.00},
  {"name": "广告营销", "today": -4.99, "w1": -8.63, "m1": -1.69, "m3": -9.02, "m6": -23.36, "ld": "元隆雅图", "lc": -10.01},
  {"name": "电机Ⅱ", "today": -4.00, "w1": -11.64, "m1": -6.31, "m3": -21.51, "m6": -38.10, "ld": "华阳智能", "lc": -11.90},
  {"name": "焦炭Ⅱ", "today": -3.13, "w1": -7.86, "m1": -8.98, "m3": -8.95, "m6": -20.61, "ld": "云煤能源", "lc": -8.51},
  {"name": "航天装备Ⅱ", "today": -3.02, "w1": -15.15, "m1": -6.94, "m3": -26.95, "m6": -45.56, "ld": "航天环宇", "lc": -5.96},
  {"name": "自动化设备", "today": -2.98, "w1": -12.47, "m1": -13.04, "m3": -31.40, "m6": -40.63, "ld": "拓斯达", "lc": -12.33},
  {"name": "汽车服务", "today": -2.92, "w1": -3.83, "m1": -0.92, "m3": -2.06, "m6": -15.73, "ld": "阿尔特", "lc": -9.82},
]

# ============ 生成 daily_snapshot INSERT ============
def snapshot_row(d, idx, intl, dist, zb, leaders, today, down, date_label, score, emotion, emotion_desc,
                 zt, dt, zbcnt, fr, up, dn, fl, total, up_ratio, amount):
    cols = ["trade_date","date_label","market_score","emotion","emotion_desc","zt","dt","zb","feng_rate",
            "up_cnt","down_cnt","flat_cnt","total_cnt","up_ratio","amount",
            "index_json","intl_json","dist_json","zb_list_json","leaders_json","today_sectors_json","sector_down_json"]
    vals = [s(d), s(date_label), s(score), s(emotion), s(emotion_desc), s(zt), s(dt), s(zbcnt), s(fr),
            s(up), s(dn), s(fl), s(total), s(up_ratio), s(amount),
            jl(idx), jl(intl), jl(dist), jl(zb), jl(leaders), jl(today), jl(down)]
    return "INSERT INTO daily_snapshot (" + ",".join(cols) + ") VALUES (\n" + ",\n".join(vals) + "\n)"

# 11-16
b16 = d16["breadth"]; p16 = d16["pools"]
sql16 = snapshot_row(
    "2026-11-16", d16["index"], d16["intl"], d16["dist"], d16["zb"], d16["leaders"],
    d16["today_sectors"], d16["sector_down"], d16["date_label"], d16["market_score"],
    "冰点", "跌停潮 · 科技崩盘 · 防御抱团",
    p16["zt"], p16["dt"], p16["zb"], p16["feng_rate"],
    b16["up"], b16["down"], b16["flat"], b16["total"], b16["up_ratio"], d16["amount"],
)
# 11-17
sql17 = snapshot_row(
    "2026-11-17", idx17, intl17, dist17, zb17, leaders17, today17, down17,
    "2026-11-17 周二 收盘快照", 5, "冰点", "跌停潮 · 传媒补跌 · 防御抱团",
    38, 84, 20, 65.5, 1326, 4119, 135, 5580, 23.8, "1.46",
)

# ============ 生成 sector_daily INSERT（hot + down） ============
def sector_rows(date, hot, down):
    rows = []
    for s in hot:
        rows.append((date, s["name"], s["today"], s["w1"], s["m1"], s["m3"], s["m6"], s["ld"], s["lc"], "hot"))
    for s in down:
        rows.append((date, s["name"], s["today"], s["w1"], s["m1"], s["m3"], s["m6"], s["ld"], s["lc"], "down"))
    return rows

all_sector = []
all_sector += sector_rows("2026-11-16", d16["today_sectors"], d16["sector_down"])
all_sector += sector_rows("2026-11-17", today17, down17)

sector_vals = ",\n".join(
    "(" + s(r[0]) + "," + s(r[1]) + "," + s(r[2]) + "," + s(r[3]) + "," + s(r[4]) + "," + s(r[5]) + "," + s(r[6]) + "," + s(r[7]) + "," + s(r[8]) + "," + s(r[9]) + ")"
    for r in all_sector
)
sql_sector = "INSERT INTO sector_daily (trade_date,sector_name,today,w1,m1,m3,m6,leader_stock,leader_chg,kind) VALUES\n" + sector_vals

# ============ 生成 stock_daily INSERT ============
stocks16 = d16["stocks"]
stocks17 = json.load(open("stock_result_1117.json", encoding="utf-8"))

def stock_rows(date, stocks):
    rows = []
    for st in stocks:
        rows.append((
            date, st["code"], st["name"], st.get("etf", False), st["price"], st["chg"],
            st["ma5"], st["ma10"], st["ma20"], st["pos"], st["stop"], st["dist"],
            st["total"], st["grade"], st["sector"], st["sect_chg"], st["vr"], st["dims"],
        ))
    return rows

all_stock = []
all_stock += stock_rows("2026-11-16", stocks16)
all_stock += stock_rows("2026-11-17", stocks17)

stock_vals = ",\n".join(
    "(" + ",".join([s(r[0]), s(r[1]), s(r[2]), s(r[3]), s(r[4]), s(r[5]), s(r[6]), s(r[7]), s(r[8]),
                    s(r[9]), s(r[10]), s(r[11]), s(r[12]), s(r[13]), s(r[14]), s(r[15]), s(r[16]), jl(r[17])]) + ")"
    for r in all_stock
)
sql_stock = "INSERT INTO stock_daily (trade_date,code,name,etf,price,chg,ma5,ma10,ma20,pos,stop,dist,total_score,grade,sector,sect_chg,vr,dims_json) VALUES\n" + stock_vals

open("seed_daily_16.sql", "w", encoding="utf-8").write(sql16)
open("seed_daily_17.sql", "w", encoding="utf-8").write(sql17)
open("seed_sector.sql", "w", encoding="utf-8").write(sql_sector)
open("seed_stock.sql", "w", encoding="utf-8").write(sql_stock)

print("生成完成:")
print("daily_16 长度:", len(sql16))
print("daily_17 长度:", len(sql17))
print("sector 长度:", len(sql_sector), "行数:", len(all_sector))
print("stock 长度:", len(sql_stock), "行数:", len(all_stock))
